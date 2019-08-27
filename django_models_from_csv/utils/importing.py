import importlib
import logging

from dateutil import parser as dt_parser
from django.conf import settings
from import_export.resources import (
    ModelResource, ModelDeclarativeMetaclass,
)
from tablib import Dataset

from django_models_from_csv import models
from django_models_from_csv.utils.csv import fetch_csv


logger = logging.getLogger(__name__)


def modelresource_factory(model, resource_class=ModelResource, extra_attrs=None):
    """
    Factory for creating ``ModelResource`` class for given Django model.
    """
    attrs = {
        'model': model,
        "skip_unchanged": True,
        "report_skipped": True,
    }
    if extra_attrs:
        attrs.update(extra_attrs)

    Meta = type(str('Meta'), (object,), attrs)

    class_name = model.__name__ + 'Resource'

    class_attrs = {
        'Meta': Meta,
    }

    metaclass = ModelDeclarativeMetaclass
    return metaclass(class_name, (resource_class,), class_attrs)


def import_records_list(csv, dynmodel):
    """
    Take a fetched CSV and turn it into a tablib Dataset, with
    a row ID column and all headers translated to model field names.
    """
    data = Dataset().load(csv, format="csv")
    # add an ID column matching the row number
    if dynmodel.csv_url or dynmodel.csv_file:
        data.insert_col(0, col=[i+1 for i in range(len(data))], header="id")
    # # screendoor: use the builtin ID field
    # elif dynmodel.csv_url:
    #     # data.insert_col(0, col=[i+1 for i in range(len(data))], header="id")

    # Turn our CSV columns into model columns
    for i in range(len(data.headers)):
        header = data.headers[i]
        model_header = dynmodel.csv_header_to_model_header(header)
        if model_header and header != model_header:
            data.headers[i] = model_header

    datetime_ixs = []
    date_ixs = []
    for c in dynmodel.columns:
        c_type = c.get("type")
        type_ixs = None
        if c_type and c_type == "datetime":
            type_ixs = datetime_ixs
        elif c_type and c_type == "date":
            type_ixs = date_ixs
        else:
            continue

        name = c["name"]
        try:
            ix = data.headers.index(name)
        except ValueError:
            # Possibly a new column not in dynamic model description, ignore
            continue
        type_ixs.append(ix)

    newdata = Dataset(headers=data.headers)
    for row in data:
        newrow = []
        for i in range(len(row)):
            val = row[i]
            if i in datetime_ixs:
                if not val:
                    newrow.append(None)
                    continue
                try:
                    val = dt_parser.parse(val).strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    logger.error("Error parsing datetime: %s" % e)
                    newrow.append(None)
                    continue
            elif i in date_ixs:
                if not val:
                    newrow.append(None)
                    continue
                try:
                    val = dt_parser.parse(val).strftime("%Y-%m-%d")
                except Exception as e:
                    logger.error("Error parsing date: %s" % e)
                    newrow.append(None)
                    continue
            newrow.append(val)
        newdata.append(newrow)
    return newdata


def import_records(csv, Model, dynmodel):
    """
    Take a fetched CSV, parse it into user rows for
    insertion and attempt to import the data into the
    specified model.

    This performs a pre-import routine which will return
    failure information we can display and let the user fix
    the dynmodel before trying again. On success this function
    returns None.

    TODO: Only show N number of errors. If there are more,
    tell the user more errors have been supressed and to
    fix the ones listed before continuing. We don't want
    to overwhelm the user with error messages.
    """
    dataset = import_records_list(csv, dynmodel)
    column_names = [c.get("name") for c in dynmodel.columns]
    logger.debug("Column names: %s" % str(column_names))
    logger.debug("Dataset: %s" % dataset)

    # Do headers check
    errors = []
    for row in dataset.dict:
        for pipeline in getattr(settings, "DATA_PIPELINE", []):
            module = importlib.import_module(pipeline)
            module.run(row)

        logger.debug("Importing: %s" % str(row))
        # 1. check fields, any extra fields are thrown out?
        #    or is this done above?
        # 2. get or create by ID
        obj = None
        try:
            obj = Model.objects.get(pk=row["id"])
        except Model.DoesNotExist:
            pass

        logger.debug("Found object? %s" % obj)

        # update all fieds found in our model columns, but
        # leave out the id field (already attached to obj above)
        if obj is not None:
            for field in row.keys():
                if field == "id" or field not in column_names:
                    continue
                # logger.debug("updating field=%s value=%s" % (field, row[field]))
                setattr(obj, field, row[field])
            try:
                obj.save()
            except Exception as e:
                logger.error("Error updating: %s" % str(e))
                errors.append("Row: %s, Error updating: %s" % (
                    obj.id, e
                ))
                continue

        # create new using similar strategy, but we went
        # to include the id field
        else:
            obj_data = {}
            for field in row.keys():
                if field != "id" and field not in column_names:
                    continue
                # logger.debug("creating field=%s value=%s" % (field, row[field]))
                obj_data[field] = row[field]

            try:
                obj = Model.objects.create(**obj_data)
                obj.save()
            except Exception as e:
                logger.error("Error creating: %s" % str(e))
                errors.append("Row: %s, Error creating: %s" % (
                    obj_data.get("id"), e
                ))
                continue

    return errors
