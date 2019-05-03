from django.test import TestCase

from django_models_from_csv.models import (
    DynamicModel, create_model_attrs, create_models
)


class ModelDynamicCreationTestCase(TestCase):
    def setUp(self):
        self.dynmodel = DynamicModel.objects.create(
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
        self.assertTrue(isinstance(self.dynmodel.columns, list))

    def test_can_convert_dynmodel_object_to_attrs(self):
        attrs = create_model_attrs(self.dynmodel)
        self.assertTrue(isinstance(attrs, dict))

    def test_attrs_have_required_model_attributes(self):
        attrs = create_model_attrs(self.dynmodel)
        self.assertTrue(attrs.get("__module__"))
        self.assertTrue(attrs.get("HEADERS_LOOKUP"))
        self.assertGreaterEqual(len(attrs.keys()), 4)

    def test_can_build_model_from_dynmodel_object(self):
        create_models()
        from django_models_from_csv import models
        SomeGoogleSheet = getattr(models, "SomeGoogleSheet")
        self.assertTrue(SomeGoogleSheet is not None)
        self.assertTrue(SomeGoogleSheet.name is not None)
        self.assertTrue(SomeGoogleSheet.when is not None)
        self.assertEqual(
            SomeGoogleSheet.HEADERS_LOOKUP["Enter your name"],
            self.dynmodel.columns[0]["name"]
        )
        self.assertEqual(
            SomeGoogleSheet.HEADERS_LOOKUP["When did this happen"],
            self.dynmodel.columns[1]["name"]
        )
