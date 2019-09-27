from copy import copy
import logging

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.utils import OperationalError
from django.dispatch import receiver

from collaborative.models import (
    MODEL_TYPES, DEFAULT_META_COLUMNS,
    default_contact_model_columns
)
from collaborative.user import set_staff_status
from django_models_from_csv import models
from django_models_from_csv.permissions import build_tag_permission_group


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

    tag_perm_group = build_tag_permission_group()
    tag_perm_group.user_set.add(user)


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
    logger.debug("build_and_link_metadata_fk dynmodel: %s" % (dynmodel))
    if not dynmodel:
        logger.warning("No dynmodel! Not attaching.")
        return

    tag_csv_dynmodel(dynmodel)

    mtype = dynmodel.get_attr("type")
    if mtype == MODEL_TYPES.CSV:
        # 1. look for dynmodel's corresponding meta model
        Model = dynmodel.get_model()
        metamodel_name = "%smetadata" % dynmodel.name

        dyn_metamodel_count = models.DynamicModel.objects.filter(
            name=metamodel_name
        ).count()
        logger.debug("dyn_metamodel_count: %s" % (dyn_metamodel_count))

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
            name=metamodel_name,
            attrs={
                "type": MODEL_TYPES.META,
            },
            columns=columns,
        )
        dyn_metamodel.save()

        # 2. c) Create contact meta model for this dynmodel
        # NOTE: since we always create metadata model along
        # with contact model, we know that contact model
        # hasn't been created if metadata doesn't already
        # exist (so no additional check)
        contact_model_name = "%scontactmetadata" % dynmodel.name
        contact_columns = default_contact_model_columns(dynmodel)
        dyn_contactmodel = models.DynamicModel.objects.create(
            name=contact_model_name,
            attrs={
                "type": MODEL_TYPES.META,
                "related_name": "contactmetadata"
            },
            columns=contact_columns,
        )
        dyn_contactmodel.save()

        # # connect a signal to attach blank FK relationships upon
        # # record create for this new table
        # logger.debug("Attaching blank meta creator to model: %s" % (
        #     str(Model)
        # ))
        # post_save.connect(attach_blank_meta_to_record, sender=Model)


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


try:
    setup_dynmodel_signals()
except OperationalError as e:
    logger.debug("[!] Skipping operational error: %s" % (e))
except Exception as e:
    logger.error("[!] Error loading signals: %s" % (e))
