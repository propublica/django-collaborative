from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django_models_from_csv import models
from django_models_from_csv.forms import SchemaRefineForm
from django_models_from_csv.utils.common import get_setting
from django_models_from_csv.utils.csv import fetch_csv
from django_models_from_csv.utils.importing import import_records
from django_models_from_csv.utils.dynmodel import from_csv_url


@login_required
def begin(request):
    """
    Entry point for setting up the rest of the system. At this point
    the user has logged in using the default login and are now getting
    ready to configure the database, schema (via Google sheets URL) and
    any authentication backends (Google Oauth2, Slack, etc).
    """
    if request.method == "GET":
        # # Don't go back into this flow if we've already done it
        # models_count = models.DynamicModel.objects.count()
        # if models_count:
        #     return redirect('/admin/')
        return render(request, 'begin.html', {})
    elif  request.method == "POST":
        # get params from request
        name = request.POST.get("name")
        csv_url = request.POST.get("csv_url")
        dynmodel = from_csv_url(name, csv_url)
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
        print("Redirecting to", to)
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
        csv_url = dynmodel.csv_url
        Model = getattr(models, dynmodel.name)
        csv = fetch_csv(csv_url)
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
