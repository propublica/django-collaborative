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
            if meta_name != "%sMetadata" % name:
                continue
            MetaModelInline = type(
                "%sInlineAdmin" % meta_name,
                (admin.StackedInline,), {
                    "model": MetaModel,
                    "extra": 0,
                })

            meta.append(MetaModelInline)
            break

        # Build our CSV-backed admin, attaching inline meta model
        ro_fields = self.get_readonly_fields(Model)
        fields = self.get_fields(Model)
        return type("%sAdmin" % name, (admin.ModelAdmin,), {
            "inlines": meta,
        })


AdminMetaAutoRegistration(include="django_models_from_csv.models").register()
admin.site.register(LogEntry)

