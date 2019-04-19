import io
import os
import re
import sqlite3
import tempfile
import time

from csvkit.utilities.csvsql import CSVSQL
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.management.commands import makemigrations, migrate, inspectdb
from django.db import DEFAULT_DB_ALIAS, connections, transaction
from django.shortcuts import render, redirect
from import_export.resources import modelresource_factory
import requests
from tablib import Dataset

from collaborative import models
# from collaborative.fields import ColumnsField
from collaborative.forms import SchemaRefineForm #, ColumnsFormField
from collaborative.settings import BASE_DIR
# from collaborative.widgets import ColumnsWidget


SEC_DB_ALIAS = 'schemabuilding'


def extract_key_from_share_url(url):
    matches = re.findall(
        "https://docs.google.com/spreadsheets/d/([^/]+)/edit",
        url
    )
    if not matches:
        raise ValueError("Invalid Google Sheets share URL")
    return matches[0]


def fetch_sheet(share_url):
    """
    Take a Google Sheet share link like this:
        https://docs.google.com/spreadsheets/d/KEY_HERE/edit#gid=09232

    And return the corresponding CSV.
    """
    key = extract_key_from_share_url(share_url)
    url = 'https://docs.google.com/spreadsheet/ccc?key=%s&output=csv' % (
        key
    )
    r = requests.get(url)
    data = r.text
    return data


class FakeArgs():
    encoding= "utf-8"
    skip_lines = 0
    table_names = None
    query = None
    unique_constraint = None
    connection_string = None
    insert = False
    no_create = False
    create_if_not_exists = False
    overwrite = None
    before_insert = None
    after_insert = None
    chunk_size = None
    sniff_limit = 1000
    no_inference = False
    date_format = None
    datetime_format = None
    locale = 'en_US'
    db_schema = None
    no_constraints = False


class CSVSQLWrap(CSVSQL):
    reader_kwargs = {}

    def __init__(self):
        self.args = FakeArgs()


def sheet_to_sql_create(sheet):
    """
    Runs the equivalent of:
        csvsql -S -i postgresql sheet.csv

    Returns a SQL CREATE TABLE command.
    """
    f_in = tempfile.NamedTemporaryFile(mode='w', delete=False)
    f_in.write(sheet)
    f_in.flush()
    try:
        # We have to close this in Windows
        f_in.close()
    except Exception as e:
        pass # this means we're on a unix env
    f_out = io.StringIO()
    # csvsql = CSVSQLWrap()
    csvsql = CSVSQLWrap()
    csvsql.args.dialect = "sqlite"
    csvsql.args.skipinitialspace = True
    csvsql.args.input_paths = [f_in.name]
    csvsql.output_file = f_out
    csvsql.main()
    return f_out.getvalue()


@transaction.atomic(using=SEC_DB_ALIAS)
def execute_sql(sql):
    """
    Run a SQL query against our secondary in-memory database.
    """
    conn = connections[SEC_DB_ALIAS]
    cursor = conn.cursor()
    cursor.execute(sql)
    table_name = re.findall("CREATE TABLE ([^ ]+) \(", sql)[0]
    return table_name

def models_py_from_database(table_name=None):
    """
    Run inspectdb against our secondary in-memory database. Basically,
    we're running the equivalent of this manage.py command:

        ./manage.py inspectdb --database schemabuilding

    Returns the generated models.py
    """
    cmd = inspectdb.Command()
    options = {
        'verbosity': 1,
        'settings': None,
        'pythonpath': None,
        'traceback': False,
        'no_color': False,
        'force_color': False,
        'table': [table_name] or [],
        'database': SEC_DB_ALIAS,
        'include_partitions': False,
        'include_views': False
    }
    # This command returns a generator of models.py text lines
    gen = cmd.handle_inspection(options)
    return "\n".join(list(gen))


