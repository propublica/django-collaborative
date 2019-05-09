from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from django.apps import apps
from import_export.resources import modelresource_factory

from django_models_from_csv.admin import AdminAutoRegistration


UserAdmin.list_display = ("username","email","first_name","last_name")
# UserAdmin.list_editable = ("first_name", "last_name")

UserAdmin.add_fieldsets = ((None, {
    'fields': ('username', 'email', 'password1', 'password2'),
    'classes': ('wide',)
}),)


class AdminMetaAutoRegistration(AdminAutoRegistration):
    def should_register_admin(self, Model):
        name = Model._meta.object_name
        if name.endswith("Metadata"):
            return False
        return super(
            AdminMetaAutoRegistration, self
        ).should_register_admin(Model)

    def create_admin(self, Model):
        name = Model._meta.object_name
        meta = []
        # find the Metadata model corresponding to the
        # csv-backed model we're creating admin for.
        # this will end up as an inline admin
        for MetaModel in self.all_models:
            meta_name = MetaModel._meta.object_name
            # all our additonal related models are in this pattern:
            # [ModelName][Contact|*]Metadata
            if not meta_name.startswith(name) or \
               not meta_name.endswith("Metadata"):
                continue
            MetaModelInline = type(
                "%sInlineAdmin" % meta_name,
                (admin.StackedInline,), {
                    "model": MetaModel,
                    "extra": 0,
                })
            meta.append(MetaModelInline)

        # Build our CSV-backed admin, attaching inline meta model
        fields = self.get_fields(Model)
        return type("%sAdmin" % name, (admin.ModelAdmin,), {
            "inlines": meta,
            "readonly_fields": fields,
        })


AdminMetaAutoRegistration(include="django_models_from_csv.models").register()
admin.site.register(LogEntry)

admin.site.site_header = "ProPublica's Instant Database"
admin.site.index_title = "Welcome"
admin.site.site_title = "ProPublica's Instant Database"

