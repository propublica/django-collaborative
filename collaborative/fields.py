from django.utils.translation import gettext_lazy as _
from jsonfield.widgets import JSONWidget
from jsonfield.forms import JSONFormField
from jsonfield.fields import JSONField

from collaborative.widgets import ColumnsWidget


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
            'widget': ColumnsWidget(column_types=self.COLUMN_TYPES)
        }
        defaults.update(**kwargs)
        return super(JSONField, self).formfield(**defaults)


