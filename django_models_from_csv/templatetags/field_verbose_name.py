import re

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def verbose_name(value):
    """
    Removes all values of arg from the given string
    """
    return re.sub(r"\s*\(ID:\s*[a-z0-9]+\)$", "", value)
