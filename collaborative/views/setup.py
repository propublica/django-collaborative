from django.shortcuts import render, redirect


def fetch_sheet(url):
    pass


def sheet_to_sql_create(sheet):
    pass


def execute_sql(sql):
    pass


def models_py_from_database():
    pass


def fix_models_py():
    pass


def setup_complete(request):
    if request.method == "GET":
        return render(request, 'setup-complete.html', {})
    elif  request.method == "POST":
        return redirect('/')


def setup_auth(request):
    if request.method == "GET":
        return render(request, 'setup-auth.html', {})
    elif  request.method == "POST":
        return redirect('setup-complete')


def setup_refine_schema(request):
    if request.method == "GET":
        return render(request, 'setup-refine-schema.html', {})
    elif  request.method == "POST":
        return redirect('setup-auth')


def setup_schema(request):
    if request.method == "GET":
        return render(request, 'setup-schema.html', {})
    elif  request.method == "POST":
        # get params from request
        # fetch sheet CSV
        # re-work the sheet headers into good column names
        # build sql from sheet CSV
        # create these tables in our DB (or new DB?)
        # build models.py from this DB
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
        return redirect('setup-schema')
