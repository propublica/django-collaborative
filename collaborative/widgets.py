import json

import django
from jsonfield.widgets import JSONWidget

try:
    from django.utils import six
except ImportError:
    import six


class ColumnsWidget(JSONWidget):
    template_name = 'forms/widget/columnswidget.html'

    def __init__(self, column_types, *args, **kwargs):
        self.COLUMN_TYPES = column_types
        super(ColumnsWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = {}
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value_obj': json.loads(value),
            'value': value,
            'column_types': self.COLUMN_TYPES,
            'attrs': self.build_attrs(self.attrs, attrs),
            'template_name': self.template_name,
        }
        return context
