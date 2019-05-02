import os

from django.test import TestCase

from django.conf import settings
from django_models_from_csv.commands.csvsql import run_csvsql


class CSVSQLTestCase(TestCase):
    def setUp(self):
        path = os.path.join(
            settings.BASE_DIR,
            "django_models_from_csv/test/data/test_form_response.csv"
        )
        with open(path, "r") as f:
            self.sheet = f.read()

    def test_can_generate_sql_from_csv(self):
        create_string = run_csvsql(self.sheet)
        print("Got create_string: %s" % create_string)
        self.assertTrue("CREATE TABLE" in create_string)
