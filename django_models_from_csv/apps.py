from django.apps import apps, AppConfig
from django.core.signals import request_started


def check_apps_need_reloading(sender, environ, **kwargs):
    ContentType = apps.get_model(
        "contenttypes", "ContentType"
    )
    DynamicModel = apps.get_model(
        "django_models_from_csv", "DynamicModel"
    )
    n_dynmodels = DynamicModel.objects.count()

    conf = apps.get_app_config("django_models_from_csv")
    n_registered = len(list(conf.get_models()))

    # subtract one for DynamicModel, which won't be in
    # the DynamicModels count()
    if n_dynmodels != (n_registered - 1):
        DynamicModel.objects.last().model_cleanup()
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
