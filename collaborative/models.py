import json
import sys

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django import forms
from django.utils.translation import gettext_lazy as _

from jsonfield.widgets import JSONWidget
from jsonfield.forms import JSONFormField
from jsonfield.fields import JSONField

try:
    from django.utils import six
except ImportError:
    import six

from collaborative.widgets import ColumnsWidget


# configurable field types for dynamic models
FIELD_TYPES = {
    "text": models.TextField,
    "date": models.DateField,
    "time": models.TimeField,
    "datetime": models.DateTimeField,
    "number": models.IntegerField,
}


class ColumnsField(JSONField):
    """
    A field describing the columns of a source spreadsheet and
    their representation in our model.
    """
    COLUMN_TYPES = (
        ("text",     "Text field"),
        ("date",     "Date field"),
        ("time",     "Time field"),
        ("datetime", "Date and time field"),
        ("number",   "Number field"),
    )
    description = _("Columns in a spreadsheet")

    def formfield(self, **kwargs):
        defaults = {
            'form_class': JSONFormField,
            # 'widget': JSONWidget,
            'widget': ColumnsWidget(column_types=self.COLUMN_TYPES)
        }
        defaults.update(**kwargs)
        return super(JSONField, self).formfield(**defaults)


class SpreadSheet(models.Model):
    """
    The model representation of a source data spreadsheet.
    """
    name = models.TextField(max_length=255)
    columns = ColumnsField(null=True, blank=True)

    def __unicode__(self):
        return "SpreadSheet: %s" % self.name


def create_model_attrs(spreadsheet):
    """
    Build an individual model's attributes, specified by the
    SpreadSheet object (and JSON columns).
    """
    model_name = spreadsheet.name
    attrs = {
        "__module__": 'collaborative.models.%s' % model_name
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
    for sheet in SpreadSheet.objects.all():
        print("Building sheet", sheet)
        attrs = create_model_attrs(sheet)
        print("Attrs", attrs)
        model_name = sheet.name
        print("model_name", model_name)

        if not attrs:
            print("WARNING: skipping model: %s. bad columns record" % sheet.name)
            continue

        # we have no fields defined
        if len(attrs.keys()) <= 2:
            print("WARNING: skipping model: %s. not enough columns" % sheet.name)
            continue

        # set DynRow w/o specifying it here
        print("Creating model", model_name)
        _model = type(model_name, (models.Model,), attrs)
        print("_model", _model)
        setattr(sys.modules[__name__], model_name, _model)
        print("Created model", _model)


create_models()


# model_name = "DynRow"
# attrs = {
#     "timestamp": models.TextField(
#         db_column='Timestamp', blank=True, null=True
#     ),
#     "question_with_short_answer_field": models.TextField(
#         db_column='Question with short answer?'
#     ),
#     "question_with_long_answer_field": models.TextField(
#         db_column='Question with long answer?'
#     ),
#     "checkbox_field": models.TextField(
#         db_column='Checkbox?'
#     ),
#     "option_with_dropdown_field": models.TextField(
#         db_column='Option with dropdown?'
#     ),
#     "multiple_choice_field": models.TextField(
#         db_column='Multiple choice?'
#     ),
#     "field_numeric_linear_scale_field": models.TextField(
#         db_column='Numeric linear scale?'
#     ),
#     "multiple_choice_grid_row1_field": models.TextField(
#         db_column='Multiple choice grid? [row1]'
#     ),
#     "multiple_choice_grid_row2_field": models.TextField(
#         db_column='Multiple choice grid? [row2]'
#     ),
#     "checkbox_grid_row1_field": models.TextField(
#         db_column='Checkbox grid? [row1]'
#     ),
#     "checkbox_grid_row2_field": models.TextField(
#         db_column='Checkbox grid? [row2]'
#     ),
#     "what_date_field": models.DateField(
#         db_column='What date?'
#     ),
#     "what_time_field": models.TextField(
#         db_column='What time?'
#     ),
#     '__module__': 'collaborative.models.%s' % model_name
# }

# # TODO: Save this information during CSV -> model transformation
# TRANSLATION_TABLE = {
#     "Timestamp": "timestamp",
#     "Question with short answer?": "question_with_short_answer_field",
#     "Question with long answer?": "question_with_long_answer_field",
#     "Checkbox?": "checkbox_field",
#     "Option with dropdown?": "option_with_dropdown_field",
#     "Multiple choice?": "multiple_choice_field",
#     " Numeric linear scale?": "field_numeric_linear_scale_field",
#     "Multiple choice grid? [row1]": "multiple_choice_grid_row1_field",
#     "Multiple choice grid? [row2]": "multiple_choice_grid_row2_field",
#     "Checkbox grid? [row1]": "checkbox_grid_row1_field",
#     "Checkbox grid? [row2]": "checkbox_grid_row2_field",
#     "What date?": "what_date_field",
#     "What time?": "what_time_field",
# }
