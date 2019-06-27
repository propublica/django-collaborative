from django.db import connection
from django.test import SimpleTestCase

from django_models_from_csv.models import DynamicModel
from django_models_from_csv.utils.importing import (
    import_records, import_records_list
)


class ImportRecordsTestCase(SimpleTestCase):
    databases = '__all__'

    def setUp(self):
        self.csv = """timestamp,question one,checkbox
11903923302,response 1,1
29803243893,another response,0
"""
        self.date_csv = """when,where
2019-04-23 15:06:51 UTC,seattle
4/23/2019 3:06pm PST,olympia
"""
        self.date_csv = """when,where
2019-04-23 15:06:51 UTC,seattle2
4/23/2019 3:06pm PST,olympia2
"""
        self.sheet = DynamicModel.objects.create(
            name = "ImportRecordsSheet",
            csv_url = "fake.url/to/sheet",
            columns = [{
                "name": "when",
                "type": "datetime",
            }, {
                "name": "where",
                "type": "text",
            }]
        )
        self.sheet.save()
        self.sheet_w_date = DynamicModel.objects.create(
            name = "ImportRecordsDateSheet",
            csv_url = "fake.url/to/sheet",
            columns = [{
                "name": "when",
                "type": "datetime",
            },{
                "name": "where",
                "type": "short-text",
                "attrs": {
                    "max_length": 50
                }
            }]
        )
        # index of date col for tests
        self.date_col = 1
        self.sheet_w_date.save()

    def tearDown(self):
        self.sheet.get_model().objects.all().delete()
        self.sheet.delete()
        self.sheet_w_date.get_model().objects.all().delete()
        self.sheet_w_date.delete()

    def test_can_transform_to_objects(self):
        data = import_records_list(self.csv, self.sheet)
        self.assertEqual(len(data), 2)

    def test_records_data_has_id_added(self):
        row = import_records_list(self.csv, self.sheet)[0]
        self.assertEqual(row[0], 1)

    def test_records_date_fields_standardized(self):
        rows = import_records_list(self.date_csv, self.sheet_w_date)
        self.assertTrue("UTC" not in rows[0][self.date_col])
        self.assertTrue("2019-04-23 15:06" in rows[0][self.date_col])
        self.assertTrue("2019-04-23 15:06" in rows[1][self.date_col])

    def test_can_perform_successful_import(self):
        Model = self.sheet.get_model()
        errors = import_records(
            self.date_csv, Model, self.sheet
        )
        self.assertTrue(errors is None)
        self.assertEqual(Model.objects.count(), 2)

    def test_can_return_import_errors(self):
        # this CSV doesn't match the model's columns. will return
        # errors about blank required fields (when)
        errors = import_records(
            self.csv, self.sheet.get_model(), self.sheet
        )
        self.assertTrue(errors)

    def test_can_perform_successful_reimport_update(self):
        Model = self.sheet.get_model()
        errors = import_records(
            self.date_csv, Model, self.sheet
        )
        self.assertTrue(errors is None)
        self.assertEqual(Model.objects.count(), 2)
        errors = import_records(
            self.date_csv, Model, self.sheet
        )
        self.assertTrue(errors is None)
        objects = Model.objects.all()
        self.assertEqual(len(objects), 2)
        self.assertTrue(objects[0].where.endswith("2"))
        self.assertTrue(objects[1].where.endswith("2"))
