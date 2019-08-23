import re

from django import template
from django.contrib.admin.templatetags.admin_list import admin_actions
from django.contrib.admin.templatetags.base import InclusionAdminNode


register = template.Library()


@register.tag(name='taggable_admin_actions')
def admin_actions_tag(parser, token):
    return InclusionAdminNode(
        parser, token, func=admin_actions,
        template_name='taggable_actions.html'
    )
