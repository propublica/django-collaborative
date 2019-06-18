from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django_models_from_csv import models
from django_models_from_csv.forms import SchemaRefineForm
from django_models_from_csv.utils.common import get_setting
from django_models_from_csv.utils.csv import fetch_csv
from django_models_from_csv.utils.importing import import_records
from django_models_from_csv.utils.dynmodel import (
    from_csv_url, from_screendoor, from_private_sheet
)
from django_models_from_csv.utils.screendoor import ScreendoorImporter
from django_models_from_csv.utils.google_sheets import (
   GoogleOAuth, PrivateSheetImporter
)


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
        # get params from request
        csv_url = request.POST.get("csv_url")
        csv_google_sheets_auth_code = request.POST.get(
            "csv_google_sheets_auth_code"
        )
        sd_api_key = request.POST.get("sd_api_key")
        sd_project_id = request.POST.get("sd_project_id")
        sd_form_id = request.POST.get("sd_form_id")
        if csv_url and csv_google_sheets_auth_code:
            name = request.POST.get("csv_name")
            dynmodel = from_private_sheet(
                name, csv_url, auth_code=csv_google_sheets_auth_code,
            )
        elif csv_url:
            name = request.POST.get("csv_name")
            dynmodel = from_csv_url(
                name, csv_url,
                csv_google_sheets_auth_code=csv_google_sheets_auth_code
            )
        elif sd_api_key:
            name = request.POST.get("sd_name")
            dynmodel = from_screendoor(
                name,
                sd_api_key,
                int(sd_project_id),
                form_id=int(sd_form_id) if sd_form_id else None
            )
        return redirect('csv_models:refine-schema', dynmodel.id)


@login_required
def refine_schema(request, id):
    """
    Allow the user to modify the auto-generated column types and
    names. This is done before we import the dynmodel data.
    """
    dynmodel = get_object_or_404(models.DynamicModel, id=id)
    if request.method == "GET":
        refine_form = SchemaRefineForm({
            "columns": dynmodel.columns
        })
        return render(request, 'refine-schema.html', {
            "form": refine_form,
            "dynmodel": dynmodel,
        })
    elif  request.method == "POST":
        refine_form = SchemaRefineForm(request.POST)
        if not refine_form.is_valid():
            return render(request, 'refine-schema.html', {
                "form": refine_form,
                "dynmodel": dynmodel,
            })

        columns = refine_form.cleaned_data["columns"]
        dynmodel.columns = columns
        dynmodel.save()
        url = reverse("csv_models:wait")
        next = reverse("csv_models:import-data", args=[dynmodel.id])
        # Security: make sure this is never None
        if not dynmodel.token:
            dynmodel.token = dynmodel.make_token()
            dynmodel.save()
        to = "%s?next=%s&token=%s" % (url, next, dynmodel.token)
        return redirect(to)


@login_required
def import_data(request, id):
    """
    Loads the rows found in the dynmodel into the database. This is
    done once the user has had a chance to change the column names
    and types. On success, this redirects to the URL specified by
    the `next` query parameter.

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
        next = get_setting("CSV_MODELS_WIZARD_REDIRECT_TO")
        Model = dynmodel.get_model()
        # TODO: move all these into methods of dynmodel
        if dynmodel.csv_url and dynmodel.csv_google_refresh_token:
            oauther = GoogleOAuth(
                get_setting("GOOGLE_CLIENT_ID"),
                get_setting("GOOGLE_CLIENT_SECRET")
            )
            access_data = oauther.get_access_data(
                refresh_token=dynmodel.csv_google_refresh_token
            )
            token = access_data["access_token"]
            csv = PrivateSheetImporter(token).get_csv_from_url(
                dynmodel.csv_url
            )
        elif dynmodel.csv_url:
            csv = fetch_csv(dynmodel.csv_url)
        elif dynmodel.sd_api_key:
            importer = ScreendoorImporter(api_key=dynmodel.sd_api_key)
            csv = importer.build_csv(
                dynmodel.sd_project_id, form_id=dynmodel.sd_form_id
            )
        else:
            raise NotImplementedError("Invalid data source for %s" % dynmodel)
        errors = import_records(csv, Model, dynmodel)
        if errors:
            return render(request, 'import-data.html', {
                "errors": errors,
                "dynmodel": dynmodel,
            })
        if next:
            return redirect(next)
        # TODO: implment this
        return render(request, "import-complete.html", {
            "dynmodel": dynmodel,
            "n_records": Model.objects.count(),
        })
