from django.template.loader import render_to_string, get_template
from django.utils.translation import gettext_lazy as _


class RenderableErrorBase(Exception):
    def __init__(self, name):
        self.name = name
        self.msg = self.MESSAGE % (self.name)
        super().__init__(self.msg)

    def render(self):
        return render_to_string(self.TEMPLATE, {
            "name": self.name
        })


class UniqueColumnError(RenderableErrorBase):
    """
    Thrown when, while import, we encounter a duplicate column
    header.
    """
    MESSAGE = _(
        "Duplicate header column '%s' found. Please rename "
        "the column in your source spreadsheet and continue "
        "again, below."
    )
    TEMPLATE = "django_models_from_csv/exceptions/unique_column_error.html"


class DataSourceExistsError(RenderableErrorBase):
    """
    Thrown when a user attempts to re-create an already existing
    data source (by name).
    """
    MESSAGE = _(
        "Data source '%s' already exists. Please choose "
        "another name or re-import the existing data source "
        "from the administration panel."
    )
    TEMPLATE = "django_models_from_csv/exceptions/unique_name_error.html"
