import logging
from django.contrib.contenttypes.management import (
    create_contenttypes
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.management import (
    create_permissions
)
from django.core.exceptions import AppRegistryNotReady
from django.db.utils import OperationalError


logger = logging.getLogger(__name__)


def get_permission_models():
    Permission = ContentType.objects.get(
        app_label="auth", model="permission"
    ).model_class()
    Group = ContentType.objects.get(
        app_label="auth", model="group"
    ).model_class()
    return Permission, Group


def build_tag_permission_group():
    Permission, Group = get_permission_models()

    tag_cts = ContentType.objects.filter(app_label="taggit")
    tag_perm_group, created = Group.objects.get_or_create(
        name="tagging"
    )
    tag_perms = list(Permission.objects.filter(content_type__in=tag_cts))
    tag_perm_group.permissions.add(*tag_perms)
    tag_perm_group.save()
    return tag_perm_group


def build_permission_groups(app_label):
    # get just the base models, we'll use this to build the
    # base groups
    DynamicModel = ContentType.objects.get(
        app_label=app_label, model="dynamicmodel"
    ).model_class()
    Permission, Group = get_permission_models()

    dynmodels = DynamicModel.objects.exclude(name__endswith="metadata")
    for dynmodel in dynmodels:
        name = dynmodel.name
        meta_name = "%smetadata" % (name)
        contact_meta_name = "%scontactmetadata" % (name)

        try:
            content_type = ContentType.objects.get(
                app_label=app_label,
                model=name,
            )
            content_type_meta = ContentType.objects.get(
                app_label=app_label,
                model=meta_name,
            )
            content_type_contactmeta = ContentType.objects.get(
                app_label=app_label,
                model=contact_meta_name,
            )
        except ContentType.DoesNotExist:
            return

        # create the permission group for this source. it simply bears the
        # name of the source and grants all perms
        perm_group, created = Group.objects.get_or_create(
            name=dynmodel.name
        )
        perms = list(Permission.objects.filter(content_type__in=[
            content_type, content_type_meta, content_type_contactmeta
        ]))
        perm_group.permissions.add(*perms)
        perm_group.save()


def hydrate_models_and_permissions(app_config):
    """
    Setup content types, base permissions and data source
    specific permission groups for use in the admin.
    """
    try:
        create_contenttypes(app_config, interactive=False, verbosity=4)
    except OperationalError as e:
        logger.error("Error creating content-types: %s" % e)

    try:
        create_permissions(app_config, interactive=False, verbosity=4)
    except OperationalError as e:
        logger.error("Error creating permissions: %s" % e)

    try:
        build_permission_groups(app_config.name)
    except (OperationalError, AppRegistryNotReady) as e:
        logger.error("Error creating permission groups: %s" % e)

    try:
        build_tag_permission_group()
    except (OperationalError, AppRegistryNotReady) as e:
        logger.error("Error creating tagging perm group: %s" % e)


def wipe_models_and_permissions(app_config, name):
    """
    Completely wipe a single model. Unlike the above functions, this
    does not also remove the meta models attached.
    """
    Permission, Group = get_permission_models()
    app_label = app_config.name

    content_type = ContentType.objects.filter(
        app_label=app_label,
        model=name,
    ).first()

    Group.objects.filter(
        name=name
    ).delete()
    Permission.objects.filter(
        content_type=content_type
    ).delete()

    ContentType.objects.filter(
        app_label=app_label,
        model=name,
    ).delete()
