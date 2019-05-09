import logging

from django.apps import apps
from django.contrib import admin
from import_export.resources import modelresource_factory

from django_models_from_csv.utils.common import get_setting


logger = logging.getLogger(__name__)


class AdminAutoRegistration:
    """
    Automatically register dynamic models. Models with a full name
    that matches the specified `include` string will be registered.

    By default, `include` is set to "django_models_from_csv.models"
    """
    def __init__(self, include="django_models_from_csv.models"):
        self.include = include
        self.all_models = apps.get_models()

    def attempt_register(self, Model, ModelAdmin):
        try:
            admin.site.register(Model, ModelAdmin)
        except admin.sites.AlreadyRegistered:
            logger.warn("WARNING! Not registering model: %s. Already exists." % (
                str(Model)
            ))

    def get_readonly_fields(self, Model):
        # return [ f.name for f in Model._meta.get_fields()]
        return []

    def get_fields(self, Model):
        return [ f.name for f in Model._meta.get_fields()]

    def create_admin(self, Model):
        name = Model._meta.object_name
        ro_fields = self.get_readonly_fields(Model)
        fields = self.get_fields(Model)
        return type("%sAdmin" % name, (admin.ModelAdmin,), {
            # "fields": fields,
            # "readonly_fields": ro_fields,
        })

    def should_register_admin(self, Model):
        return self.include in str(Model)

    def register(self):
        for Model in self.all_models:
            if not self.should_register_admin(Model):
                continue

            ModelAdmin = self.create_admin(Model)
            self.attempt_register(Model, ModelAdmin)


if get_setting("CSV_MODELS_AUTO_REGISTER_ADMIN", True):
    # Auto-register Admins for all dymamic models. This avoids needing to
    # write code and inject it into an admin.py for our auto-generated
    # models
    auto_reg = AdminAutoRegistration(include="django_models_from_csv.models")
    auto_reg.register()
