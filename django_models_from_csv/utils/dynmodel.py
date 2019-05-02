import re

from django.contrib.auth.models import User
from django.db import connections, transaction

from django_models_from_csv.commands.csvsql import run_csvsql
from django_models_from_csv.commands.manage_py import run_inspectdb
from django_models_from_csv.models import DynamicModel
from django_models_from_csv.utils.common import get_setting
from django_models_from_csv.utils.models_py import (
    fix_models_py, extract_field_declaration_args,
    extract_field_type, extract_fields
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


def from_models_py(name, csv_url, models_py):
    """
    Convert a generated models.py document to a DynamicModel with
    the specified name and URL to a source CSV.
    """
    fields = extract_fields(models_py)
    columns = []
    for field_name, declaration in fields.items():
        kwargs = extract_field_declaration_args(declaration)
        field_type = extract_field_type(declaration)
        original_name = kwargs.pop("db_column")
        columns.append({
            "name": field_name,
            "original_name": original_name,
            "type": field_type,
            "attrs": kwargs,
        })
    sheet = DynamicModel.objects.create(
        name = name,
        csv_url = csv_url,
        columns = columns,
        token = User.objects.make_random_password(length=16),
    )
    return sheet


def from_csv_url(name, csv_url):
    # fetch sheet CSV
    sheet = fetch_sheet(csv_url)
    # build sql from sheet CSV
    sql = run_csvsql(sheet)
    # create these tables in our DB (or new DB?)
    table_name = execute_sql(sql)
    # build models.py from this DB
    models_py = run_inspectdb(table_name=table_name)
    fixed_models_py = fix_models_py(models_py)
    sheet = from_models_py(fixed_models_py, name, csv_url)
    return sheet
