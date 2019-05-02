from django import forms
from jsonfield.forms import JSONFormField

from django_models_from_csv.widgets import ColumnsWidget
from django_models_from_csv.fields import ColumnsField
from django_models_from_csv.validators import validate_columns, COLUMN_TYPES


class ColumnsFormField(JSONFormField):
    empty_values = [None, [], '']

    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = ColumnsWidget(
                column_types = COLUMN_TYPES
            )
        super(ColumnsFormField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(ColumnsFormField, self).validate(value)
        validate_columns(value)


class SchemaRefineForm(forms.Form):
    columns = ColumnsFormField(label="DynamicModel columns")
