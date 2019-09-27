import logging
import time

from django.apps import apps, AppConfig
from django.contrib.admin import site
from django.conf import settings
from django.core.signals import request_started


logger = logging.getLogger(__name__)


def check_apps_need_reloading(sender, environ, **kwargs):
    # don't run this on static asset request. since we're using
    # whitenoise, this will happen (all assets go through as a
    # django request, triggering this signal)
    request = sender.request_class(environ)
    path = request.path
    static_url = getattr(settings, "STATIC_URL", "/static/")
    if path.startswith(static_url):
        return

    start = time.time()
    ContentType = apps.get_model(
        "contenttypes", "ContentType"
    )
    DynamicModel = apps.get_model(
        "django_models_from_csv", "DynamicModel"
    )
    try:
        n_dynmodels = DynamicModel.objects.values("id").count()
    except Exception as e:
        # migrations not ran
        logger.error("Not checking for data sources due to error: %s" % (
            e
        ))
        return

    conf = apps.get_app_config("django_models_from_csv")
    registered_models = list(conf.get_models())
    n_registered = len(registered_models)

    # subtract one for DynamicModel, one for CredentialStore which won't
    # be in the DynamicModels count()
    if n_dynmodels != (n_registered - 2):
        last_model = DynamicModel.objects.last()
        if last_model:
            last_model.model_cleanup()

    # figure out how many of our admins are registered
    n_admins = 0
    for model, admin in site._registry.items():
        if model._meta.app_label != "django_models_from_csv":
            continue
        if model._meta.object_name == "DynamicModel":
            continue
        n_admins += 1

    # since each data source has three models (source data, meta and
    # contact), but we only build admins for the main data source
    # model. so we divide by three because we only want to count base
    # model admins and it's quicker to do a divide than to re-query,
    # filtering by name
    if True: # or (n_dynmodels / 3) > n_admins:
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
