import logging

from django.apps import apps
from django.contrib import admin
from import_export.resources import modelresource_factory


logger = logging.getLogger(__name__)


# Auto-register Admins for all dymamic models. This avoids needing to
# write code and inject it into an admin.py for our auto-generated
# models
models = apps.get_models()
for Model in models:
    model_str = str(Model)
    if "django_models_from_csv.models" not in model_str:
        continue
    fields = [ f.name for f in Model._meta.get_fields()]
    ModelAdmin = type("%sAdmin" % model_str, (admin.ModelAdmin,), {
        "readonly_fields": fields
    })
    try:
        admin.site.register(Model, ModelAdmin)
    except admin.sites.AlreadyRegistered:
        logger.warn("WARNING! Not registering model: %s. Already exists." % (
            model_str
        ))
        continue

    # set up a django-import-export class for this model
    modelresource_factory(Model)
