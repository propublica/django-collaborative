from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django_models_from_csv.models import DynamicModel, create_models


@csrf_exempt
def migrate(request):
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
    sheet = get_object_or_404(DynamicModel, token=token)
    sheet.token = None
    sheet.save()
    create_models()

    return HttpResponse(200, "OK")


@login_required
def wait(request):
    """
    This view triggers a makemigrations/migrate via JS and
    waits for the server to come back online. It then automatically
    redirects the user to the view specified in the "next" param.
    """
    next = request.GET["next"] # required
    token = request.GET["token"] # required
    sheet = get_object_or_404(DynamicModel, token=token)
    return render(request, 'wait.html', {
        "next": next,
        "token": token,
    })



