from copy import copy

from django.db import models
from jsonfield.fields import JSONField


class MODEL_TYPES:
    CSV = 1
    META = 2
    CONTACT = 3


def get_metamodel_name(name):
    return "%smetadata" % name


def get_contact_metamodel_name(name):
    return "%scontactmetadata" % name


# Legacy
DEFAULT_STATUSES = (
    (0, "Available"),
    (1, "In Progress"),
    (2, "Verified"),
    (3, "Spam"),
    (4, "Duplicate"),
    (5, "Not Applicable"),
    (6, "Inconclusive"),
    (7, "False"),
)

DEFAULT_STATUS_CHOICES = (
    "Available",
    "In Progress",
    "Verified",
    "Spam",
    "Duplicate",
    "Not Applicable",
    "Inconclusive",
    "False",
)

DEFAULT_META_COLUMNS = [{
    "name": "status",
    "type": "choice",
    "attrs": {
        "choices": ", ".join(DEFAULT_STATUS_CHOICES),
        "default": DEFAULT_STATUS_CHOICES[0],
    },
},{
    "name": "assigned_to",
    "type": "short-text",
    "attrs": {
        "max_length": 120,
        "blank": True,
        "null": True,
        "verbose_name": "Assigned to",
    },
},{
    "name": "notes",
    "type": "text",
    "attrs": {
        "blank": True,
        "null": True,
    },
}]


# Legacy
DEFAULT_CONTACT_METHODS = (
    (0, "Email"),
    (1, "Phone call"),
    (2, "In person"),
)

DEFAULT_CONTACT_METHOD_CHOICES = (
    "Email",
    "Phone call",
    "In person",
)

DEFAULT_CONTACT_COLUMNS = [{
    "name": "reporter",
    "type": "short-text",
    "attrs": {
        "max_length": 120
    }
},{
    "name": "method",
    "type": "choice",
    "attrs": {
        "choices": ", ".join(DEFAULT_CONTACT_METHOD_CHOICES),
        "default": DEFAULT_CONTACT_METHOD_CHOICES[0],
    },
}]

def default_contact_model_columns(parent_dynmodel):
    """
    Create "contact" model description for holding information
    about when a source was contacted, when and by whom.
    """
    columns = copy(DEFAULT_CONTACT_COLUMNS)
    columns.append({
        "name": "contact_date",
        "type": "datetime",
        "attrs": {
            "blank": True,
            "null": True,
        },
    })
    columns.append({
        "name": "metadata",
        "type": "foreignkey",
        "args": [parent_dynmodel.fullname, "SET_NULL"],
        "attrs": {
            "blank": True,
            "null": True,
        },
    })
    return columns


class AppSetting(models.Model):
    """
    A place to store some information about the current state of the
    system and to store credentials, etc.
    """
    name = models.CharField(max_length=128)
    data = JSONField(editable=True)

    def __str__(self):
        return "Application setting: %s" % (self.name.replace("_", " "))
