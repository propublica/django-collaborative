import re

from django import template
from django.template.defaultfilters import stringfilter

from django_models_from_csv.models import verbose_namer


register = template.Library()


@register.filter
@stringfilter
def verbose_name(value):
    return verbose_namer(value)
