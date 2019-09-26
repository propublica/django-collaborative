import json
import re

from django.conf import settings
from django.shortcuts import HttpResponse
from django.utils.text import slugify as og_slugify


def get_setting(name, default=None):
    return getattr(settings, name, default)


def slugify(name):
    """
    Does the same as django's slugify, but replaces dash with underscore.
    We do this because deleting a table doesn't like table names with
    dashes.

    NOTE: It's important that this routine is synced with the one we
    have running in the widget UI choices formatter publish method:

    file: django_models_from_csv/static/django_models_from_csv/columnswidget.js
    function: rivets.formatters.choices:publish
    """
    return re.sub('-', '_', og_slugify(name)).lower()


def http_response(data, code=200):
    return HttpResponse(
        json.dumps(data), status=code,
        content_type="application/json",
    )
