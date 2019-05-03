from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


COLUMN_TYPES = (
    ("text",     "Text field"),
    ("date",     "Date field"),
    ("time",     "Time field"),
    ("datetime", "Date and time field"),
    ("number",   "Number field"),
    ("foreignkey",   "Associated Table"),
)
REQUIRED_FIELDS = (
    "name", "type", "type"
)
ALL_FIELDS = REQUIRED_FIELDS + (
    "attrs", "original_name", "args",
)


def validate_columns(value):
    if not value:
        return

    for col in value:
        for field_name in REQUIRED_FIELDS:
            req_field = col.get(field_name)
            if not req_field:
                raise ValidationError(
                    _("A column is missing required field: %s" % field_name)
                )
            if field_name not in ALL_FIELDS:
                raise ValidationError(
                    _("A column contains invalid field: %s" % field_name)
                )

        type = col.get("type")
        valid_type_names = [v[0] for v in COLUMN_TYPES]
        if type not in valid_type_names:
            raise ValidationError(_("A column has invalid type: %s" % type))

        attrs = col.get("attrs", {})
        if attrs and not isinstance(attrs, dict):
            raise ValidationError(_("Column attributes must be a dictionary"))

