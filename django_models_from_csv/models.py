import json
import logging
import sys

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django import forms

try:
    from django.utils import six
except ImportError:
    import six

from django_models_from_csv.fields import ColumnsField


logger = logging.getLogger(__name__)


# For lookup during conversion from generated models.py
TYPE_TO_FIELDNAME = {
    "models.TextField": "text",
    "models.DateField": "date",
    "models.TimeField": "time",
    "models.DateTimeField": "datetime",
    "models.IntegerField": "number",
    "models.CharField": "text",
}
# configurable field types for dynamic models
FIELD_TYPES = {
    "text": models.TextField,
    "date": models.DateField,
    "time": models.TimeField,
    "datetime": models.DateTimeField,
    "number": models.IntegerField,
}


def random_token(length=16):
    return User.objects.make_random_password(length=length)


class DynamicModel(models.Model):
    """
    The managed database model representing the data in a CSV file.
    """
    name = models.TextField(max_length=255)
    csv_url = models.URLField(null=True, blank=True)
    columns = ColumnsField(null=True, blank=True)
    token = models.CharField(
        max_length=16,
        null=True, blank=True,
        default=random_token,
    )

    def __unicode__(self):
        return "Dynamic Model: %s" % self.name

    def csv_header_to_model_header(self, header):
        for column in self.columns:
            if column["original_name"] == header:
                return column["name"]

    def make_token(self):
        return random_token(16)

def create_model_attrs(dynmodel):
    """
    Build an individual model's attributes, specified by the
    DynamicModel object (and JSON columns).
    """
    model_name = dynmodel.name
    attrs = {
        "__module__": 'django_models_from_csv.models.%s' % model_name,
    }

    if type(dynmodel.columns) != list:
        return None

    original_to_model_headers = {}
    for column in dynmodel.columns:
        column_name = column.get("name")
        og_column_name = column.get("original_name")
        column_type = column.get("type")
        column_attrs = column.get("attrs", {})

        if not column_name or not column_type:
            continue

        original_to_model_headers[og_column_name] = column_name

        Field = FIELD_TYPES[column_type]
        attrs[column_name] = Field(**column_attrs)

    attrs["HEADERS_LOOKUP"] = original_to_model_headers
    return attrs


def create_models():
    """
    Build & register models from the DynamicModel descriptions found
    in our database.
    """
    for dynmodel in DynamicModel.objects.all():
        attrs = create_model_attrs(dynmodel)
        model_name = dynmodel.name

        if not attrs:
            logger.warn(
                "WARNING: skipping model: %s. bad columns record" % dynmodel.name)
            continue

        # we have no fields defined
        if len(attrs.keys()) <= 2:
            logger.warn(
                "WARNING: skipping model: %s. not enough columns" % dynmodel.name)
            continue

        # set DynRow w/o specifying it here
        _model = type(model_name, (models.Model,), attrs)
        setattr(sys.modules[__name__], model_name, _model)


try:
    create_models()
except Exception as e:
    logger.error("[!] Exception creating models: %s" % e)
    pass
