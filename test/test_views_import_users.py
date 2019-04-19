from django.test import TestCase

from collaborative.models import Spreadsheet
from collaborative.views.setup import (
    import_users, import_users_list
)


class ImportUsersTestCase(TestCase):
    def setUp(self):
        self.csv = """timestamp,question one,checkbox
11903923302,response 1,1
29803243893,another response,0
"""
        self.sheet = Spreadsheet.objects.create(
            name = "ImportUsersSheet",
            share_url = "fake.url/to/sheet",
            columns = []
        )

    def tearDown(self):
        self.sheet.delete()

    def test_can_transform_to_objects(self):
        data = import_users_list(self.csv, self.sheet)
        self.assertEqual(len(data), 2)

    def test_users_data_has_id_added(self):
        row = import_users_list(self.csv, self.sheet)[0]
        self.assertEqual(row[0], 1)
