import json

from django import forms
from django.conf import settings
from jsonfield.widgets import JSONWidget

try:
    from django.utils import six
except ImportError:
    import six

from django_models_from_csv import models


class ColumnsWidget(JSONWidget):
    template_name = 'forms/widget/columnswidget.html'

    class Media:
        extra = '' if settings.DEBUG else '.min'
        js = (
            'admin/js/vendor/jquery/jquery%s.js' % extra,
            'admin/js/jquery.init.js',
            'admin/js/core.js',
        )

    def __init__(self, column_types, *args, **kwargs):
        self.COLUMN_TYPES = column_types
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = {}
        attrs = self.build_attrs(self.attrs, attrs)
        columns = json.loads(value)
        indexed_columns = []
        for i in range(len(columns)):
            indexed_columns.append({
                "ix": i,
                **columns[i]
            })
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value_obj': indexed_columns,
            'value': json.dumps(indexed_columns, indent=2),
            'column_types': self.COLUMN_TYPES,
            'attrs': attrs,
            'template_name': self.template_name,
            'media': self.media
        }

        # look for redactor credentials
        dlp_cred = models.CredentialStore.objects.filter(
            name="google_dlp_credentials"
        ).first()
        if dlp_cred:
            context["dlp_credentials_exist"] = True
        return context


class MetaWidget(ColumnsWidget):
    template_name = 'forms/widget/metawidget.html'

    def get_context(self, name, value, attrs):
        context = {}
        attrs = self.build_attrs(self.attrs, attrs)
        columns = json.loads(value)
        indexed_columns = []
        for i in range(len(columns)):
            indexed_columns.append({
                "ix": i,
                **columns[i]
            })
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value_obj': indexed_columns,
            'value': json.dumps(indexed_columns, indent=2),
            'column_types': self.COLUMN_TYPES,
            'attrs': attrs,
            'template_name': self.template_name,
            'media': self.media
        }
        return context
