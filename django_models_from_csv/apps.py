from django.apps import AppConfig

from django.contrib.contenttypes.management import (
    create_contenttypes
)
from django.contrib.auth.management import (
    create_permissions
)
from django.core.exceptions import AppRegistryNotReady
from django.db.utils import OperationalError


def build_permission_groups(app_label):
    from django.contrib.contenttypes.models import ContentType
    # get just the base models, we'll use this to build the
    # base groups
    DynamicModel = ContentType.objects.get(
        app_label=app_label, model="dynamicmodel"
    ).model_class()
    Permission = ContentType.objects.get(
        app_label="auth", model="permission"
    ).model_class()
    Group = ContentType.objects.get(
        app_label="auth", model="group"
    ).model_class()

    dynmodels = DynamicModel.objects.exclude(name__endswith="metadata")
    for dynmodel in dynmodels:
        Model = dynmodel.get_model()
        content_type = ContentType.objects.get_for_model(Model)
        perm_group, created = Group.objects.get_or_create(
            name=dynmodel.name
        )
        perms = list(Permission.objects.filter(content_type=content_type))
        perm_group.permissions.add(*perms)
        perm_group.save()


def hydrate_django_models_in_db(app_config):
    """
    Setup content types, base permissions and data source
    specific permission groups for use in the admin.
    """
    try:
        create_contenttypes(app_config)
    except OperationalError as e:
        logger.error("Error creating content-types: %s" % e)

    try:
        create_permissions(app_config)
    except OperationalError as e:
        logger.error("Error creating permissions: %s" % e)

    try:
        build_permission_groups(app_config.name)
    except (OperationalError, AppRegistryNotReady) as e:
        logger.error("Error creating permission groupss: %s" % e)


class DjangoDynamicModelsConfig(AppConfig):
    name = 'django_models_from_csv'
    verbose_name = "Data Sources"
