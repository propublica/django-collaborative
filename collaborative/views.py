from django.shortcuts import render
from django.urls import reverse


def begin_setup(request):
    """
    Entry point for setting up the rest of the system. At this point
    the user has logged in using the default login and are now getting
    ready to configure the database, schema (via Google sheets URL) and
    any authentication backends (Google Oauth2, Slack, etc).
    """
    return render(request, 'begin-setup.html', {})


def request_access(request):
    """
    This endpoint alerts the user that an admin hasn't created a
    user with the email they used with social auth. This also gives
    them a link they can use to resume the login once an admin has
    done this.
    """
    partial_token = request.GET.get('partial_token')
    backend = request.GET.get('backend')
    url = '{0}?partial_token={1}'.format(
        reverse('social:complete', args=(backend,)),
        partial_token
    )
    args = {
        "resume_url": request.build_absolute_uri(url)
    }
    return render(request, 'request-access.html', args)
