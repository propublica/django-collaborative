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
        })
    dynmodel = DynamicModel.objects.create(
        name = name,
        csv_url = csv_url,
        columns = columns,
    )
    # dynmodel.save()
    return dynmodel


def from_csv_url(name, csv_url):
    csv = fetch_csv(csv_url)
    # build SQL from CSV
    sql = run_csvsql(csv)
    # create these tables in our DB
    table_name = execute_sql(sql)
    # build models.py from this DB
    models_py = run_inspectdb(table_name=table_name)
    fixed_models_py = fix_models_py(models_py)
    return from_models_py(name, csv_url, fixed_models_py)
