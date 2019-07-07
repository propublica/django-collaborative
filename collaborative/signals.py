from copy import copy
import logging

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.db.utils import OperationalError
from django.dispatch import receiver

from collaborative.models import (
    get_metamodel_name, MODEL_TYPES, DEFAULT_META_COLUMNS,
    default_contact_model_columns
)
from collaborative.user import set_staff_status
from django_models_from_csv import models


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def ensure_staff(sender, **kwargs):
    """
    Give users staff status (so they can see the Admin) if
    they are able to log in.
    """
    user = kwargs.get("instance")
    if user and not user.is_staff:
        set_staff_status(user)


def tag_csv_dynmodel(dynmodel):
    # skip already tagged or no instance
    if not dynmodel or dynmodel.get_attr("type"):
        return
    # check for CSV record type, tag and return if found
    for col in dynmodel.columns:
        if col.get("original_name") is not None:
            dynmodel.attrs["type"] = MODEL_TYPES.CSV
            dynmodel.save()
            return


# TODO: do this on Model.__new__
# @receiver(pre_save, sender=models.DynamicModel)
# def build_and_link_metadata_fk(sender, **kwargs):
def build_and_link_metadata_fk(dynmodel):
    """
    This signal listens for the creation of a new dynamically-generated
    CSV-backed model. When it finds one, it will automatically create a
    corresponding Metadata model (if it doesn't already exist) with the
    proper defaults and also add a foreign key relationship pointing
    to the CSV-backed model.

    This allows us to inline metadata models inside the CSV-backed model
    admin detail page, without messing with the CSV-backed records at all.
    (Since the FK is on the metadata side.)
    """
    if not dynmodel:
        return

    tag_csv_dynmodel(dynmodel)

    mtype = dynmodel.get_attr("type")
    if mtype == MODEL_TYPES.CSV:
        # 1. look for dynmodel's corresponding meta model
        Model = dynmodel.get_model()
        metamodel_name = "%sMetadata" % dynmodel.name

        dyn_metamodel_count = models.DynamicModel.objects.filter(
            name=metamodel_name
        ).count()

        # 2. a) Does exist: return
        if dyn_metamodel_count > 0:
            return

        # 2. b) Doesn't exist: create meta model for this dynmodel.
        columns = copy(DEFAULT_META_COLUMNS)
        columns.append({
            "name": "metadata",
            "type": "foreignkey",
            "args": [dynmodel.fullname, "SET_NULL"],
            "attrs": {
                "blank": True,
                "null": True,
                "related_name": "metadata"
            },
        })

        dyn_metamodel = models.DynamicModel.objects.create(
            name = metamodel_name,
            attrs = {
                "type": MODEL_TYPES.META,
            },
            columns = columns,
        )
        dyn_metamodel.save()

        # 2. c) Create contact meta model for this dynmodel
        # NOTE: since we always create metadata model along
        # with contact model, we know that contact model
        # hasn't been created if metadata doesn't already
        # exist (so no additional check)
        contact_model_name = "%sContactMetadata" % dynmodel.name
        contact_columns = default_contact_model_columns(dynmodel)
        dyn_contactmodel = models.DynamicModel.objects.create(
            name = contact_model_name,
            attrs = {
                "type": MODEL_TYPES.META,
                "related_name": "contactmetadata"
            },
            columns = contact_columns,
        )
        dyn_contactmodel.save()

        # connect a signal to attach blank FK relationships upon
        # record create for this new table
        post_save.connect(attach_blank_meta_to_record, sender=Model)


def attach_blank_meta_to_record(sender, instance, **kwargs):
    """
    This signal gets ran when a new CSV-backed form response record
    gets added to the system.

    Here, we manage creating & linking blank metadata foreignkeys to
    new records upon their creation. This signal handler assumes
    its only provided Models that are backed by a CSV (not manually
    managed).
    """
    if not instance:
        return

    meta_model_name = "%sMetadata" % instance._meta.object_name
    try:
        meta_model_desc = models.DynamicModel.objects.get(name=meta_model_name)
    except (models.DynamicModel.DoesNotExist, OperationalError) as e:
        logger.debug("Skipping signal on non-existant model: %s => %s" % (
            instance._meta.object_name, meta_model_name
        ))
        return
    MetaModel = meta_model_desc.get_model()
    meta_direct_count = MetaModel.objects.filter(
        metadata__id=instance.id
    ).count()
    if meta_direct_count:
        return

    # create a blank metadata record
    metadata = MetaModel.objects.create(
        metadata=instance
    )


# TODO: do this on Model.__new__ ?
def setup_dynmodel_signals():
    """
    Attach signals to our dynamically generated models. Here, we
    only attach dynamically-generated signals to non-CSV backed
    models.
    """
    models.DynamicModel._POST_SAVE_SIGNALS.append(build_and_link_metadata_fk)
    for dynmodel in models.DynamicModel.objects.all():
        if dynmodel.get_attr("type") != MODEL_TYPES.CSV:
            continue
        Model = getattr(models, dynmodel.name)
        post_save.connect(attach_blank_meta_to_record, sender=Model)


try:
    setup_dynmodel_signals()
except Exception as e:
    logger.error("[!] Error loading signals: %s" % e)
