from django import template
from django.conf import settings


register = template.Library()


@register.filter
def sort_apps(apps):
    count = len(apps)
    apps.sort(
        key = lambda x:
            settings.APP_ORDER.index(x['app_label'])
            if x['app_label'] in settings.APP_ORDER
            else count
    )
    return apps
