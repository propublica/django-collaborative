from django.conf import settings


def get_setting(name, default=None):
    return getattr(settings, name, default)
