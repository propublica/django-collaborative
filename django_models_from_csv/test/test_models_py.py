from django.test import SimpleTestCase

from django_models_from_csv.utils.models_py import (
    extract_fields, extract_field_declaration_args,
    extract_field_type
)
from django_models_from_csv.utils.dynmodel import from_models_py


class ModelsPyConversionTestCase(SimpleTestCase):
    databases = '__all__'

    def setUp(self):
        self.models_py = """
        from django.db import models

        class Tmp4Wlpvd0C(models.Model):
            timestamp = models.TextField(db_column='Timestamp', blank=True, null=True)
            question_with_short_answer_field = models.TextField(db_column='Question with short answer?')
            question_with_long_answer_field = models.TextField(db_column='Question with long answer?')
            checkbox_field = models.TextField(db_column='Checkbox?')
            option_with_dropdown_field = models.TextField(db_column='Option with dropdown?')
            multiple_choice_field = models.TextField(db_column='Multiple choice?')
            field_numeric_linear_scale_field = models.TextField(db_column=' Numeric linear scale?')
            multiple_choice_grid_row1_field = models.TextField(db_column='Multiple choice grid? [row1]')
            multiple_choice_grid_row2_field = models.TextField(db_column='Multiple choice grid? [row2]')
            checkbox_grid_row1_field = models.TextField(db_column='Checkbox grid? [row1]')
            checkbox_grid_row2_field = models.TextField(db_column='Checkbox grid? [row2]')
            what_date_field = models.DateField(db_column='What date?')
            what_time_field = models.TextField(db_column='What time?')
            """

    def test_can_extract_fields_from__models_py(self):
        fields = extract_fields(self.models_py)
        self.assertTrue(fields)
        field_names = list(fields.keys())
        self.assertGreaterEqual(len(field_names), 13)
        self.assertEqual(field_names[0], "timestamp")
        self.assertEqual(field_names[-1], "what_time_field")

    def test_can_extract_field_attributes(self):
        fields = extract_fields(self.models_py)
        declaration = fields["timestamp"]
        kwargs = extract_field_declaration_args(declaration)
        self.assertEqual(len(list(kwargs.keys())), 3)
        self.assertEqual(kwargs["db_column"], "Timestamp")
        self.assertEqual(kwargs["blank"], True)
        self.assertEqual(kwargs["null"], True)

    def test_can_extract_field_type(self):
        declaration = self.models_py.split("\n")[4]
        field_type = extract_field_type(declaration)
        self.assertEqual(field_type, "text")
        declaration = self.models_py.split("\n")[-3]
        field_type = extract_field_type(declaration)
        self.assertEqual(field_type, "date")

    def test_can_build_dynmodel_from_models_py(self):
        model_name = "TestData"
        csv_url = "https://fake.url"
        sheet = from_models_py(model_name, self.models_py,
            csv_url=csv_url
        )
        self.assertTrue(sheet)
        self.assertEqual(sheet.name, model_name)
        self.assertEqual(sheet.csv_url, csv_url)
        self.assertTrue(type(sheet.columns), list)
        self.assertGreaterEqual(len(sheet.columns), 13)
        self.assertEqual(sheet.columns[0]["name"], "timestamp")
        self.assertEqual(sheet.columns[0]["original_name"], "Timestamp")
        self.assertEqual(sheet.columns[0]["type"], "text")
        # we removed db_column, that's the CSV header name,
        # so we have two remaining field kwargs
        self.assertEqual(len(sheet.columns[0]["attrs"].keys()), 2)
        self.assertEqual(sheet.columns[-2]["name"], "what_date_field")
        self.assertEqual(sheet.columns[-2]["type"], "date")