def fix_models_py(models_py):
    """
    The output of inspectdb is pretty messy, so here we trim down
    some of the mess, add mandatory ID field and fix the bad
    conversion to CharField (we use TextField instead).
    """
    lines = models_py.split("\n")
    fixed_lines = []
    for line in lines:
        # Postgres TextFields are preferable. No performance
        # hit compared to CharField and we don't need to
        # specify a max length
        line = line.replace(
            "CharField", "TextField"
        )

        # Strip out comments. They're super long and repetitive
        try:
            comment_ix = line.index("#")
        except ValueError as e:
            comment_ix = -1
        if comment_ix == 0:
            continue
        elif comment_ix != -1:
            line = line[0:comment_ix]

        # Skip the managed part. We're going to actually
        # use a managed model, derived from the auto-generated
        # models.py
        if "class Meta:" in line:
            continue
        elif "managed = False" in line:
            continue
        elif "db_table = " in line:
            continue

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def extract_fields(models_py):
    """
    Take a models.py string and extract the lines that
    declare model fields into a dictionary of the following
    format:

        { "FIELD_NAME": "models.FieldType(arguments...)" }
    """
    fields = {}
    for line in models_py.split("\n"):
        # skip imports
        if re.match(".*from.*import.*", line):
            continue
        # skip class declarations
        if re.match(".*class\s+.*models\.Model.*", line):
            continue
        # extract field name
        field_matches = re.match("\s*([^\s\-=]+)\s*=\s*(.*)$", line)
        if not field_matches or not field_matches.groups():
            continue
        field, declaration = field_matches.groups()
        fields[field] = declaration
    return fields


def extract_field_declaration_args(declaration_str):
    matches = re.match(".*\((.*)\)", declaration_str)
    args_str = matches.groups()[0]
    indiv_args = re.split(",\s*", args_str)
    kw_arguments = {}
    for arg in indiv_args:
        key, value = arg.split("=", 1)
        kw_arguments[key] = eval(value)
    return kw_arguments


def extract_field_type(declaration_str):
    matches = re.match(".*(models\.[A-Za-z0-9_]+)\(", declaration_str)
    field_class_str = matches.groups()[0]
    # TODO: default here? or use default dict in TYPE_TO_FIELDNAME
    type_name = models.TYPE_TO_FIELDNAME[field_class_str]
    return type_name


def build_sheet_object(models_py, model_name, share_url):
    fields = extract_fields(models_py)
    columns = []
    for name, declaration in fields.items():
        kwargs = extract_field_declaration_args(declaration)
        field_type = extract_field_type(declaration)
        original_name = kwargs.pop("db_column")
        columns.append({
            "name": name,
            "original_name": original_name,
            "type": field_type,
            "attrs": kwargs,
        })
    sheet = models.Spreadsheet(
        name = model_name,
        share_url = share_url,
        columns = columns,
    )
    return sheet


def write_models_py(models_py):
    models_py_path = os.path.join(BASE_DIR, "collaborative", "models.py")
    with open(models_py_path, "w") as f:
        f.write(models_py)


def write_settings_py(oauth_key, oauth_secret):
    path = os.path.join(BASE_DIR, "collaborative", "settings_config.py")
    settings_py = """
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "%s"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "%s"
""" % ( oauth_key, oauth_secret)
    with open(path, "w") as f:
        f.write(settings_py)


def make_and_apply_migrations():
    """
    Runs the equivalent of makemigrations on our collaborative
    models.py and then applies he migrations via migrate.
    """
    models.create_models()
    # apply the model to the DB
    mkmigrate_cmd = makemigrations.Command()
    args = ('collaborative',)
    options =  {
        'verbosity': 1,
        'settings': None,
        'pythonpath': None,
        'traceback': False,
        'no_color': False,
        'force_color': False,
        'dry_run': False,
        'merge': False,
        'empty': False,
        'interactive': True,
        'name': None,
        'include_header': True,
        'check_changes': False
    }
    mkmigrate_cmd.handle(*args, **options)
    # apply the migrations
    migrate_cmd = migrate.Command()
    args = ()
    options = {
        'verbosity': 3,
        'interactive': False,
        'database': DEFAULT_DB_ALIAS,
        'run_syncdb': True,
        'app_label': None,
        'plan': None,
        'fake': False,
        'fake_initial': False,
    }
    migrate_cmd.handle(*args, **options)
    # short pause to allow for migration to complete. eventually
    # we may want to use JS to test for the server to complete the
    # cycle, during a middle phase during which we do the migration
    time.sleep(2)


