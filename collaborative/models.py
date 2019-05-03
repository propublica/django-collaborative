from django.db import models
from django.utils.timezone import now


class Metadata(models.Model):
    """
    Additional metadata for annotating and tracking the form responses
    and proples' progress.
    """
    STATUSES = (
            (0, "Available"),
            (1, "In Progress"),
            (2, "Verified"),
            (3, "Troll"),
            (4, "Duplicate"),
            (5, "Not Applicable"),
            (6, "Inconclusive"),
            (7, "False"),
    )

    status = models.IntegerField(
        choices=STATUSES,
        default=STATUSES[0][0],
    )
    partner = models.CharField(max_length=120, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)


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
