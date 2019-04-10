import os

from django.test import TestCase

from collaborative.settings import BASE_DIR
from collaborative.views.setup import sheet_to_sql_create


class CSVSQLTestCase(TestCase):
    def setUp(self):
        path = os.path.join(BASE_DIR, "test/data/test_form_response.csv")
        with open(path, "r") as f:
            self.sheet = f.read()

    def test_can_generate_sql_from_csv(self):
        create_string = sheet_to_sql_create(self.sheet)
        print("Got create_string: %s" % create_string)
        self.assertTrue("CREATE TABLE" in create_string)
