import logging

from django.apps import apps, AppConfig
from django.contrib.admin import site
from django.core.signals import request_started


logger = logging.getLogger(__name__)


def check_apps_need_reloading(sender, environ, **kwargs):
    ContentType = apps.get_model(
        "contenttypes", "ContentType"
    )
    DynamicModel = apps.get_model(
        "django_models_from_csv", "DynamicModel"
    )
    try:
        n_dynmodels = DynamicModel.objects.count()
    except Exception as e:
        # migrations not ran
        logger.error("Not checking for data sources due to error: %s" % (
            e
        ))
        return

    conf = apps.get_app_config("django_models_from_csv")
    n_registered = len(list(conf.get_models()))

    logger.debug("Checking apps n_dynmodels=%s n_registered=%s" % (
        n_dynmodels, n_registered
    ))

    # subtract one for DynamicModel, which won't be in
    # the DynamicModels count()
    if n_dynmodels != (n_registered - 1):
        logger.debug("Re-registering django apps models...")
        DynamicModel.objects.last().model_cleanup()

    # figure out how many of our admins are registered
    n_admins = 0
    for model, admin in site._registry.items():
        if model._meta.app_label != "django_models_from_csv":
            continue
        if model._meta.object_name == "DynamicModel":
            continue
        n_admins += 1

    logger.debug("Checking admins n_dynmodels=%s n_admins=%s" % (
        n_dynmodels, n_admins
    ))

    if n_dynmodels != n_admins:
        logger.debug("Re-registering django admins...")
        # re-register apps. the goal here is to get the AdminSite's
        # internal _registry to be updated with the new app.
        from collaborative.admin import AdminMetaAutoRegistration
        AdminMetaAutoRegistration(
            include="django_models_from_csv.models"
        ).register()


class DjangoDynamicModelsConfig(AppConfig):
    name = 'django_models_from_csv'
    app_label = 'django_models_from_csv'
    verbose_name = "Data Sources"

    def ready(self):
        request_started.connect(check_apps_need_reloading)
