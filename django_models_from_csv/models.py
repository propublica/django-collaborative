import importlib
import json
import logging
import re
import sys

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls.base import clear_url_caches
from django.utils.module_loading import import_module
from django.utils.translation import gettext_lazy as _
from jsonfield.fields import JSONField
from taggit.managers import TaggableManager

from django_models_from_csv.fields import ColumnsField
from django_models_from_csv.permissions import (
    hydrate_models_and_permissions, wipe_models_and_permissions,
)
from django_models_from_csv.schema import ModelSchemaEditor, FieldSchemaEditor
from django_models_from_csv.utils.common import slugify
from django_models_from_csv.utils.csv import fetch_csv
from django_models_from_csv.utils.google_sheets import PrivateSheetImporter
from django_models_from_csv.utils.importing import import_records
from django_models_from_csv.utils.screendoor import ScreendoorImporter


logger = logging.getLogger(__name__)


# For lookup during conversion from generated models.py
TYPE_TO_FIELDNAME = {
    "models.TextField": "text",
    "models.CharField": "short-text",
    "models.DateField": "date",
    "models.TimeField": "time",
    "models.DateTimeField": "datetime",
    "models.FloatField": "number",
    "models.IntegerField": "integer",
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
    "number": models.FloatField,
    "integer": models.IntegerField,
    "foreignkey": models.ForeignKey,
    "tagging": TaggableManager,
}


def random_token(length=16):
    return User.objects.make_random_password(length=length)


class CredentialStore(models.Model):
    """
    A place to store data source related credentials.
    """
    CREDENTIAL_TYPES = {
        "google_oauth_credentials": "JSON",
        "google_dlp_credentials": "JSON",
        "csv_google_credentials": "JSON",
    }
    # Currently used keyspaces:
    # Key                       Type         Descripion
    # ========================= ============ ================================
    # google_oauth_credentials  json string  Google OAuth client secrets
    # google_dlp_credentials    json string  Google DLP credentials
    # csv_google_credentials    json string  Google Sheets credentials
    name = models.CharField(max_length=1024)
    credentials = models.TextField(null=True, blank=True)

    @property
    def credentials_json(self):
        if not self.credentials:
            return self.credentials
        try:
            return json.loads(self.credentials)
        except json.JSONDecodeError as e:
            logger.error("Bad Google OAuth credential found!")
            return None

    def clean_json(self, credentials):
        """
        Turn json of various types into a UTF-8 string for storage.
        """
        # file upload => string
        if isinstance(credentials, bytes):
            return credentials.decode("utf-8")
        elif isinstance(credentials, dict):
            return json.dumps(credentials)
        return credentials

    def create(self, **kwargs):
        if "credentials" in kwargs:
            kwargs["credentials"] = self.clean_json(kwargs.get("credentials"))
        return super().create(**kwargs)

    def save(self, **kwargs):
        if self.credentials:
            cleaned = self.clean_json(self.credentials)
            self.credentials = cleaned
        if "credentials" in kwargs:
            kwargs["credentials"] = self.clean_json(kwargs.get("credentials"))
        return super().save(**kwargs)


