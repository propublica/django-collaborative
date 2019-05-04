from copy import copy

from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from collaborative.models import (
    get_metamodel_name, Metadata, MODEL_TYPES, DEFAULT_META_COLUMNS
)
from collaborative.user import set_staff_status
from django_models_from_csv import models


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
            return


@receiver(pre_save, sender=models.DynamicModel)
def build_and_link_metadata_fk(sender, **kwargs):
    dynmodel = kwargs.get("instance")
    if not dynmodel:
        return

    tag_csv_dynmodel(dynmodel)

    mtype = dynmodel.get_attr("type")
    if mtype == MODEL_TYPES.CSV:
        # 1. look for dynmodel's corresponding meta model
        Model = dynmodel.get_model()
        metamodel_name = get_metamodel_name(dynmodel.name)
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


def attach_blank_meta_to_record(sender, **kwargs):
    """
    These signals manage inserting blank metadata foreignkeys to
    new records upon their creation.
    """
    record = kwargs.get("instance")
    if not record:
        return

    if not hasattr(record, "metadata_id"):
        return

    # get the record's model declaration
    # check if it's a CSV model
    # if not, return
    # get metadata model
    # lookup metadata record for this record
    # if found, return
    # create a blank metadata record
    # create a FK on the metadata -> this record


def setup_dynmodel_signals():
    """
    Attach signals to our dynamically generated models.
    """
    for dynmodel in models.DynamicModel.objects.all():
        if dynmodel.get_attr("type") != MODEL_TYPES.CSV:
            continue
        Model = getattr(models, dynmodel.name)
        pre_save.connect(attach_blank_meta_to_record, sender=Model)


try:
    setup_dynmodel_signals()
except Exception as e:
    print("[!] Error loading signals: %s" % e)
