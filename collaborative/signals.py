from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from collaborative.user import set_staff_status
from collaborative.models import Metadata
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

@receiver(pre_save, sender=models.DynamicModel)
def attach_fk_to_model(sender, **kwargs):
    dynmodel = kwargs.get("instance")
    print("#" * 100)
    print("Sender", sender)
    print("Pre-save", dynmodel)
    print("columns", dynmodel.columns)
    print("#" * 100)
    if not dynmodel:
        return
    for col in dynmodel.columns:
        if col["name"] == "metadata":
            return
    # if we're here, we haven't attached our relation
    fk_column = {
        "name": "metadata",
        "type": "foreignkey",
        "args": ["collaborative.Metadata", "SET_NULL"],
        "attrs": {
            "blank": True,
            "null": True,
        },
    }
    dynmodel.columns.append(fk_column)
    # # alredy added default fields
    # if dynmodel.extrafields:
    #     return
    # dynmodel.extrafields = DEFAULT_FIELDS


def attach_blank_meta_to_record(sender, **kwargs):
    rec = kwargs.get("instance")
    print("|"*100)
    print("rec", rec)
    if not rec:
        return
    # if not hasattr(rec, "metadata_id"):
    #     return
    meta = Metadata.objects.create()
    print("meta", meta)
    rec.metadata = meta
    print("|"*100)


def setup_dynmodel_signals():
    print("setup_dynmodel_signals" * 10)
    for dynmodel in models.DynamicModel.objects.all():
        print("dynmodel", dynmodel)
        Model = getattr(models, dynmodel.name)
        pre_save.connect(attach_blank_meta_to_record, sender=Model)


try:
    setup_dynmodel_signals()
except Exception as e:
    print("[!] Error loading signals: %s" % e)
