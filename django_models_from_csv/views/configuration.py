import logging
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from tablib.core import UnsupportedFormat
from requests.exceptions import ConnectionError

from django_models_from_csv import models
from django_models_from_csv.exceptions import (
    UniqueColumnError, DataSourceExistsError
)
from django_models_from_csv.forms import SchemaRefineForm
from django_models_from_csv.utils.common import get_setting, slugify
from django_models_from_csv.utils.csv import fetch_csv
from django_models_from_csv.utils.dynmodel import (
    from_csv_url, from_screendoor, from_private_sheet,
    from_csv_file,
)


logger = logging.getLogger(__name__)


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
        if addnew:
            return render(request, 'begin.html', {})
        elif models_count:
            return redirect('/admin/')
        return render(request, 'begin.html', {})
    elif  request.method == "POST":
        # For CSV URL/Google Sheets (public)
        csv_url = request.POST.get("csv_url")
        # Private Google Sheet (Service Account Credentials JSON)
        csv_google_sheets_credentials_file = request.FILES.get(
            "csv_google_sheets_credentials"
        )

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
            "csv_google_sheets_auth_code": csv_google_sheets_auth_code,
            "sd_name": request.POST.get("sd_name"),
            "sd_api_key": sd_api_key,
            "sd_project_id": sd_project_id,
            "sd_form_id": sd_form_id,
        }
        try:
            if csv_url and csv_google_sheets_credentials_file:
                name = slugify(request.POST.get("csv_name"))
                dynmodel = from_private_sheet(
                    name, csv_url,
                    credentials=csv_google_sheets_credentials_file,
                )
            elif csv_url:
                name = slugify(request.POST.get("csv_name"))
                dynmodel = from_csv_url(
                    name, csv_url,
                    csv_google_sheets_auth_code=csv_google_sheets_auth_code
                )
            elif sd_api_key:
                name = slugify(request.POST.get("sd_name"))
                dynmodel = from_screendoor(
                    name,
                    sd_api_key,
                    int(sd_project_id),
                    form_id=int(sd_form_id) if sd_form_id else None
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

        except (UniqueColumnError, DataSourceExistsError) as e:
            return render(request, 'begin.html', {
                "errors": e.render(),
                **context
            })
        # handles valid URLs to non-CSV data and also just bad URLs
        except UnsupportedFormat as e:
            err_msg = _(
                "Invalid data source. Please make sure you "
                "linked to a valid CSV data source."
            )
            return render(request, 'begin.html', {
                "errors": err_msg,
                **context
            })
        except ConnectionError as e:
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
        # Alter the DB
        dynmodel.save()
        dynmodel.refresh_from_db()

        errors = dynmodel.import_data()
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

