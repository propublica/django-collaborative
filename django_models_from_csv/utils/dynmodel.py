from functools import wraps
import logging
import re
from io import StringIO

from django.db import connections, transaction
from tablib import Dataset

from django_models_from_csv.commands.csvsql import run_csvsql
from django_models_from_csv.commands.manage_py import run_inspectdb
from django_models_from_csv.exceptions import (
    UniqueColumnError, DataSourceExistsError, NoPrivateSheetCredentialsError,
)
from django_models_from_csv.models import DynamicModel
from django_models_from_csv.utils.common import get_setting, slugify
from django_models_from_csv.utils.csv import fetch_csv, clean_csv_headers
from django_models_from_csv.utils.models_py import (
    fix_models_py, extract_field_declaration_args_eval,
    extract_field_type, extract_fields
)
from django_models_from_csv.utils.screendoor import ScreendoorImporter
from django_models_from_csv.utils.google_sheets import PrivateSheetImporter


logger = logging.getLogger(__name__)


CSV_MODELS_TEMP_DB = get_setting(
    "CSV_MODELS_TEMP_DB"
)


@transaction.atomic(using=CSV_MODELS_TEMP_DB)
def execute_sql(sql, params=None):
    """
    Run a SQL query against our secondary in-memory database. Returns
    the table name, if this was a CREATE TABLE command, otherwise just
    returns None.
    """
    conn = connections[CSV_MODELS_TEMP_DB]
    cursor = conn.cursor()
    if params is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, params)
    matches = re.findall("CREATE TABLE ([^ ]+) \\(", sql)
    if not matches:
        return None
    table_name = matches[0]
    return table_name


def require_unique_name(f):
    @wraps(f)
    def unique_name_wrapper(*args, **kwargs):
        name = args[0]
        if DynamicModel.objects.filter(name=name).count():
            raise DataSourceExistsError(name)
        return f(*args, **kwargs)
    return unique_name_wrapper


def csv_precheck(csv_data):
    """
    Do some basic sanity checks on a CSV.
    """
    data = Dataset().load(csv_data, format="csv")
    unique_names = []
    for header in data.headers:
        if header in unique_names:
            raise UniqueColumnError(header)
        unique_names.append(header)


def from_models_py(name, models_py, **model_attrs):
    """
    Convert a generated models.py document to a DynamicModel with
    the specified name and URL to a source CSV.
    """
    logger.debug("New model: %s models.py:\n %s" % (name, models_py))
    fields = extract_fields(models_py)
    columns = []
    for field_name, declaration in fields.items():
        logger.info("Column field_name: %s declaration: %s" % (
            field_name, declaration
        ))

        kwargs = extract_field_declaration_args_eval(declaration)
        if not kwargs:
            kwargs = {}
            logger.info("Field kwargs: %s" % (kwargs))

        field_type = extract_field_type(declaration)
        logger.info("field_type: %s" % (field_type))

        try:
            original_name = kwargs.pop("db_column")
        except KeyError as e:
            original_name = field_name
        column = {
            "name": field_name,
            "original_name": original_name,
            "type": field_type,
            "attrs": kwargs,
            "searchable": True,
            "filterable": False,
        }
        columns.append(column)
        logger.info("from_models_py Columns: %s" % column)
    dynmodel = DynamicModel.objects.create(
        name=name,
        columns=columns,
        **model_attrs
    )
    return dynmodel


def from_csv(name, csv_data, **kwargs):
    """
    Create a dynamic model from some CSV data (a string of a CSV).
    The model is given a specified name and is populated with the
    attributes found in kwargs.
    """
    logger.debug("New model from CSV:\n %s" % name)
    csv_precheck(csv_data)
    # build SQL from CSV
    sql = run_csvsql(csv_data)
    logger.debug("SQL: %s" % sql)
    # create these tables in our DB
    table_name = execute_sql(sql)
    logger.debug("table_name: %s" % table_name)
    # build models.py from this DB
    models_py = run_inspectdb(table_name=table_name)
    logger.debug("models_py: %s" % models_py)
    # # wipe the temporary table
    # logger.debug("Dropping temporary table '%s'" % (table_name))
    # execute_sql("DROP TABLE %s", [table_name])
    fixed_models_py = fix_models_py(models_py)
    logger.debug("fixed_models_py: %s" % fixed_models_py)
    return from_models_py(name, fixed_models_py, **kwargs)


@require_unique_name
def from_csv_file(filename, file):
    """
    Import a file from an upload, using its filename as the data
    source name.
    """
    csv = clean_csv_headers(file.read().decode("utf-8"))
    name = filename
    no_ext = re.findall(r"^(.*)\.csv$", name)
    if no_ext:
        name = no_ext[0]
    dynmodel = from_csv(slugify(name), csv)
    with StringIO() as fio:
        fio.write(csv)
        dynmodel.csv_file.save(name, fio)
        dynmodel.save()
        return dynmodel


@require_unique_name
def from_csv_url(name, csv_url):
    """
    Build a dynamic model from a CSV URL. This supports Google
    Sheets share URLs and normal remote CSVs.
    """
    csv = fetch_csv(csv_url)
    return from_csv(name, csv, **dict(
        csv_url=csv_url
    ))


@require_unique_name
def from_screendoor(name, api_key, project_id, form_id=None):
    """
    Build a dynamic model from a screendoor project/form, given
    a supplied API KEY. This will fetch all the data from the
    API and build a CSV, which will be used to build the rest
    of the table.
    """
    importer = ScreendoorImporter(api_key=api_key)
    csv = importer.build_csv(project_id, form_id=form_id)
    return from_csv(name, csv, **dict(
        sd_api_key=api_key,
        sd_project_id=project_id,
        sd_form_id=form_id,
    ))


@require_unique_name
def from_private_sheet(name, sheet_url, credentials=None):
    """
    Build a model from a private Google Sheet. Credentials is the
    service account secrets JSON data, provided by the google API
    console. It should either be a JSON string or a JSON file (bytes).
    """
    if not credentials:
        raise NoPrivateSheetCredentialsError(
            "No private sheet credentials found."
        )
    csv = PrivateSheetImporter(credentials).get_csv_from_url(sheet_url)
    return from_csv(name, csv, **dict(
        csv_url=sheet_url,
        csv_google_sheet_private=True,
    ))
