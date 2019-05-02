import re

from django.db import connections, transaction

from django_models_from_csv.commands.csvsql import run_csvsql
from django_models_from_csv.commands.manage_py import run_inspectdb
from django_models_from_csv.utils.models_py import (
    fix_models_py, build_sheet_object
)
from django_models_from_csv.utils.common import get_setting


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


# TODO: replace with DynamicModel.create(url) command
def build_dynmodel(name, csv_url):
    # fetch sheet CSV
    sheet = fetch_sheet(csv_url)
    # build sql from sheet CSV
    sql = run_csvsql(sheet)
    # create these tables in our DB (or new DB?)
    table_name = execute_sql(sql)
    # build models.py from this DB
    models_py = run_inspectdb(table_name=table_name)
    fixed_models_py = fix_models_py(models_py)
    # TODO: convert models.py to JSON
    sheet = build_sheet_object(fixed_models_py, name, csv_url)
