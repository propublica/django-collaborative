from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from django_models_from_csv.forms import SchemaRefineForm
from django_models_from_csv.utils.importing import import_records
from django_models_from_csv import models


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
        return render(request, 'setup-import.html', {
            "sheet": dynmodel
        })
    elif request.method == "POST":
        next = request.GET.get('next')
        csv_url = dynmodel.csv_url
        Model = getattr(models, dynmodel.name)
        csv = fetch_csv(csv_url)
        errors = import_records(csv, Model, dynmodel)
        if errors:
            return render(request, 'setup-import.html', {
                "errors": errors,
                "sheet": sheet,
            })
        if next:
            return redirect(next)
        # TODO: implment this
        return render(request, "import-complete.html", {
            "dynmodel": dynmodel,
            "n_records": Model.objects.count(),
        })


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
        return render(request, 'setup-refine-schema.html', {
            "form": refine_form,
            "sheet": dynmodel,
        })
    elif  request.method == "POST":
        refine_form = SchemaRefineForm(request.POST)
        if not refine_form.is_valid():
            return render(request, 'setup-refine-schema.html', {
                "form": refine_form,
                "sheet": dynmodel,
            })

        columns = refine_form.cleaned_data["columns"]
        dynmodel.columns = columns
        dynmodel.save()
        url = reverse("setup-wait")
        next = reverse("import-data", args=[dynmodel.id])
        to = "%s?next=%s&token=%s" % (url, next, dynmodel.token)
        return redirect(to)


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
        sheet_count = models.DynamicModel.objects.count()
        if sheet_count and sheet_count > 0:
            return redirect('/admin/')
        return render(request, 'setup-begin.html', {})
    elif  request.method == "POST":
        # get params from request
        name = request.POST.get("name")
        csv_url = request.POST.get("csv_url")
        sheet = from_csv_url(name, csv_url)
        return redirect('refine-schema', sheet.id)
