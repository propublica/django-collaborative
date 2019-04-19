from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from jsonfield.widgets import JSONWidget
from jsonfield.forms import JSONFormField
from jsonfield.fields import JSONField

from collaborative.widgets import ColumnsWidget
from collaborative.validators import validate_columns, COLUMN_TYPES


class ColumnsField(JSONField):
    """
    A field describing the columns of a source spreadsheet and
    their representation in our model.
    """
    description = _("Columns in a spreadsheet")

    def formfield(self, **kwargs):
        defaults = {
            'form_class': JSONFormField,
            'widget': ColumnsWidget(column_types=COLUMN_TYPES)
        }
        defaults.update(**kwargs)
        return super(JSONField, self).formfield(**defaults)

    def validate(self, value, model_instance):
        super(ColumnsField, self).validate(value, model_instance)
        validate_columns(value)
