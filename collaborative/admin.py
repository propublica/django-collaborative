import logging
import re

from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.admin.views.main import ChangeList
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, FieldDoesNotExist
from django.db import connection
from django.db.models.functions import Lower
from django.db.utils import OperationalError
from django.forms import modelform_factory
from django.utils.html import mark_safe, format_html
from django.views.decorators.cache import never_cache
from import_export.admin import ExportMixin
from social_django.models import Association, Nonce, UserSocialAuth
from taggit.models import Tag
from taggit.apps import TaggitAppConfig

from collaborative.export import collaborative_modelresource_factory
from collaborative.filters import TagListFilter
from django_models_from_csv.admin import AdminAutoRegistration, NoEditMixin
from django_models_from_csv.forms import create_taggable_form
from django_models_from_csv.models import DynamicModel, CredentialStore


logger = logging.getLogger(__name__)


class NewUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    add_form_template = 'admin/auth/user/add_form.html'

    def add_view(self, request, *args, **kwargs):
        if request.method != "POST":
            return super().add_view(request, *args, **kwargs)
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if not password1 and not password2:
            newpass = User.objects.make_random_password(length=32)
            request.POST._mutable = True
            request.POST["password1"] = newpass
            request.POST["password2"] = newpass
            request.POST._mutable = False
        return super().add_view(request, *args, **kwargs)


def widget_for_object_field(obj, field_name):
    FieldForm = modelform_factory(
        obj.source_dynmodel().get_model(),
        fields=(field_name,)
    )
    widget = FieldForm().fields[field_name].widget
    return widget


def make_getter(rel_name, attr_name, getter_name, field=None):
    """
    Build a reverse lookup getter, to be attached to the custom
    dynamic lookup admin class.
    """
    def getter(self):
        if not hasattr(self, rel_name):
            return None

        rel = getattr(self, rel_name).first()
        if not rel:
            return None
        fieldname = "%s__%s" % (rel_name, attr_name)
        content_type_id = ContentType.objects.get_for_model(self).id

        # handle tagging separately
        if attr_name == "tags":
            all_tags = rel.tags.all()
            tags_html = []
            for t in all_tags:
                name = t.name
                html = (
                    "<span class='tag-bubble'>"
                    "<span class='remtag'>x</span>"
                    "%s</span>"
                ) % (name)
                tags_html.append(html)
            return mark_safe(format_html(
                "".join(tags_html)
            ))

        # try to lookup choices for field
        choices = getattr(
            rel, "%s_CHOICES" % attr_name.upper(), []
        )
        value = getattr(rel, attr_name)
        for pk, txt in choices:
            if pk == value:
                widget = widget_for_object_field(rel, attr_name)
                html = widget.render(fieldname, value)
                return mark_safe(format_html(
                    "<span content_type_id='{}' class='inline-editable'>{}</span>",
                    content_type_id,
                    html,
               ))

        # no choice found, return field value
        widget = widget_for_object_field(rel, attr_name)
        html = widget.render(fieldname, value)
        return mark_safe(format_html(
            "<span content_type_id='{}' class='inline-editable'>{}</span>",
            content_type_id,
            html,
        ))

    # the header in django admin is named after the function name. if
    # this line is removed, the header will be "GETTER" for all derived
    # reverse lookup columns
    getter.__name__ = getter_name
    return getter


class ReimportMixin(ExportMixin):
    """
    Mixin for displaying re-import button on admin list view, alongside the
    export button (from import_export module).
    """
    change_list_template = 'django_models_from_csv/change_list_dynmodel.html'


class CaseInsensitiveChangeList(ChangeList):
    """
    Provides case-insensitive ordering for admin list view.
    """
    def get_ordering(self, request, queryset):
        ordering = super().get_ordering(request, queryset)
        for i in range(len(ordering)):
            desc = False
            fieldname = ordering[i]
            if fieldname.startswith("-"):
                fieldname = fieldname[1:]
                desc = True

            try:
                field = queryset.model()._meta.get_field(
                    "id" if fieldname == "pk" else fieldname
                )
            except FieldDoesNotExist:
                continue

            f_type = field.db_type(connection)
            if f_type != "text":
                continue

            if desc:
                ordering[i] = Lower(fieldname).desc()
            else:
                ordering[i] = Lower(fieldname)
        return ordering


class ReverseFKAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        """
        Build relations lookup methods, like metadata__status, but
        for the reverse foreignkey direction.
        """
        super().__init__(*args, **kwargs)
        Model, site = args
        if "DynamicModel" == Model._meta.object_name:
            return
        # setup reverse related attr getters so we can do things like
        # metadata__status in the reverse direction
        for rel in Model._meta.related_objects:
            rel_name = rel.get_accessor_name() # "metadata", etc, related_name
            rel_model = rel.related_model
            if not rel_model:
                logger.warning("No related model found!")
                continue

            for rel_field in rel_model._meta.get_fields():
                # build a getter for this relation attribute
                attr_name = rel_field.name

                # remove auto fields and other fields of that nature. we
                # only want the directly acessible fields of this method
                if attr_name != "tags":
                    if rel_field.is_relation: continue
                    if not hasattr(rel_field, "auto_created"): continue
                    if rel_field.auto_created: continue


                getter_name = "%s_%s" % (rel_name, attr_name)
                short_desc = re.sub(r"[\-_]+", " ", attr_name).replace(
                    "assignee", "assigned to"
                )

                getter = make_getter(
                    rel_name, attr_name, getter_name, field=rel_field
                )
                setattr(self, getter_name, getter)
                getattr(self, getter_name).short_description = short_desc
                getattr(
                    self, getter_name
                ).admin_order_field = "%s__%s" % (rel_name, attr_name)

    def get_view_label(self, obj):
        return "View"

    get_view_label.short_description = 'Records'

    def get_changelist(self, request, **kwargs):
        # This controls how the admin list view works. Override the
        # ChangeList to modify ordering, template, etc
        return CaseInsensitiveChangeList


class DynamicModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return DynamicModel.objects.exclude(name__icontains="metadata")

    def get_full_deletion_set(self, queryset, only_meta=False):
        """
        This is called when a user selects some dynamic models to be
        deleted. Since the admin queryset only displays the main models,
        not the metadata models, each item in the queryset can be
        assumed to be a primary data source model. Here, we want to
        also add the corresponding meta models.
        """
        pks = []
        for model in queryset:
            name = model.name
            meta = "%smetadata" % (name)
            contact_meta = "%scontactmetadata" % (name)

            names = (meta, contact_meta)
            if not only_meta:
                names = (name, meta, contact_meta)

            for dynmodel in DynamicModel.objects.filter(name__in=names):
                pks.append(dynmodel.pk)

        # order this by descending id, since the original model gets
        # created first, and we need to delete the reverse fk attached
        # models first to avoid a cascade
        return DynamicModel.objects.filter(
            pk__in=pks
        ).order_by("-id")

    def get_deleted_objects(self, queryset, request):
        extended_queryset = self.get_full_deletion_set(queryset)
        return super().get_deleted_objects(extended_queryset, request)

    def delete_queryset(self, request, queryset):
        # for model in queryset:
        # for model in self.get_full_deletion_set(queryset):
        for model in queryset:
            Model = model.get_model()
            model_qs = DynamicModel.objects.filter(pk=model.pk)
            # wipe all relations, by truncating table
            for related in self.get_full_deletion_set(model_qs, only_meta=True):
                RelatedModel = related.get_model()
                for obj in RelatedModel.objects.all():
                    obj.delete()
            model.delete()
        # NOTE: we have to delete these *after* we wipe the original.
        # otherwise django throws all kinds of errors or will gracefuly
        # succeed but throw errors later during normal admin operation
        for metamodel in self.get_full_deletion_set(model_qs, only_meta=True):
            metamodel.delete()


