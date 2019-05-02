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
        self.sheet = DynamicModel.objects.create(
            name = "ImportRecordsSheet",
            csv_url = "fake.url/to/sheet",
            columns = []
        )

    def tearDown(self):
        self.sheet.delete()

    def test_can_transform_to_objects(self):
        data = import_records_list(self.csv, self.sheet)
        self.assertEqual(len(data), 2)

    def test_records_data_has_id_added(self):
        row = import_records_list(self.csv, self.sheet)[0]
        self.assertEqual(row[0], 1)
