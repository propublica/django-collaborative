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
    # Landing
    return render(request, 'setup-complete.html', {})


def setup_auth(request):
    # Landing
    return render(request, 'setup-auth.html', {})
    # Submit
    return redirect('setup-complete')


def setup_refine_schema(request):
    # Landing
    return render(request, 'setup-refine-schema.html', {})
    # Submit
    return redirect('setup-auth')


def setup_schema(request):
    # get params from request
    # fetch sheet CSV
    # re-work the sheet headers into good column names
    # build sql from sheet CSV
    # create these tables in our DB (or new DB?)
    # build models.py from this DB
    return render(request, 'setup-schema.html', {})
    # Submit
    return redirect('setup-refine-schema')


def setup_begin(request):
    """
    Entry point for setting up the rest of the system. At this point
    the user has logged in using the default login and are now getting
    ready to configure the database, schema (via Google sheets URL) and
    any authentication backends (Google Oauth2, Slack, etc).
    """
    return render(request, 'setup-begin.html', {})
