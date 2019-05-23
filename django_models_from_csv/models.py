import json
import logging
import sys

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonfield.fields import JSONField

try:
    from django.utils import six
except ImportError:
    import six

from django_models_from_csv.fields import ColumnsField


logger = logging.getLogger(__name__)


# For lookup during conversion from generated models.py
TYPE_TO_FIELDNAME = {
    "models.TextField": "text",
    "models.CharField": "text",
    "models.DateField": "date",
    "models.TimeField": "time",
    "models.DateTimeField": "datetime",
    "models.IntegerField": "number",
    "models.ForeignKey": "foreignkey",
}
# configurable field types for dynamic models.
# any that aren't above, but are below will be
# possible to create in the code/by modifying
# the columns JSON directly, but will not be
# shown to users as a dropdown field type.
FIELD_TYPES = {
    "text": models.TextField,
    "short-text": models.CharField,
    "date": models.DateField,
    "time": models.TimeField,
    "datetime": models.DateTimeField,
    "number": models.IntegerField,
    "foreignkey": models.ForeignKey,
}


def random_token(length=16):
    return User.objects.make_random_password(length=length)


class DynamicModel(models.Model):
    """
    The managed database model representing the data in a CSV file.
    """
    # name of this model. should be singular and contain no spaces
    # or special characters. e.g., FormResponse, SurveyResult
    name = models.CharField(max_length=255)
    # a URL to a Google Sheet or any source CSV for building model
    csv_url = models.URLField(null=True, blank=True)
    # columns derived from the above CSV. this field is managed
    # by the library, but it can be changed and managed manually
    # after it's been instantiated
    columns = ColumnsField(null=True, blank=True)

    # some attributes (as dict) to distinguish dynamic models from
    # eachother, to drive some business logic, etc. not used internally.
    attrs = JSONField(max_length=255, editable=True)
    # a token for authenticating migration requests
    # TODO: remove this once we've moved to migrationless
    token = models.CharField(
        max_length=16,
        null=True, blank=True,
        default=random_token,
    )

    class Meta:
        verbose_name = _("Successful Import")
        verbose_name_plural = _("Successful Imports")

    @property
    def fullname(self):
        """
        Fully qualified name of this module, for use in ForeignKeys
        and importing via `to` arguments.
        """
        return "django_models_from_csv.%s" % self.name

    def __str__(self):
        return "Model Description: %s (%i columns)" % (
            self.name, len(self.columns))

    def get_attr(self, value):
        """
        Return an attribute, by key. This function assumes that
        the attr field is a single JSON object/Python dict.
        """
        if not self.attrs:
            return None
        return self.attrs.get(value)

    def get_column(self, value, key="name"):
        """
        Lookup and return a column by attribute value. By
        default this checks the "name" key. Returns None
        if such a column isn't found or if the column field
        is null.
        """
        if not self.columns:
            return None
        for col in self.columns:
            if col.get(key) == value:
                return col

    def get_model(self, name=None):
        """
        Return the Model created by this dynamic model
        description. For example, if this DynamicModel instance
        refers, by "name" attribute, to OtherRecord then this
        method will return the models.OtherRecord class.

        Returns None is model doesn't exist.
        """
        these_models = sys.modules[__name__]
        model_name = name or self.name
        if not hasattr(these_models, model_name):
            return None
        return getattr(these_models, model_name)

    def csv_header_to_model_header(self, header):
        column = self.get_column(header, key="original_name")
        if not column:
            return None
        return column.get("name")

    def make_token(self):
        return random_token(16)


def create_model_attrs(dynmodel):
    """
    Build an individual model's attributes, specified by the
    DynamicModel object (and JSON columns).
    """
    model_name = dynmodel.name
    attrs = {
        "__module__": "django_models_from_csv.models.%s" % model_name,
    }

    if type(dynmodel.columns) != list:
        return None

    original_to_model_headers = {}
    for column in dynmodel.columns:
        column_name = column.get("name")
        og_column_name = column.get("original_name")
        column_type = column.get("type")
        column_args = column.get("args", [])
        column_attrs = column.get("attrs", {})

        if not column_name or not column_type:
            continue

        original_to_model_headers[og_column_name] = column_name

        Field = FIELD_TYPES[column_type]
        attrs[column_name] = Field(*column_args, **column_attrs)

        # include any column choice structs as [COL_NAME]_CHOICES
        choices = column_attrs.get("choices")
        if choices:
            choices_attr = "%s_CHOICES" % column_name.upper()
            attrs[choices_attr] = choices

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
