# -*- coding: utf-8 -*-
"""
# Examples for modifying metadata columns

This is a developer-friendly guide for changing the metadata and
contact log tables.

First some terminology: internally, we call all Collaborate-generated
models "dynamic models". All such models derive from the `DynamicModel`
class (found in `django_models_from_csv.models`).

Second: A `DynamicModel` object describes the schema of a particular
model. To get the data associated with this model, you can obtain the
actual model by calling `.get_model()` on the object.

For convenience, we will refer to all metadata and contact log models as
"meta" models.

While the main dynamic models are backed by the source data itself,
metadata fields are fully customizable.

Provided here are examples on how to do common tasks:

- create a new dynamic model
- alter choice field options
- change column data type
- adding a column to a model
- removing a column from a model

Currently, you need to restart the application server after applying any
one of these changes. This is a limitation that will be removed in
future versions of Collaborate.

Applying these methods to base imported models (CSV, Sheet, or
Screendoor-backed) is highly discouraged. Doing so can result in data
loss and other strange errors, as those base import models are managed
internally by Collaborate.
"""
__author__ = 'Brandon Roberts <brandon@bxroberts.org>'
__version__ = '1.0.0'

from django.db import connection
from django_models_from_csv.models import DynamicModel


# We're going to set our dynamic model type to this value so
# Collaborate's auto-admin builder will ignore it.  Since this is an
# example, it is fine. In practice your models will have a value from
# `collaborative.models.MODEL_TYPES`.
IGNORED_TYPE = -1


def create_dynmodel(name):
    """
    Create a simple example dynamic model with a text and choice field.
    """
    # some status choices for our example choice field.  we have
    # implemented this as an integer field, but you could easily build
    # this as a character field.
    # NOTE: If this is a tuple, we have to convert it to a list and then
    # overwrite it in the original model columns structure to get it to
    # 'take' upon save. Storing as list makes updates more straightforward.
    WEATHER_STATUSES = [
        [0, "Sunny"],
        [1, "Raining"],
        [2, "Snowing"],
        [3, "Didn't look"],
    ]

    return DynamicModel.objects.create(
        name=name,
        attrs={
            "type": IGNORED_TYPE,
        },
        # add a basic text field and a choice field here
        columns=[{
            "name": "place",
            "type": "text",
            "attrs": {
                # if you leave these out, `place` will be a required field
                "blank": True,
                "null": True,
            },
        }, {
            "name": "weather",
            "type": "integer",
            "attrs": {
                "choices": WEATHER_STATUSES,
                "default": WEATHER_STATUSES[0][0],
            },
        }],
    )


def updating_choice_column_option_names(dynmodel):
    """
    Update one of our choice field's options. In this example,
    we're going to change the last option from "Didn't look" to
    "Unsure".
    """
    print("Changing a choice column's options...")
    # Grab our weather column (by name). This avoids having
    # to iterate over the columns list manually.
    column = dynmodel.get_column("weather")
    weather_choices = column["attrs"]["choices"]

    # let's alter the last one's name
    weather_choices[-1][1] = "Unsure"
    column["attrs"]["choices"] = weather_choices
    # this applies the change to the database
    dynmodel.save()

    # Show the model as it is seen by django now (debug output)
    print("Checking for updated column choice field options...")
    for field in dynmodel.get_model()._meta.get_fields():
        print("Field", field)
        if field.name == "weather":
            print("Choices", field.choices)


def changing_column_datatype(dynmodel):
    """
    Shows how to alter the data type of an existing (text)
    field (to a number field).
    """
    print("Changing a column data type...")
    column = dynmodel.get_column("place")
    coltype = column["type"]

    # let's change it to a number (FloatField).
    coltype = "number"
    dynmodel.save()

    print("Checking for updated column data type...")
    for field in dynmodel.get_model()._meta.get_fields():
        print("Field", field)
        print("Data type", field.db_type)


def adding_new_column(dynmodel):
    """
    Shows how to add a new column to an existing model.
    """
    print("Adding a column...")
    new_column = {
        "name": "weather_person",
        "type": "text",
        "attrs": {
            "blank": True,
            "null": True,
        },
    }
    dynmodel.columns.append(new_column)
    dynmodel.save()

    print("Checking for newly added column...")
    for field in dynmodel.get_model()._meta.get_fields():
        print("Field", field)
        print("Data type", field.db_type)


def removing_a_column(dynmodel):
    """
    Shows how to remove a column from an existing model. This
    requires you to restart the application server for Django
    to 'see' the change.
    """
    print("Removing a column...")
    # find the index of the column and delete it
    for ix, c in enumerate(dynmodel.columns):
        if c["name"] == "place":
            print("Found 'place' column at index", ix)
            del dynmodel.columns[ix]
            break
    dynmodel.save()
    dynmodel.refresh_from_db()
    print("Restarting the server will finalize the removal.")


def main():
    """
    Entry point: run each one of our modification examples on a
    newly created dynamic model.
    """
    dynmodel = create_dynmodel("places_weather")
    updating_choice_column_option_names(dynmodel)
    changing_column_datatype(dynmodel)
    # TODO: fix meta add, it explodes for some reason here...
    # adding_new_column(dynmodel)
    removing_a_column(dynmodel)
    dynmodel.delete()


if __name__ == "__main__":
    main()
