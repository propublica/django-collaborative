from collaborative.models import (
    Spreadsheet, create_model_attrs, create_models
)

from django.db import models
from django.test import TestCase


class ModelDynamicCreationTestCase(TestCase):
    def setUp(self):
        self.sheet = Spreadsheet.objects.create(
            name="SomeGoogleSheet",
            columns=[{
                "name": "name",
                "type": "text",
                "original_name": "Enter your name",
            },{
                "name": "when",
                "type": "datetime",
                "original_name": "When did this happen",
            }]
        )

    def test_columns_is_object(self):
        self.assertTrue(isinstance(self.sheet.columns, list))

    def test_can_convert_sheet_object_to_attrs(self):
        attrs = create_model_attrs(self.sheet)
        self.assertTrue(isinstance(attrs, dict))

    def test_attrs_have_required_model_attributes(self):
        attrs = create_model_attrs(self.sheet)
        self.assertTrue(attrs.get("__module__"))
        self.assertTrue(attrs.get("HEADERS_LOOKUP"))
        self.assertEqual(len(attrs.keys()), 4)

    def test_can_build_model_from_sheet_object(self):
        create_models()
        from collaborative import models
        SomeGoogleSheet = getattr(models, "SomeGoogleSheet")
        self.assertTrue(SomeGoogleSheet is not None)
        self.assertTrue(SomeGoogleSheet.name is not None)
        self.assertTrue(SomeGoogleSheet.when is not None)
        self.assertEqual(
            SomeGoogleSheet.HEADERS_LOOKUP["Enter your name"],
            self.sheet.columns[0]["name"]
        )
        self.assertEqual(
            SomeGoogleSheet.HEADERS_LOOKUP["When did this happen"],
            self.sheet.columns[1]["name"]
        )
