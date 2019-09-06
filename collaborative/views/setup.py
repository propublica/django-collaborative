import io
import re
import sqlite3
import tempfile
import time

from csvkit.utilities.csvsql import CSVSQL
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

from collaborative.models import AppSetting
from collaborative.settings import BASE_DIR
from django_models_from_csv import models
from django_models_from_csv.models import CredentialStore


def setup_complete(request):
    """
    Setup is complete. Show users some diagnostic information and let
    them continue.
    """
    if request.method == "GET":
        return render(request, 'setup-complete.html', {
            "user": request.user or "admin",
        })


@login_required
def setup_credentials(request):
    """
    Let the user setup Google credentials.
    """
    # flag indicating we just saved a model, not visited this
    # page directly. this lets us avoid showing this after every
    # import a user does
    is_postsave = request.GET.get("postsave")
    current_host = request.META.get('HTTP_HOST', "http://localhost/")

    # Don't show the password change screen if we've already
    # added models or setup an initial password.
    try:
        AppSetting.objects.get(
            name="initial_setup_completed"
        )
        if is_postsave:
            return redirect('/admin/')
    except AppSetting.DoesNotExist as e:
        pass

    sheets_cred = CredentialStore.objects.filter(
        name="csv_google_credentials"
    ).first()
    dlp_cred = CredentialStore.objects.filter(
        name="google_dlp_credentials"
    ).first()
    oauth_cred = CredentialStore.objects.filter(
        name="google_oauth_credentials"
    ).first()

    # this is what we show the user
    oauth_json_creds = None
    if oauth_cred.credentials_json:
        oauth_json_creds = oauth_cred.credentials_json
        # re-stringify whitelist
        whitelist = oauth_json_creds.get("google_oauth_whitelist")
        if whitelist:
            oauth_json_creds["google_oauth_whitelist"] = ",".join(whitelist)

    if request.method == "GET":
        return render(request, 'setup-credentials.html', {
            "hostname": current_host,
            "sheets_cred": sheets_cred,
            "dlp_cred": dlp_cred,
            "oauth_cred": oauth_json_creds,
        })

    elif request.method == "POST":
        sheets_credentials_file = request.FILES.get("csv_google_credentials")
        dlp_credentials = request.FILES.get("google_redaction_credentials")
        google_oauth_key = request.POST.get("google_oauth_key")
        google_oauth_secret = request.POST.get("google_oauth_secret")
        google_oauth_whitelist = request.POST.get("google_oauth_whitelist")

        # set an appsetting that will prevent the configure auth
        # screen from showing up again
        AppSetting.objects.get_or_create(
            name="initial_setup_completed",
        )

        if dlp_credentials:
            dlp, _ = CredentialStore.objects.get_or_create(
                name="google_dlp_credentials"
            )
            dlp.credentials = dlp_credentials.read().decode("utf-8")
            dlp.save()

        if google_oauth_key:
            setting, created = CredentialStore.objects.get_or_create(
                name="google_oauth_credentials"
            )
            parsed_whitelist = [
                w.strip() for w in google_oauth_whitelist.strip().split(",")
                if w and w.strip()
            ]
            data = {
                "google_oauth_key": google_oauth_key,
                "google_oauth_secret": google_oauth_secret,
                "google_oauth_whitelist": parsed_whitelist,
            }
            setting.credentials = data
            setting.save()

        if sheets_credentials_file:
            cred, _ = CredentialStore.objects.get_or_create(
                name="csv_google_credentials"
            )
            cred.credentials = sheets_credentials_file.read().decode("utf-8")
            cred.save()

        return redirect('/admin/')

