import json
import logging
import sys

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django import forms

try:
    from django.utils import six
except ImportError:
    import six

from collaborative.fields import ColumnsField


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

class Spreadsheet(models.Model):
    """
    The model representation of a source data spreadsheet.
    """
    name = models.TextField(max_length=255)
    share_url = models.URLField(null=True, blank=True)
    columns = ColumnsField(null=True, blank=True)
    token = models.CharField(max_length=16, null=True, blank=True)

    def __unicode__(self):
        return "Spreadsheet: %s" % self.name

    def csv_header_to_model_header(self, header):
        for column in self.columns:
            if column["original_name"] == header:
                return column["name"]


def create_model_attrs(spreadsheet):
    """
    Build an individual model's attributes, specified by the
    Spreadsheet object (and JSON columns).
    """
    model_name = spreadsheet.name
    attrs = {
        "__module__": 'collaborative.models.%s' % model_name,
    }

    if type(spreadsheet.columns) != list:
        return None

    original_to_model_headers = {}
    for column in spreadsheet.columns:
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
    Build & register models from the spreadsheet model descriptions found
    in our database.
    """
    for sheet in Spreadsheet.objects.all():
        attrs = create_model_attrs(sheet)
        model_name = sheet.name

        if not attrs:
            logger.warn(
                "WARNING: skipping model: %s. bad columns record" % sheet.name)
            continue

        # we have no fields defined
        if len(attrs.keys()) <= 2:
            logger.warn(
                "WARNING: skipping model: %s. not enough columns" % sheet.name)
            continue

        # set DynRow w/o specifying it here
        _model = type(model_name, (models.Model,), attrs)
        setattr(sys.modules[__name__], model_name, _model)


try:
    create_models()
except Exception as e:
    logger.error("[!] Exception creating models: %s" % e)
    pass