class DynamicModel(models.Model):
    """
    The managed database model representing the data in a CSV file.
    """
    # name of this model. should be singular and contain no spaces
    # or special characters. e.g., FormResponse, SurveyResult
    name = models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    # columns derived from the above CSV. this field is managed
    # by the library, but it can be changed and managed manually
    # after it's been instantiated
    columns = ColumnsField(null=True, blank=True)

    # URL to a Google Sheet or any source CSV for building model
    csv_url = models.URLField(null=True, blank=True)
    # Flag marking this as private (we will use the service account
    # credentials to access the sheet, assuming they exist)
    csv_google_sheet_private = models.BooleanField(
        default=False,
    )

    # Screendoor-specific columns
    sd_api_key = models.CharField(max_length=100, null=True, blank=True)
    sd_project_id = models.IntegerField(null=True, blank=True)
    sd_form_id = models.IntegerField(null=True, blank=True)

    # File upload storage
    csv_file = models.FileField(
        upload_to="csv_uploads/", blank=True,
    )

    # some attributes (as dict) to distinguish dynamic models from
    # eachother, to drive some business logic, etc. not used internally.
    # Currently used attributes:
    # Key   Type   Description
    # ======================================================================
    # type  int    Model type (1=Base model, 2=Metadata, 3=Contact log)
    # dead  bool   If True, this model has been failing auto update and
    #              will be skipped until a manual successful import succeeds
    attrs = JSONField(max_length=255, editable=True)

    # This is a bit of a hack, but since Django calls post_save
    # migrations inside of save(), and we have to do our manual
    # migrations *after* save, there is a .middle state when using
    # actual migrations (model exists, but not in table). This
    # is a hacky workaround to get post_save signals to run after
    # save() and DB migrations have been ran.
    _POST_SAVE_SIGNALS = []

    class Meta:
        verbose_name = _("Successful Import")
        verbose_name_plural = _("Successful Imports")

    def __init__(self, *args, **kwargs):
        """
        Initialize the schema editor with the currently registered model and the
        initial name.
        """
        super().__init__(*args, **kwargs)
        self._initial_name = self.name
        initial_model = self.get_model(name=self._initial_name)
        self.schema_editor = ModelSchemaEditor(initial_model)

    def __str__(self):
        return "Model Description: %s (%i columns)" % (
            self.name, len(self.columns))

    @property
    def fullname(self):
        """
        Fully qualified name of this module, for use in ForeignKeys
        and importing via `to` arguments.
        """
        return "django_models_from_csv.%s" % self.name

    def csv_header_to_model_header(self, header):
        column = self.get_column(header, key="original_name")
        if not column:
            return None
        return column.get("name")

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
        model_name = name or self.name
        try:
            return apps.get_model('django_models_from_csv', model_name)
        except LookupError as e:
            return None

    def import_data(self, max_import_records=None, csv_file=None):
        """
        Perform a (re)import on a previously loaded model. This takes
        the loaded columns into account, ignoring any new columns that
        may exist in the spreadsheet.
        """
        if not self.columns:
            logger.warn("Attempted to import source without columns. Baililng")
            return [
                "Data source hasn't been configured. Re-import this source " \
                "using the confiruation wizard."
            ]

        creds_model = CredentialStore.objects.filter(
            name="csv_google_credentials"
        ).first()

        csv = None
        if self.csv_url and creds_model:
            csv = PrivateSheetImporter(
                creds_model.credentials
            ).get_csv_from_url(
                self.csv_url
            )
        elif self.csv_url:
            # NOTE: InvalidDimensions
            csv = fetch_csv(self.csv_url)
        elif self.sd_api_key:
            importer = ScreendoorImporter(
                api_key=self.sd_api_key,
                max_import_records=max_import_records,
            )
            csv = importer.build_csv(
                self.sd_project_id, form_id=self.sd_form_id
            )
        elif csv_file:
            csv = csv_file.read().decode("utf-8")
        elif self.csv_file:
            csv = self.csv_file.read().decode("utf-8")
        else:
            raise NotImplementedError("Invalid data source for %s" % self)

        return import_records(csv, self.get_model(), self)


    def make_token(self):
        return random_token(16)

    def find_old_field(self, OldModel, field):
        """
        Find matching field from old instance of the model using
        the database column name. This works for now, until we
        change the update strategy to hash based on the column
        description JSON.
        """
        if not OldModel:
            return
        for old_field in OldModel._meta.fields:
            if field.column == old_field.column:
                return old_field

    def do_migrations(self):
        """
        Do a custom migration without leaving any migration files
        around.
        """
        old_desc = DynamicModel.objects.filter(name=self.name).first()
        try:
            OldModel = apps.get_model("django_models_from_csv", self.name)
        except LookupError:
            OldModel = None

        # TODO: for some reason force_new=True (removed now, but forces re-
        # creation of the model class) makes the model show up multiple
        # times in the admin. but setting this to False makes the meta
        # schema migrations not work properly w/o restarting the system.
        # I need to fix this, along with custom meta in general, but for
        # now we need to reinstate sane working defaults.
        NewModel = construct_model(self)
        new_desc = self
        ModelSchemaEditor(OldModel).update_table(NewModel)

        for new_field in NewModel._meta.fields:
            if new_field.name == "id":
                continue
            old_field = self.find_old_field(OldModel, new_field)
            if old_field:
                FieldSchemaEditor(old_field).update_column(NewModel, new_field)

    def model_cleanup(self):
        create_models()
        importlib.reload(import_module(settings.ROOT_URLCONF))
        app_config = apps.get_app_config("django_models_from_csv")
        hydrate_models_and_permissions(app_config)
        apps.clear_cache()
        clear_url_caches()

    def save(self, **kwargs):
        self.name = slugify(self.name)
        super().save(**kwargs)
        self.do_migrations()
        self.model_cleanup()
        for fn in self._POST_SAVE_SIGNALS:
            fn(self)

    def delete(self, **kwargs):
        # first drop the table, we have to do this first, else
        # django will complain about no content type existing
        Model = apps.get_model("django_models_from_csv", self.name)
        ModelSchemaEditor().drop_table(Model)

        # then remove django app and content-types/permissions
        app_config = apps.get_app_config("django_models_from_csv")
        wipe_models_and_permissions(app_config, self.name)

        # finally kill the row
        super().delete(**kwargs)

        # delete it from the django app registry
        try:
            del apps.all_models["django_models_from_csv"][self.name]
        except KeyError as err:
            raise LookupError("'{}' not found.".format(self.name))

        # Unregister the model from the admin, before we wipe it out
        try:
            admin.site.unregister(Model)
        except admin.sites.NotRegistered:
            pass


