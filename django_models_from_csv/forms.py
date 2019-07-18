from django import forms
from django.urls import reverse
from jsonfield.forms import JSONFormField

from dal import autocomplete
from django_models_from_csv.widgets import ColumnsWidget
from django_models_from_csv.fields import ColumnsField
from django_models_from_csv.validators import validate_columns, COLUMN_TYPES


class ColumnsFormField(JSONFormField):
    empty_values = [None, [], ""]

    def __init__(self, *args, **kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = ColumnsWidget(
                column_types = COLUMN_TYPES
            )
        super(ColumnsFormField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(ColumnsFormField, self).validate(value)
        validate_columns(value)


class SchemaRefineForm(forms.Form):
    columns = ColumnsFormField(label="DynamicModel columns")


def create_taggable_form(Model, fields=None):
    """
    Create a ModelForm with support for select2-based tagging with autocomplete.
    """
    name = "Taggable%sForm" % Model._meta.object_name
    attrs = {
        "model": Model,
        "fields": (),
        "widgets": {
            "tags": autocomplete.TaggitSelect2(
                reverse("csv_models:tag-autocomplete")
            ),
        },
    }

    if fields:
        attrs["fields"] = fields
    if "tags" not in fields:
        fields.append("tags")

    Meta = type("Meta", (object,), attrs)
    return type(name, (autocomplete.FutureModelForm,), {
        "Meta": Meta,
    })
