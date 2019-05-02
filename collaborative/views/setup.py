import io
import os
import re
import sqlite3
import tempfile
import time

from csvkit.utilities.csvsql import CSVSQL
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.management.commands import makemigrations, migrate, inspectdb
from django.db import DEFAULT_DB_ALIAS, connections, transaction
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django_models_from_csv.forms import SchemaRefineForm
import requests

from collaborative.settings import BASE_DIR


def make_and_apply_migrations():
    """
    Runs the equivalent of makemigrations on our collaborative
    models.py and then applies he migrations via migrate.
    """
    models.create_models()
    # TODO: replace with migration-less DB management
    run_makemigrations("collaborative")
    run_migrate()


def setup_complete(request):
    """
    Setup is complete. Show users some diagnostic information and let
    them continue.
    """
    if request.method == "GET":
        return render(request, 'setup-complete.html', {})


@login_required
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
        return redirect("setup-complete")


@login_required
def setup_import(request, id):
    """
    Loads the rows found in the sheet into the database. This is
    done once the user has had a chance to change the column names
    and types.

    NOTE: We do the import as a POST as a security precaution. The
    GET phase isn't really necessary, so the page just POSTs the
    form automatically via JS on load.
    """
    sheet = get_object_or_404(models.DynamicModel, id=id)
    if request.method == "GET":
        return render(request, 'setup-import.html', {
            "sheet": sheet
        })
    elif request.method == "POST":
        csv_url = sheet.csv_url
        csv = fetch_sheet(csv_url)
        Model = getattr(models, sheet.name)
        errors = import_users(csv, Model, sheet)
        if not errors:
            return redirect("setup-auth")
        return render(request, 'setup-import.html', {
            "errors": errors,
            "sheet": sheet,
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
    sheet = get_object_or_404(models.DynamicModel, token=token)
    sheet.token = None
    sheet.save()
    make_and_apply_migrations()
    return HttpResponse(200, "OK")


@login_required
def setup_wait(request):
    """
    This view triggers a makemigrations/migrate via JS and
    waits for the server to come back online. It then automatically
    redirects the user to the view specified in the "next" param.
    """
    next = request.GET["next"] # required
    token = request.GET["token"] # required
    sheet = get_object_or_404(models.DynamicModel, token=token)
    return render(request, 'setup-wait.html', {
        "next": next,
        "token": token,
    })


@login_required
def setup_refine_schema(request, id):
    """
    Allow the user to modify the auto-generated column types and
    names. This is done before we import the sheet data.
    """
    sheet = get_object_or_404(models.DynamicModel, id=id)
    if request.method == "GET":
        refine_form = SchemaRefineForm({
            "columns": sheet.columns
        })
        return render(request, 'setup-refine-schema.html', {
            "form": refine_form,
            "sheet": sheet,
        })
    elif  request.method == "POST":
        refine_form = SchemaRefineForm(request.POST)
        if not refine_form.is_valid():
            return render(request, 'setup-refine-schema.html', {
                "form": refine_form,
                "sheet": sheet,
            })

        columns = refine_form.cleaned_data["columns"]
        sheet.columns = columns
        sheet.save()
        url = reverse("setup-wait")
        next = reverse("setup-import", args=[sheet.id])
        to = "%s?next=%s&token=%s" % (url, next, sheet.token)
        return redirect(to)


@login_required
def setup_begin(request):
    """
    Entry point for setting up the rest of the system. At this point
    the user has logged in using the default login and are now getting
    ready to configure the database, schema (via Google sheets URL) and
    any authentication backends (Google Oauth2, Slack, etc).
    """
    if request.method == "GET":
        # Don't go back into this flow if we've already done it
        sheet_count = models.DynamicModel.objects.count()
        if sheet_count and sheet_count > 0:
            return redirect('/admin/')
        return render(request, 'setup-begin.html', {})
    elif  request.method == "POST":
        # get params from request
        name = request.POST.get("name")
        csv_url = request.POST.get("csv_url")
        sheet = build_dynmodel(name, csv_url)
        return redirect('setup-refine-schema', sheet.id)



