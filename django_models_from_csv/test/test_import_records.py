from django.test import TestCase

from django_models_from_csv.models import DynamicModel
from django_models_from_csv.utils.importing import (
    import_records, import_records_list
)


class ImportRecordsTestCase(TestCase):
    def setUp(self):
        self.csv = """timestamp,question one,checkbox
11903923302,response 1,1
29803243893,another response,0
"""
        self.date_csv = """when,where
2019-04-23 15:06:51 UTC,seattle
"""
        self.sheet = DynamicModel.objects.create(
            name = "ImportRecordsSheet",
            csv_url = "fake.url/to/sheet",
            columns = []
        )
        self.sheet_w_date = DynamicModel.objects.create(
            name = "ImportRecordsDateSheet",
            csv_url = "fake.url/to/sheet",
            columns = [{
                "name": "when",
                "type": "datetime",
            },{
                "name": "where",
                "type": "short-text",
            }]
        )

    def tearDown(self):
        self.sheet.delete()

    def test_can_transform_to_objects(self):
        data = import_records_list(self.csv, self.sheet)
        self.assertEqual(len(data), 2)

    def test_records_data_has_id_added(self):
        row = import_records_list(self.csv, self.sheet)[0]
        self.assertEqual(row[0], 1)

    def test_records_date_fields_standardized(self):
        row = import_records_list(self.date_csv, self.sheet_w_date)[0]
        parsed_date = row[1]
        self.assertTrue("UTC" not in parsed_date)
