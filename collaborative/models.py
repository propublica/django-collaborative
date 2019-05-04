from django.db import models
from django.utils.timezone import now


class MODEL_TYPES:
    CSV = 1
    META = 2
    CONTACT = 3


def get_metamodel_name(name):
    return "%sMetadata" % name


DEFAULT_STATUSES = (
    (0, "Available"),
    (1, "In Progress"),
    (2, "Verified"),
    (3, "Troll"),
    (4, "Duplicate"),
    (5, "Not Applicable"),
    (6, "Inconclusive"),
    (7, "False"),
)


DEFAULT_META_COLUMNS = [{
    "name": "status",
    "type": "number",
    "attrs": {
        "choices": DEFAULT_STATUSES,
        "default": DEFAULT_STATUSES[0][0],
    },
},{
    "name": "partner",
    "type": "short-text",
    "attrs": {
        "max_length": 120,
        "blank": True,
        "null": True
    },
},{
    "name": "notes",
    "type": "text",
    "attrs": {
        "blank": True,
        "null": True,
    },
}]


class Metadata(models.Model):
    """
    Additional metadata for annotating and tracking the form responses
    and proples' progress.
    """

    # record = models.ForeignKey(
    #     models.FormRecord,
    # )


class Contact(models.Model):
    """
    Information about when a source was contacted, when and by whom.
    """
    METHODS = (
        (0, "Email"),
        (1, "Phone call"),
        (2, "In person"),
    )

    reporter = models.CharField(max_length=120)
    method = models.IntegerField(
        choices=METHODS,
    )
    contact_date = models.DateTimeField(
        default=now,
    )
    metadata = models.ForeignKey(
        Metadata, models.SET_NULL,
        blank=True, null=True
    )
