import logging
import re

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.apps import apps
from import_export.admin import ExportMixin
from import_export.resources import modelresource_factory

import social_django.models as social_models
from social_django.models import Association, Nonce, UserSocialAuth

from collaborative.models import AppSetting
from django_models_from_csv.admin import AdminAutoRegistration, NoEditMixin
from django_models_from_csv.models import DynamicModel


UserAdmin.list_display = ("username","email","first_name","last_name")
# UserAdmin.list_editable = ("first_name", "last_name")

UserAdmin.add_fieldsets = ((None, {
    'fields': ('username', 'email', 'password1', 'password2'),
    'classes': ('wide',)
}),)


logger = logging.getLogger(__name__)


def make_getter(rel_name, attr_name, getter_name):
    """
    Build a reverse lookup getter, to be attached to the custom
    dynamic lookup admin class.
    """
    def getter(self):
        if hasattr(self, rel_name):
            rel = getattr(self, rel_name).first()
            # try to lookup choices for field
            choices = getattr(
                rel, "%s_CHOICES" % attr_name.upper(), []
            )
            value = getattr(rel, attr_name)
            for pk, txt in choices:
                if pk == value:
                    return txt
            # no choice found, return field value
            return value
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
    change_list_template = 'django_models_from_csv/change_list_reimport.html'


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
                continue

            for rel_field in rel_model._meta.get_fields():
                # remove auto fields and other fields of that nature. we
                # only want the directly acessible fields of this method
                if rel_field.is_relation: continue
                if not hasattr(rel_field, "auto_created"): continue
                if rel_field.auto_created: continue

                # build a getter for this relation attribute
                attr_name = rel_field.name
                getter_name = "%s_%s" % (rel_name, attr_name)
                getter = make_getter(rel_name, attr_name, getter_name)
                setattr(Model, getter_name, getter)
                short_desc = re.sub(r"[\-_]+", " ", attr_name)
                getattr(Model, getter_name).short_description = short_desc
                getattr(Model, getter_name).admin_order_field = "%s__%s" % (
                    rel_name, attr_name
                )

    def get_view_label(self, obj):
        return "View"

    get_view_label.short_description = 'Records'


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
        )#.order_by("-id")

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
        name = Model._meta.object_name
        if name.endswith("metadata"):
            return False
        return super(
            AdminMetaAutoRegistration, self
        ).should_register_admin(Model)

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
            # [model-name][contact|*]metadata
            if not meta_name.startswith(name) or \
               not meta_name.endswith("metadata"):
                continue
            MetaModelInline = type(
                "%sInlineAdmin" % meta_name,
                (admin.StackedInline,), {
                    "model": MetaModel,
                    "extra": 0,
                })
            meta.append(MetaModelInline)

        # get searchable and filterable (from column attributes)
        # TODO: order by something? number of results?
        try:
            model_desc = DynamicModel.objects.get(name=name)
        except DynamicModel.DoesNotExist:
            logger.warning("Model with name: %s doesn't exist. Skipping" % name)
            return super().create_admin(Model)

        cols = list(reversed(model_desc.columns))
        searchable = [c.get("name") for c in cols if c.get("searchable")]
        filterable = [c.get("name") for c in cols if c.get("filterable")]

        # Build our CSV-backed admin, attaching inline meta model
        ro_fields = self.get_readonly_fields(Model)
        fields = self.get_fields(Model)
        associated_fields = ["get_view_label"]
        if name != "DynamicModel":
            associated_fields.append("metadata_status")
            associated_fields.append("metadata_partner")
        list_display = associated_fields + fields[:5]

        # Note that ExportMixin needs to be declared before ReverseFKAdmin
        inheritance = (NoEditMixin, ReimportMixin, ReverseFKAdmin,)
        return type("%sAdmin" % name, inheritance, {
            "inlines": meta,
            "readonly_fields": fields,
            "list_display": list_display,
            "search_fields": searchable,
            "list_filter": filterable,
            "resource_class": modelresource_factory(model=Model)(),
        })


admin.site.register(LogEntry)
admin.site.register(AppSetting)

admin.site.site_header = "Collaborate"
admin.site.index_title = "Welcome"
admin.site.site_title = "Collaborate"

# unregister django social auth from admin
admin.site.unregister(Association)
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)

def register_dynamic_admins(*args, **kwargs):
    AdminMetaAutoRegistration(include="django_models_from_csv.models").register()

# Register the ones that exist ...
register_dynamic_admins()

# ... and register new ones that get created. Otherwise, we'd
# have to actually restart the Django process post-model create
if register_dynamic_admins not in DynamicModel._POST_SAVE_SIGNALS:
    DynamicModel._POST_SAVE_SIGNALS.append(register_dynamic_admins)