class AdminMetaAutoRegistration(AdminAutoRegistration):
    def should_register_admin(self, Model):
        # metadata models get admin created along with the base model
        name = Model._meta.object_name
        if name.endswith("metadata"):
            return False
        return super().should_register_admin(Model)

    def create_dynmodel_admin(self, Model):
        name = Model._meta.object_name
        inheritance = (NoEditMixin, DynamicModelAdmin,)
        return type("%sAdmin" % name, inheritance, {})

    def create_admin(self, Model):
        name = Model._meta.object_name
        if "metadata" in name:
            return
        if name == "DynamicModel":
            return self.create_dynmodel_admin(Model)

        meta = []
        # find the Metadata model corresponding to the
        # csv-backed model we're creating admin for.
        # this will end up as an inline admin
        for MetaModel in apps.get_models():
            meta_name = MetaModel._meta.object_name
            # all our additonal related models are in this pattern:
            # [model-name][contact|]metadata
            if not meta_name.startswith(name) or \
               not meta_name.endswith("metadata"):
                continue
            dynmodel_meta = MetaModel.source_dynmodel(MetaModel)
            # for contact log, always show a blank one for easy access
            extra = 0
            if meta_name.endswith("contactmetadata"):
                extra = 1
            meta_attrs = {
                "model": MetaModel,
                "extra": extra,
            }
            if not meta_name.endswith("contactmetadata"):
                fields_meta = self.get_fields(MetaModel, dynmodel=dynmodel_meta)
                try:
                    form_meta = create_taggable_form(MetaModel, fields=fields_meta)
                    meta_attrs["form"] = form_meta
                # no tags on this model
                except FieldError:
                    pass
            MetaModelInline = type(
                "%sInlineAdmin" % meta_name,
                (admin.StackedInline,), meta_attrs)
            meta.append(MetaModelInline)

        # get searchable and filterable (from column attributes)
        # should we order by something? number of results?
        try:
            model_desc = DynamicModel.objects.get(name=name)
        except OperationalError:
            return None
        except DynamicModel.DoesNotExist:
            logger.warning("Model with name: %s doesn't exist. Skipping" % name)
            # return super().create_admin(Model)
            return None

        cols = list(reversed(model_desc.columns))
        searchable = [c.get("name") for c in cols if c.get("searchable")]
        filterable = [c.get("name") for c in cols if c.get("filterable")]

        # Build our CSV-backed admin, attaching inline meta model
        dynmodel = Model.source_dynmodel(Model)
        fields = self.get_fields(Model, dynmodel=dynmodel)
        associated_fields = ["get_view_label"]
        if name != "DynamicModel":
            test_item = Model.objects.first()
            if test_item and hasattr(test_item, "metadata"):
                associated_fields.append("metadata_status")
                filterable.append("metadata__status")
                test_metadata = test_item.metadata.first()
                if hasattr(test_metadata, "assigned_to"):
                    associated_fields.append("metadata_assigned_to")
                    filterable.append("metadata__assigned_to")
                elif hasattr(test_metadata, "assignee"):
                    associated_fields.append("metadata_assignee")
                    filterable.append("metadata__assignee")
                if test_metadata and hasattr(test_metadata, "tags"):
                    associated_fields.append("metadata_tags")
                    filterable.append(TagListFilter)
        list_display = associated_fields + fields[:5]

        exporter = collaborative_modelresource_factory(
            model=Model,
        )

        # Note that ExportMixin needs to be declared before ReverseFKAdmin
        inheritance = (NoEditMixin, ReimportMixin, ReverseFKAdmin,)
        return type("%sAdmin" % name, inheritance, {
            "inlines": meta,
            "readonly_fields": fields,
            "list_display": list_display,
            "search_fields": searchable,
            "list_filter": filterable,
            "resource_class": exporter,
        })


# Hide "taggit" name
TaggitAppConfig.verbose_name = "Tagging"

# Remove tagged item inline
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    ordering = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}

    class Meta:
        verbose_name = "Tags"
        verbose_name_plural = "Tags"
        app_label = "Tags"


@never_cache
def login(*args, **kwargs):
    """
    Override login view to hide Google Sign In button if no
    OAuth credentials added.
    """
    extra_context = kwargs.get("extra_context", {})
    have_oauth_creds = CredentialStore.objects.filter(
        name="google_oauth_credentials"
    ).count()
    extra_context["google_oauth_credentials"] = have_oauth_creds > 0
    if "first_login" in extra_context:
        extra_context["first_login"] = False
    kwargs["extra_context"] = extra_context
    return AdminSite().login(*args, **kwargs)


admin.site.login = login
admin.site.site_header = "Collaborate"
admin.site.index_title = "Welcome"
admin.site.site_title = "Collaborate"
# Remove the "view site" link from the admin header
admin.site.site_url = None

# unregister django social auth from admin
admin.site.unregister(Association)
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(User)
admin.site.unregister(Tag)

admin.site.register(Tag, TagAdmin)
admin.site.register(LogEntry)
admin.site.register(User, NewUserAdmin)

def register_dynamic_admins(*args, **kwargs):
    AdminMetaAutoRegistration(include="django_models_from_csv.models").register()

# Register the ones that exist ...
register_dynamic_admins()

# ... and register new ones that get created. Otherwise, we'd
# have to actually restart the Django process post-model create
if register_dynamic_admins not in DynamicModel._POST_SAVE_SIGNALS:
    DynamicModel._POST_SAVE_SIGNALS.append(register_dynamic_admins)
