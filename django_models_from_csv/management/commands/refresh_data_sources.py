#!/usr/bin/env python3
import logging

from django.core.management.base import BaseCommand, CommandError

from collaborative.models import MODEL_TYPES
from django_models_from_csv.models import DynamicModel


logger = logging.getLogger(__name__)
syslog = logging.StreamHandler()
logger.addHandler(syslog)
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    help = "Refresh CSV models from source data."

    def add_arguments(self, parser):
        parser.add_argument('--name', action='append', type=str)
        parser.add_argument('--pk', action='append', type=int)

    def get_dynmodel(self, name=None, pk=None):
        if name is not None:
            logger.info("Loading by name=%s" % (name))
            return DynamicModel.objects.get(name=name)
        elif pk is not None:
            logger.info("Loading by id=%s" % (pk))
            return DynamicModel.objects.get(pk=pk)

    def handle(self, *args, **options):
        logger.info("Loading models...")

        names = options.get("name") or []
        pks = options.get("pk") or []

        models = []
        for name in names:
            model = self.get_dynmodel(name=name)
            models.append(model)
        for pk in pks:
            model = self.get_dynmodel(pk=pk)
            models.append(model)

        if not names or not pks:
            models = DynamicModel.objects.all()

        for model in models:
            if model.attrs.get("type") != MODEL_TYPES.CSV:
                continue
            # model import has been failing, skip
            if model.attrs.get("dead")
                logger.info("Skipping failing import %s..." % (
                    model.name
                ))
                continue
            logger.info("Refreshing %s" % model)
            try:
            errors = model.import_data()
            if not errors:
                logger.info("Success!")
                continue

            # TODO: on error, use the user messages framework
            for error in errors:
                logger.error("Import error: %s" % (error))
