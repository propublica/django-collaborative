from django.template.loader import render_to_string, get_template
from django.utils.translation import gettext_lazy as _


class GenericCSVError(Exception):
    def render(self):
        return render_to_string(self.TEMPLATE, {
            "message": self.MESSAGE,
        })


class RenderableErrorBase(GenericCSVError):
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


class BadCSVError(GenericCSVError):
    MESSAGE = _(
        "We can't find a valid CSV from the URL provided. "
        "If this is a Google Sheet, make sure you copied the share "
        "link. If it's a private sheet, make sure you used the private "
        "sheet checkbox and have uploaded a credential file. Otherwise, "
        "make sure there are no typos or errors in your URL."
    )
    TEMPLATE = "django_models_from_csv/exceptions/generic_error.html"

class NoPrivateSheetCredentialsError(GenericCSVError):
    MESSAGE = _(
        "We couldn't find any private Google sheet credentials saved. "
        "If you intended to import a private sheet, please make sure you "
        "went through the instructions for getting credentials and upload "
        "them upon import. If you need to re-upload credentials, you "
        "can do so via the 'Configure Google Credentials' link at the "
        "top of the Collaborate dashboard."

    )
    TEMPLATE = "django_models_from_csv/exceptions/generic_error.html"

