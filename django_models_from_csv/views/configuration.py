import logging
import json

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tablib.core import UnsupportedFormat
from requests.exceptions import ConnectionError

from django_models_from_csv import models
from django_models_from_csv.exceptions import GenericCSVError
from django_models_from_csv.forms import SchemaRefineForm
from django_models_from_csv.utils.common import get_setting, slugify
from django_models_from_csv.utils.csv import fetch_csv
from django_models_from_csv.utils.dynmodel import (
    from_csv_url, from_screendoor, from_private_sheet,
    from_csv_file,
)
from django_models_from_csv.models import CredentialStore


logger = logging.getLogger(__name__)


def get_credentials_model():
    """
    Find the stored Google creds JSON model.
    """
    return CredentialStore.objects.filter(
        name="csv_google_credentials"
    ).first()


def get_service_account_email(credential_model):
    """
    Get the service account email from the stored Google creds JSON.
    """
    if not credential_model.credentials:
        return None
    credentials = json.loads(credential_model.credentials)
    return credentials.get("client_email")


@login_required
def begin(request):
    """
    Entry point for setting up the rest of the system. At this point
    the user has logged in using the default login and are now getting
    ready to configure the database, schema (via Google sheets URL) and
    any authentication backends (Google Oauth2, Slack, etc).
    """
    if request.method == "GET":
        # Don't go back into this flow if we've already done it
        addnew = request.GET.get("addnew")
        models_count = models.DynamicModel.objects.count()
        if not addnew and models_count:
            return redirect('/admin/')

        context = {
            "first_run": True,
        }
        creds_model = get_credentials_model()
        if creds_model:
            context["service_account_email"] = get_service_account_email(
                creds_model
            )

        if CredentialStore.objects.count():
            context["first_run"] = False

        # NOTE: this leaves this module separated from collaborate, but
        # still compatable in its presence
        try:
            AppSetting = apps.get_model("collaborative", "appsetting")
            app_setting = AppSetting.objects.filter(
                name="initial_setup_completed"
            ).count()
            if app_setting:
                context["first_run"] = False
        except LookupError:
            pass

        return render(request, 'begin.html', context)
    elif request.method == "POST":
        # For CSV URL/Google Sheets (public)
        csv_url = request.POST.get("csv_url")

        # Private Sheet toggle (all other private sheet stuff will
        # be ignored if this wasn't checked in the form
        # NOTE: Why getlist? Well, django POST with checkboxes only
        # returns blank strings as checkbox values. So we check the
        # list to see if it has any length (not not) and go with that.
        # (A list like this [''] is truthy, this [] is not!)
        # Unsolved SO issue: https://stackoverflow.com/questions/47374647
        csv_sheets_private = request.POST.getlist("csv_google_sheet_private")
        # Private Google Sheet (Service Account Credentials JSON) ...
        # this only gets displayed when there are no other creds uploaded
        csv_google_credentials_file = request.FILES.get(
            "csv_google_credentials"
        )
        # Also see if we've already saved a dynamic model, we will use
        # the credentials from this file and the email for the UI
        creds_model = get_credentials_model()
        service_account_email = None
        if creds_model:
            service_account_email = get_service_account_email(creds_model)

        # Screendoor
        sd_api_key = request.POST.get("sd_api_key")
        sd_project_id = request.POST.get("sd_project_id")
        sd_form_id = request.POST.get("sd_form_id")

        # CSV File Upload
        csv_file = request.FILES.get("csv_file_upload")

        # TODO: move all this into a form
        context = {
            "csv_name": request.POST.get("csv_name"),
            "csv_url": csv_url,
            "sd_name": request.POST.get("sd_name"),
            "sd_api_key": sd_api_key,
            "sd_project_id": sd_project_id,
            "sd_form_id": sd_form_id,
            "service_account_email": service_account_email,
        }
        try:
            if csv_url and csv_sheets_private:
                name = slugify(request.POST.get("csv_name"))
                # pull the credentials from FILE or saved model
                credentials = None
                if csv_google_credentials_file:
                    credentials = csv_google_credentials_file.read(
                    ).decode("utf-8")
                    cr, _ = CredentialStore.objects.get_or_create(
                        name="csv_google_credentials",
                    )
                    cr.credentials = credentials
                    cr.save()
                elif creds_model:
                    credentials = creds_model.credentials
                else:
                    # TODO: raise if we got a check marked private,
                    # but couldn't find the credential and none uploaded
                    # here. we should direct them to the google page
                    pass
                dynmodel = from_private_sheet(
                    name, csv_url,
                    credentials=credentials,
                )
            elif csv_url:
                name = slugify(request.POST.get("csv_name"))
                dynmodel = from_csv_url(
                    name, csv_url,
                )
            elif sd_api_key:
                name = slugify(request.POST.get("sd_name"))
                max_import_records = None
                if hasattr(settings, "MAX_IMPORT_RECORDS"):
                    max_import_records = settings.MAX_IMPORT_RECORDS
                dynmodel = from_screendoor(
                    name,
                    sd_api_key,
                    int(sd_project_id),
                    form_id=int(sd_form_id) if sd_form_id else None,
                    max_import_records=max_import_records,
                )
            elif csv_file:
                dynmodel = from_csv_file(
                    csv_file.name, csv_file,
                )
            else:
                return render(request, 'begin.html', {
                    "errors": "No data source selected!",
                    **context
                })

        except Exception as e:
            # TODO: roll back
            if not isinstance(e, GenericCSVError):
                raise e
            return render(request, 'begin.html', {
                "errors": e.render(),
                **context
            })
        # handles valid URLs to non-CSV data and also just bad URLs
        except UnsupportedFormat as e:
            # TODO: roll back
            err_msg = _(
                "Invalid data source. Please make sure you "
                "linked to a valid CSV data source."
            )
            return render(request, 'begin.html', {
                "errors": err_msg,
                **context
            })
        except ConnectionError as e:
            # TODO: roll back
            err_msg = _(
                "Invalid URL. Please make sure there aren't "
                "typos in the URL, and that the data isn't "
                "protected. If you're trying to use a protected "
                "Google Sheet, you need to use the private Sheet "
                "authenticator, below."
            )
            return render(request, 'begin.html', {
                "errors": err_msg,
                **context
            })
        return redirect('csv_models:refine-and-import', dynmodel.id)


