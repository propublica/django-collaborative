import re
import requests

from django.contrib.auth.models import User

from django_models_from_csv.utils.common import get_setting
from django_models_from_csv.commands.manage_py import run_inspectdb
from django_models_from_csv.models import DynamicModel, TYPE_TO_FIELDNAME


def fix_models_py(models_py):
    """
    The output of inspectdb is pretty messy, so here we trim down
    some of the mess, add mandatory ID field and fix the bad
    conversion to CharField (we use TextField instead).
    """
    lines = models_py.split("\n")
    fixed_lines = []
    for line in lines:
        # Postgres TextFields are preferable. No performance
        # hit compared to CharField and we don't need to
        # specify a max length
        line = line.replace(
            "CharField", "TextField"
        )

        # Strip out comments. They're super long and repetitive
        try:
            comment_ix = line.index("#")
        except ValueError as e:
            comment_ix = -1
        if comment_ix == 0:
            continue
        elif comment_ix != -1:
            line = line[0:comment_ix]

        # Skip the managed part. We're going to actually
        # use a managed model, derived from the auto-generated
        # models.py
        if "class Meta:" in line:
            continue
        elif "managed = False" in line:
            continue
        elif "db_table = " in line:
            continue

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def extract_fields(models_py):
    """
    Take a models.py string and extract the lines that
    declare model fields into a dictionary of the following
    format:

        { "FIELD_NAME": "models.FieldType(arguments...)" }
    """
    fields = {}
    for line in models_py.split("\n"):
        # skip imports
        if re.match(".*from.*import.*", line):
            continue
        # skip class declarations
        if re.match(".*class\s+.*models\.Model.*", line):
            continue
        # extract field name
        field_matches = re.match("\s*([^\s\-=]+)\s*=\s*(.*)$", line)
        if not field_matches or not field_matches.groups():
            continue
        field, declaration = field_matches.groups()
        fields[field] = declaration
    return fields


def extract_field_declaration_args(declaration_str):
    """
    Extract the arguments (**kwargs) from a field declaration string.

    Returns a dict of the arguments.
    """
    matches = re.match(".*\((.*)\)", declaration_str)
    args_str = matches.groups()[0]
    indiv_args = re.split(",\s*", args_str)
    kw_arguments = {}
    for arg in indiv_args:
        key, value = arg.split("=", 1)
        kw_arguments[key] = eval(value)
    return kw_arguments


def extract_field_type(declaration_str):
    """
    Take a models.py declaration string, extract the field type class
    and match it to a name that we will show users for
    selecting column types.

    For example, we have this field declaration (as a string):

        name = models.CharField(max_length=100)

    This function will return "text".

    The point of this function is to make sure we're not directly loading
    django classes based on the user input and to help show users friendlier
    names for the different column types.
    """
    matches = re.match(".*(models\.[A-Za-z0-9_]+)\(", declaration_str)
    field_class_str = matches.groups()[0]
    # TODO: default here? or use default dict in TYPE_TO_FIELDNAME
    type_name = TYPE_TO_FIELDNAME[field_class_str]
    return type_name


# TODO: move this into DynamicModel.from_models_py(...)
def build_sheet_object(models_py, model_name, csv_url):
    """
    Convert a generated models.py document to a DynamicModel with
    the specified name and URL to a source CSV.
    """
    fields = extract_fields(models_py)
    columns = []
    for name, declaration in fields.items():
        kwargs = extract_field_declaration_args(declaration)
        field_type = extract_field_type(declaration)
        original_name = kwargs.pop("db_column")
        columns.append({
            "name": name,
            "original_name": original_name,
            "type": field_type,
            "attrs": kwargs,
        })
    sheet = DynamicModel(
        name = model_name,
        csv_url = csv_url,
        columns = columns,
        token = User.objects.make_random_password(length=16),
    )
    sheet.save()
    return sheet
