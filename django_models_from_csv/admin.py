import logging

from django.apps import apps
from django.contrib import admin
from import_export.resources import modelresource_factory


logger = logging.getLogger(__name__)


# Auto-register Admins for all dymamic models. This avoids needing to
# write code and inject it into an admin.py for our auto-generated
# models
models = apps.get_models()
for model in models:
    model_str = str(model)
    if "django_models_from_csv.models" not in model_str:
        continue
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        logger.warn("WARNING! Not registering model: %s. Already exists." % (
            model_str
        ))
        continue

    # set up a django-import-export class for this model
    modelresource_factory(model)
