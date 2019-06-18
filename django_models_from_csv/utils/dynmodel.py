import re
import string

from django.contrib.auth.models import User
from django.db import connections, transaction

from django_models_from_csv.commands.csvsql import run_csvsql
from django_models_from_csv.commands.manage_py import run_inspectdb
from django_models_from_csv.models import DynamicModel
from django_models_from_csv.utils.common import get_setting
from django_models_from_csv.utils.csv import fetch_csv, clean_csv_headers
from django_models_from_csv.utils.models_py import (
    fix_models_py, extract_field_declaration_args,
    extract_field_type, extract_fields
)
from django_models_from_csv.utils.screendoor import ScreendoorImporter
from django_models_from_csv.utils.google_sheets import (
    GoogleOAuth, PrivateSheetImporter
)


CSV_MODELS_TEMP_DB = get_setting(
    "CSV_MODELS_TEMP_DB"
)


@transaction.atomic(using=CSV_MODELS_TEMP_DB)
def execute_sql(sql):
    """
    Run a SQL query against our secondary in-memory database.
    """
    conn = connections[CSV_MODELS_TEMP_DB]
    cursor = conn.cursor()
    cursor.execute(sql)
    table_name = re.findall("CREATE TABLE ([^ ]+) \(", sql)[0]
    return table_name


def from_models_py(name, models_py, **model_attrs):
    """
    Convert a generated models.py document to a DynamicModel with
    the specified name and URL to a source CSV.
    """
    fields = extract_fields(models_py)
    columns = []
    for field_name, declaration in fields.items():
        kwargs = extract_field_declaration_args(declaration)
        if not kwargs:
            kwargs = {}
        field_type = extract_field_type(declaration)
        try:
            original_name = kwargs.pop("db_column")
        except KeyError as e:
            original_name = field_name
        columns.append({
            "name": field_name,
            "original_name": original_name,
            "type": field_type,
            "attrs": kwargs,
            "searchable": True,
            "filterable": False,
        })
    dynmodel = DynamicModel.objects.create(
        name = name,
        columns = columns,
        **model_attrs
    )
    return dynmodel


def from_csv(name, csv_data, **kwargs):
    """
    Create a dynamic model from some CSV data (a string of a CSV).
    The model is given a specified name and is populated with the
    attributes found in kwargs.
    """
    # build SQL from CSV
    sql = run_csvsql(csv_data)
    # create these tables in our DB
    table_name = execute_sql(sql)
    # build models.py from this DB
    models_py = run_inspectdb(table_name=table_name)
    fixed_models_py = fix_models_py(models_py)
    return from_models_py(name, fixed_models_py, **kwargs)


def from_csv_url(name, csv_url, csv_google_sheets_auth_code=None):
    """
    Build a dynamic model from a CSV URL. This supports Google
    Sheets share URLs and normal remote CSVs.
    """
    csv = fetch_csv(csv_url)
    return from_csv(name, csv, **dict(
        csv_url=csv_url
    ))


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


def from_private_sheet(name, sheet_url, auth_code=None, refresh_token=None):
    """
    Build a model from a private Google Sheet, given an OAuth auth code
    or refresh token, private sheet URL and name. This, of course,
    assumes the user has already gone through the Google Auth flow and
    explicitly granted Sheets view access.
    """
    GOOGLE_CLIENT_ID = get_setting("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = get_setting("GOOGLE_CLIENT_SECRET")
    oauther = GoogleOAuth(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    access_data = oauther.get_access_data(
        code=auth_code, refresh_token=refresh_token
    )
    token = access_data["access_token"]
    csv = PrivateSheetImporter(token).get_csv_from_url(sheet_url)
    return from_csv(name, csv, **dict(
        csv_url=sheet_url,
        csv_google_refresh_token=refresh_token or access_data["refresh_token"],
    ))
