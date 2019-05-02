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



