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
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from import_export.resources import modelresource_factory
import requests
from tablib import Dataset

from collaborative import models
from collaborative.forms import SchemaRefineForm #, ColumnsFormField
from collaborative.settings import BASE_DIR


SEC_DB_ALIAS = 'schemabuilding'


def extract_key_from_share_url(url):
    matches = re.findall(
        "https://docs.google.com/spreadsheets/d/([^/]+)/edit",
        url
    )
    if not matches:
        raise ValueError(_("Invalid Google Sheets share URL"))
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
        token = User.objects.make_random_password(length=16),
    )
    sheet.save()
    return sheet


def write_models_py(models_py):
    models_py_path = os.path.join(BASE_DIR, "collaborative", "models.py")
    with open(models_py_path, "w") as f:
        f.write(models_py)


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
    """
    Setup is complete. Show users some diagnostic information and let
    them continue.
    """
    if request.method == "GET":
        return render(request, 'setup-complete.html', {})
    elif  request.method == "POST":
        logout(request)
        return redirect('/')


def setup_auth(request):
    """
    Force the user to change the password and let them setup
    OAuth social login.
    """
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
        # TODO: store (google_oauth_key, google_oauth_secret) somewhere
        return redirect('setup-complete')


def setup_import(request):
    """
    Loads the rows found in the sheet into the database. This is
    done once the user has had a chance to change the column names
    and types.

    NOTE: We do the import as a POST as a security precaution. The
    GET phase isn't really necessary, so the page just POSTs the
    form automatically via JS on load.
    """
    sheet = models.Spreadsheet.objects.last()
    if request.method == "GET":
        return render(request, 'setup-import.html')
    elif request.method == "POST":
        share_url = sheet.share_url
        csv = fetch_sheet(share_url)
        Model = getattr(models, sheet.name)
        errors = import_users(csv, Model, sheet)
        if not errors:
            return redirect("setup-auth")
        return render(request, 'setup-import.html', {
            "errors": errors,
        })


@csrf_exempt
def setup_migrate(request):
    """
    Triggers a makemigrations and migrate via the API. The token
    is one-time use, as it's cleared here, pre-migrate.

    NOTE: This will cause the local server to restart, so we use
    it in conjunction with the setup-wait enpoint that triggers
    this endpoint, then waits for the server to come back up via
    JavaScript and then moves to the next part of the setup flow.

    Example:

        POST /setup-migrate

        { "token": "SHEET TOKEN HERE" }
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Bad method")
    token = request.POST.get("token")
    if not token:
        return HttpResponseBadRequest("Bad token provided")
    # security check
    sheet = get_object_or_404(models.Spreadsheet, token=token)
    sheet.token = None
    sheet.save()
    make_and_apply_migrations()
    return HttpResponse(200, "OK")


def setup_wait(request):
    """
    This view triggers a makemigrations/migrate via JS and
    waits for the server to come back online. It then automatically
    redirects the user to the view specified in the "next" param.
    """
    next = request.GET["next"] # required
    token = request.GET["token"] # required
    sheet = get_object_or_404(models.Spreadsheet, token=token)
    return render(request, 'setup-wait.html', {
        "next": next,
        "token": token,
    })


def setup_refine_schema(request):
    """
    Allow the user to modify the auto-generated column types and
    names. This is done before we import the sheet data.
    """
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
        url = reverse("setup-wait")
        next = reverse("setup-import")
        to = "%s?next=%s&token=%s" % (url, next, sheet.token)
        return redirect(to)


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
        return redirect('setup-refine-schema')


def setup_check(request):
    """
    Check to see if we have set up any spreadsheets, yet, and if
    not redirect to the setup wizard. If we've already set up a sheet,
    go to the normal admin.
    """
    sheet_count = models.Spreadsheet.objects.count()
    if not sheet_count:
        return redirect('setup-begin')
    return redirect('admin')