@login_required
def refine_and_import(request, id):
    """
    Allow the user to modify the auto-generated column types and
    names. This is done before we import the dynmodel data.

    If this succeeds, we do some preliminary checks against the
    CSV file to make sure there aren't duplicate headers/etc.
    Then we do the import. On success, this redirects to the URL
    specified by the CSV_MODELS_WIZARD_REDIRECT_TO setting if
    it exists.
    """
    dynmodel = get_object_or_404(models.DynamicModel, id=id)
    if request.method == "GET":
        refine_form = SchemaRefineForm({
            "columns": dynmodel.columns
        })
        return render(request, 'refine-and-import.html', {
            "form": refine_form,
            "dynmodel": dynmodel,
        })
    elif  request.method == "POST":
        refine_form = SchemaRefineForm(request.POST)
        if not refine_form.is_valid():
            return render(request, 'refine-and-import.html', {
                "form": refine_form,
                "dynmodel": dynmodel,
            })

        columns = refine_form.cleaned_data["columns"]
        dynmodel.columns = columns

        # CSV File Upload (update)
        csv_file = request.FILES.get("csv_file_upload")

        errors = None
        try:
            max_import_records = None
            if hasattr(settings, "MAX_IMPORT_RECORDS"):
                max_import_records = settings.MAX_IMPORT_RECORDS
            # Alter the DB
            dynmodel.save()
            dynmodel.refresh_from_db()
            errors = dynmodel.import_data(
                max_import_records=max_import_records,
                csv_file=csv_file,
            )
        except Exception as e:
            if not isinstance(e, GenericCSVError):
                raise e
            # if we have one of these errors, it's most likely
            # due to a change in the data source (credentials
            # revoked, URL unshared, etc)
            return render(request, 'refine-and-import.html', {
                "error_message": e.render(),
                "form": refine_form,
                "dynmodel": dynmodel,
            })

        if errors:
            logger.error("Import errors: %s" % errors)
            return render(request, 'refine-and-import.html', {
                "form": refine_form,
                "dynmodel": dynmodel,
                "errors": errors,
            })

        # this will re-run the admin setup and build up
        # the related fields properly
        logger.info("Doing post-import, re-setup save for admin...")
        dynmodel.save()

        next = get_setting("CSV_MODELS_WIZARD_REDIRECT_TO")
        if next:
            return redirect(next)

        return render(request, "import-complete.html", {
            "dynmodel": dynmodel,
            "n_records": Model.objects.count(),
        })


@login_required
def refine_and_import_by_name(request, name):
    dynmodel = get_object_or_404(models.DynamicModel, name=name)
    return refine_and_import(request, dynmodel.id)


@login_required
def import_data(request, id):
    """

    NOTE: We do the import as a POST as a security precaution. The
    GET phase isn't really necessary, so the page just POSTs the
    form automatically via JS on load.
    """

    dynmodel = get_object_or_404(models.DynamicModel, id=id)
    if request.method == "GET":
        return render(request, 'import-data.html', {
            "dynmodel": dynmodel
        })
    elif request.method == "POST":
        Model = dynmodel.get_model()

