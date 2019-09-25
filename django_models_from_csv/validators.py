from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# NOTE: when these change, ensure the columnswidget.html
# JavasCript changes to include any new fields
COLUMN_TYPES = (
    ("text", "Textbox field"),
    ("short-text", "Text field"),
    ("date", "Only date field"),
    ("time", "Only time field"),
    ("datetime", "Date and time field"),
    ("number", "Number field"),
    # ("foreignkey", "Associated Table"),
    # ("tagging", "Tags field"),
)
# This gets used as the set of field types available
# to users to add/remove/alter. The ones that are
# not in here (commented out) will be automatically
# added and never allowed to be changed/added/removed
META_COLUMN_TYPES = (
    ("text", "Textbox field"),
    ("short-text", "Text field"),
    ("date", "Only date field"),
    ("time", "Only time field"),
    ("datetime", "Date and time field"),
    ("number", "Number field"),
    ("choice", "Choice selection field"),
    # ("foreignkey", "Associated Table"),
    # ("tagging", "Tags field"),
    # ("created-at", "Create time (readonly)"),
)

# fields required by all model types. this
# is external to the "columns" type, which gets
# checked using the above data structures
REQUIRED_FIELDS = (
    "name", "type",
)
# specify all allowed fields (hidden or otherwise)
# here. if a field is found attached to a model
# not in this list, we will throw a validation error
ALL_FIELDS = REQUIRED_FIELDS + (
    "attrs", "original_name", "args",
    "searchable", "filterable",
    "redact",
)


def validate_columns(value, model_type=None):
    """
    Validate the columns and attribtues on a dynamic model. If we
    know this is a meta (or contact log) model, set model_type to "meta".
    If it's a base import model, set this to "base". Otherwise leave
    this argument to None and we will combine both checks and make sure
    one of them passes.
    """
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

        column_types = META_COLUMN_TYPES + COLUMN_TYPES
        if model_type == "base":
            column_types = COLUMN_TYPES
        elif model_type == "meta":
            column_types = META_COLUMN_TYPES

        col_type = col.get("type")
        valid_type_names = [v[0] for v in column_types]
        if col_type not in valid_type_names:
            raise ValidationError(_("A column has invalid type: %s" % col_type))

        attrs = col.get("attrs", {})
        if attrs and not isinstance(attrs, dict):
            raise ValidationError(_("Column attributes must be a dictionary"))

