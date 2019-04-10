import re

from django.test import TestCase

from collaborative.views.setup import execute_sql, models_py_from_database


class SchemaBuildingTestCase(TestCase):
    databases = ["schemabuilding"]

    def setUp(self):
        self.table_name = "tmp4wlpvd0c"
        self.create_table = """
CREATE TABLE %s (
        "Timestamp" TIMESTAMP,
        "Question with short answer?" VARCHAR NOT NULL,
        "Question with long answer?" VARCHAR NOT NULL,
        "Checkbox?" VARCHAR NOT NULL,
        "Option with dropdown?" VARCHAR NOT NULL,
        "Multiple choice?" VARCHAR NOT NULL,
        " Numeric linear scale?" FLOAT NOT NULL,
        "Multiple choice grid? [row1]" VARCHAR NOT NULL,
        "Multiple choice grid? [row2]" VARCHAR NOT NULL,
        "Checkbox grid? [row1]" VARCHAR NOT NULL,
        "Checkbox grid? [row2]" VARCHAR NOT NULL,
        "What date?" DATE NOT NULL,
        "What time?" VARCHAR NOT NULL
);
""" % self.table_name

    def test_can_execute_sql_against_secondary_db(self):
        result = execute_sql(self.create_table)
        self.assertIs(result, None)

    def test_can_run_inspectdb_against_secondary_db(self):
        execute_sql(self.create_table)
        models_py = models_py_from_database(table_name=self.table_name)
        print("Generated models.py", models_py)
        self.assertIsNot(models_py, None)
        self.assertGreater(len(models_py), 0)
        model_match = "class Tmp4Wlpvd0C\(models.Model\):"
        models_py_flat = " ".join(models_py.split("\n"))
        self.assertEqual(len(re.findall(model_match, models_py_flat)), 1)
