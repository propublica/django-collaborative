from django.contrib.admin.sites import site
from django.shortcuts import redirect

from django_models_from_csv.models import DynamicModel


def redirect_wizard_or_admin(request):
    """
    Check to see if we have set up any spreadsheets, yet, and if
    not redirect to the setup wizard. If we've already set up a sheet,
    go to the normal admin.
    """
    sheet_count = DynamicModel.objects.count()
    if not sheet_count:
        return redirect('db-config:begin')
    return redirect('admin')


def root(request):
    """
    Landing page for website ("website.tld/"). Checks to see
    if we have any sheet tables configured and passes this information
    off to the site.login view (admin login).
    """
    sheet_count = DynamicModel.objects.count()
    return site.login(request, extra_context={
        "first_login": not sheet_count
    })