def verbose_namer(name, make_friendly=False):
    """
    Removes all values of screendoor IDs from the column name. Optionally
    this will make the column name friendly by removing dashes/underscore
    with spaces.
    """
    if name.endswith("contactmetadata"):
        return "Contact MetaData"
    elif name.endswith("metadata"):
        return "MetaData"
    no_sd_id = re.sub(r"\s*\(ID:\s*[a-z0-9]+\)$", "", name)
    if not make_friendly:
        return no_sd_id
    return re.sub(r"[_\-]+", " ", no_sd_id)


def get_source_dynmodel(self):
    name = self._meta.object_name
    try:
        return DynamicModel.objects.get(name=name)
    except DynamicModel.DoesNotExist as e:
        logger.warning("Couldn't find DynamicModel with name=%s" % name)


def dynmodel__str__(self):
    if hasattr(self, "name"):
        return "Row from data source '%s'" % (self.name)
    return "Row from data source"


def create_model_attrs(dynmodel):
    """
    Build an individual model's attributes, specified by the
    DynamicModel object (and JSON columns).
    """
    model_name = dynmodel.name
    Meta = type("Meta", (), dict(
        managed=False,
        verbose_name=verbose_namer(model_name, make_friendly=True),
        verbose_name_plural=verbose_namer(model_name, make_friendly=True),
    ))

    attrs = {
        "__module__": "django_models_from_csv.models.%s" % model_name,
        "Meta": Meta,
        "source_dynmodel": get_source_dynmodel,
        # "tags": TaggableManager(blank=True),
    }

    # make the objects displayed in the admin easy to understant. the
    # default of '[Model name] (ID)' doesn't provide any useful information
    # to the end user, so hide it here.
    if not model_name.endswith("metadata"):
        attrs["__str__"] = dynmodel__str__
    else:
        attrs["__str__"] = lambda s: model_name

    if not isinstance(dynmodel.columns, list):
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
        if column_type == "foreignkey":
            fk_model_name = column_args[0]
            fk_on_delete = getattr(models, column_args[1])
            attrs[column_name] = Field(
                fk_model_name, fk_on_delete, **column_attrs
            )
        else:
            verbose = column_name
            if og_column_name:
                verbose = re.sub(
                    r"\s*\(ID:\s*[a-z0-9]+\)$", "", og_column_name
                )
                verbose = re.sub(r"[_\-]+", " ", verbose)
            if "verbose_name" not in column_attrs:
                column_attrs["verbose_name"] = verbose
            attrs[column_name] = Field(
                *column_args, **column_attrs
            )

        # include any column choice structs as [COL_NAME]_CHOICES
        choices = column_attrs.get("choices")
        if choices:
            choices_attr = "%s_CHOICES" % column_name.upper()
            attrs[choices_attr] = choices

    attrs["HEADERS_LOOKUP"] = original_to_model_headers
    return attrs


def construct_model(dynmodel):
    """
    This creates the model instance from a dynamic model description record.
    """
    model_name = dynmodel.name
    _model = dynmodel.get_model()

    if not hasattr(sys.modules[__name__], model_name):
        setattr(sys.modules[__name__], model_name, _model)

    if _model:
        return _model

    attrs = create_model_attrs(dynmodel)

    if not attrs:
        logger.warn(
            "WARNING: skipping model: %s. bad columns record" % dynmodel.name)
        return

    # we have no fields defined
    if len(attrs.keys()) <= 2:
        logger.warning(
            "WARNING: skipping model: %s. not enough columns" % dynmodel.name)
        return

    return type(model_name, (models.Model,), attrs)


def create_models():
    """
    Build & register models from the DynamicModel descriptions found
    in our database.
    """
    for dynmodel in DynamicModel.objects.all():
        model_name = dynmodel.name
        _model = construct_model(dynmodel)
        if not _model:
            logger.error("No model was created for: %s" % model_name)
            continue

        these_models = apps.all_models["django_models_from_csv"]
        these_models[model_name] = _model


try:
    create_models()
except Exception as e:
    logger.error("[!] Exception creating models: %s" % e)