# TODO: pass sheet mode lin here
def import_users_list(csv, sheet):
    """
    Take a fetched CSV and turn it into a tablib Dataset, with
    a row ID column and all headers translated to model field names.
    """
    data = Dataset().load(csv)
    data.insert_col(0, col=[i+1 for i in range(len(data))], header='id')
    # Turn our CSV columns into model columns
    for i in range(len(data.headers)):
        header = data.headers[i]
        model_header = sheet.csv_header_to_model_header(header)
        if model_header and header != model_header:
            data.headers[i] = model_header
    return data


# TODO: pass sheet model in here
def import_users(csv, Model, sheet):
    """
    Take a fetched sheet CSV, parse it into user rows for
    insertion and attempt to import the data into the
    specified model.

    This performs a pre-import routine which will return
    failure information we can display and let the user fix
    the sheet before trying again. On success this function
    returns None.

    TODO: Only show N number of errors. If there are more,
    tell the user more errors have been supressed and to
    fix the ones listed before continuing. We don't want
    to overwhelm the user with error messages.
    """
    resource = modelresource_factory(model=Model)()
    dataset = import_users_list(csv, sheet)
    result = resource.import_data(dataset, dry_run=True)
    # TODO: transform errors to something readable
    if result.has_errors():
        return result.row_errors()
    resource.import_data(dataset, dry_run=False)


def setup_complete(request):
    if request.method == "GET":
        return render(request, 'setup-complete.html', {})
    elif  request.method == "POST":
        # cleanup, reboot server if deployed?
        logout(request)
        return redirect('/')


def setup_auth(request):
    if request.method == "GET":
        return render(request, 'setup-auth.html', {})
    elif request.method == "POST":
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        google_oauth_key = request.POST.get("google_oauth_key")
        google_oauth_secret = request.POST.get("google_oauth_secret")
        if password != password_confirm:
            raise ValueError("Passwords do not match!")
        admin = User.objects.get(username="admin")
        admin.set_password(password)
        admin.save()
        # write_settings_py(google_oauth_key, google_oauth_secret)
        return redirect('setup-complete')


def setup_refine_schema(request):
    sheet = models.Spreadsheet.objects.last()
    if request.method == "GET":
        refine_form = SchemaRefineForm({
            "columns": sheet.columns
        })
        return render(request, 'setup-refine-schema.html', {
            "form": refine_form,
        })
    elif  request.method == "POST":
        refine_form = SchemaRefineForm(request.POST)
        if not refine_form.is_valid():
            return render(request, 'setup-refine-schema.html', {
                "form": refine_form,
            })

        columns = refine_form.cleaned_data["columns"]
        sheet.columns = columns
        sheet.save()
        make_and_apply_migrations()
        share_url = sheet.share_url
        csv = fetch_sheet(share_url)
        Model = getattr(models, sheet.name)
        errors = import_users(csv, Model, sheet)
        if not errors:
            return redirect('setup-auth')
        return render(request, 'setup-refine-schema.html', {
            "form": refine_form,
            "errors": errors,
        })


def setup_schema(request):
    if request.method == "GET":
        return render(request, 'setup-schema.html', {})
    elif  request.method == "POST":
        return redirect('setup-refine-schema')


def setup_begin(request):
    """
    Entry point for setting up the rest of the system. At this point
    the user has logged in using the default login and are now getting
    ready to configure the database, schema (via Google sheets URL) and
    any authentication backends (Google Oauth2, Slack, etc).
    """
    if request.method == "GET":
        return render(request, 'setup-begin.html', {})
    elif  request.method == "POST":
        # get params from request
        share_url = request.POST.get("share_url")
        name = request.POST.get("name")
        # fetch sheet CSV
        sheet = fetch_sheet(share_url)
        # build sql from sheet CSV
        sql = sheet_to_sql_create(sheet)
        # create these tables in our DB (or new DB?)
        table_name = execute_sql(sql)
        # build models.py from this DB
        models_py = models_py_from_database(table_name=table_name)
        fixed_models_py = fix_models_py(models_py)
        # TODO: convert models.py to JSON
        sheet = build_sheet_object(fixed_models_py, name, share_url)
        sheet.save()
        make_and_apply_migrations()
        return redirect('setup-refine-schema')
