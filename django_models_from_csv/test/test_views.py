import json
from unittest import skip
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse

from django_models_from_csv import models as csv_models
from django_models_from_csv.commands.manage_py import (
    make_and_apply_migrations
)
from django_models_from_csv.models import DynamicModel, create_models
from django_models_from_csv.utils.common import get_setting

# from django.db import DEFAULT_DB_ALIAS, connections, transaction


CSV = """Timestamp,Question with short answer?,Question with long answer?,Checkbox?,Option with dropdown?,Multiple choice?, Numeric linear scale?,Multiple choice grid? [row1],Multiple choice grid? [row2],Checkbox grid? [row1],Checkbox grid? [row2],What date?,What time?
4/8/2019 20:43:03,This is a short answer.,This is a suuuuuuuuuuuppperrr long answer. I could repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it repeat it.,The option,OPT2,Lol,4,col1,col2,col2,col1,4/9/2019,10:01:00 PM"""
COLUMNS = [
    {
        "name": "timestamp",
        "original_name": "Timestamp",
        "type": "datetime",
        "attrs": {
            "blank": True,
            "null": True
        }
    },
    {
        "name": "question_with_short_answer_field",
        "original_name": "Question with short answer?",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "question_with_long_answer_field",
        "original_name": "Question with long answer?",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "checkbox_field",
        "original_name": "Checkbox?",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "option_with_dropdown_field",
        "original_name": "Option with dropdown?",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "multiple_choice_field",
        "original_name": "Multiple choice?",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "field_numeric_linear_scale_field",
        "original_name": " Numeric linear scale?",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "multiple_choice_grid_row1_field",
        "original_name": "Multiple choice grid? [row1]",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "multiple_choice_grid_row2_field",
        "original_name": "Multiple choice grid? [row2]",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "checkbox_grid_row1_field",
        "original_name": "Checkbox grid? [row1]",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "checkbox_grid_row2_field",
        "original_name": "Checkbox grid? [row2]",
        "type": "text",
        "attrs": {}
    },
    {
        "name": "what_date_field",
        "original_name": "What date?",
        "type": "date",
        "attrs": {}
    },
    {
        "name": "what_time_field",
        "original_name": "What time?",
        "type": "text",
        "attrs": {}
    }
]


class ViewsTestCaseBase(SimpleTestCase):
    databases = "__all__"

    def login(self):
        self.client.login(username="admin", password=self.password)

    def setUp(self):
        self.password = User.objects.make_random_password(length=16)
        self.user = User.objects.create_superuser(
            username="admin", password=self.password,
            email="admin@localhost",
        )
        self.user.save()
        self.login()

    def tearDown(self):
        self.user.delete()


class BeginViewTestCase(ViewsTestCaseBase):

    def setUp(self):
        super(BeginViewTestCase, self).setUp()
        self.csv = CSV

    def tearDown(self):
        super(BeginViewTestCase, self).tearDown()
        DynamicModel.objects.all().delete()

    def test_can_access_begin_csv_model_page_authed(self):
        self.login()
        url = reverse('csv_models:begin')
        url += "?addnew=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_access_begin_csv_model_page_unauthed(self):
        c = Client()
        response = c.get(reverse('csv_models:begin'))
        self.assertEqual(response.status_code, 302)

    @patch("django_models_from_csv.utils.dynmodel.fetch_csv")
    def test_can_start_new_csv_model(self, fetch_csv):
        fetch_csv.return_value = self.csv
        ids = DynamicModel.objects.all().values("id")
        response = self.client.post(reverse('csv_models:begin'), {
            "csv_name": "TestSheet",
            "csv_url": "https://fake.url",
        })
        new_dynmodel = DynamicModel.objects.first()
        to_url = reverse(
            'csv_models:refine-and-import', args=[new_dynmodel.id]
        )
        self.assertTrue(new_dynmodel.columns)
        self.assertGreaterEqual(len(new_dynmodel.columns), 13)
        self.assertRedirects(response, to_url)
        new_dynmodel.delete()

    # @patch("django_models_from_csv.utils.dynmodel.ScreendoorImporter")
    # def test_can_build_model_from_screendoor(self, fetch_csv):
    #     fetch_csv.return_value = self.csv
    #     ids = DynamicModel.objects.all().values("id")
    #     response = self.client.post(reverse('csv_models:begin'), {
    #         "name": "TestScreendoor",
    #         "sd_api_key": "KEY",
    #         "sd_project_id": "PROJECT_ID",
    #         "sd_form_id": "FORM_ID",
    #     })
    #     new_dynmodel = DynamicModel.objects.last()
    #     to_url = reverse(
    #         'csv_models:refine-and-import', args=[new_dynmodel.id]
    #     )
    #     self.assertTrue(new_dynmodel.columns)
    #     self.assertGreaterEqual(len(new_dynmodel.columns), 13)
    #     self.assertRedirects(response, to_url)
    #     new_dynmodel.delete()


class RefineViewTestCase(ViewsTestCaseBase):
    databases = "__all__"

    def setUp(self):
        super(RefineViewTestCase, self).setUp()
        self.columns = [
            {
                "name": "timestamp",
                "original_name": "Timestamp",
                "type": "text",
                "attrs": {
                    "blank": True,
                    "null": True
                }
            },
            {
                "name": "question_with_short_answer_field",
                "original_name": "Question with short answer?",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "question_with_long_answer_field",
                "original_name": "Question with long answer?",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "checkbox_field",
                "original_name": "Checkbox?",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "option_with_dropdown_field",
                "original_name": "Option with dropdown?",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "multiple_choice_field",
                "original_name": "Multiple choice?",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "field_numeric_linear_scale_field",
                "original_name": " Numeric linear scale?",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "multiple_choice_grid_row1_field",
                "original_name": "Multiple choice grid? [row1]",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "multiple_choice_grid_row2_field",
                "original_name": "Multiple choice grid? [row2]",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "checkbox_grid_row1_field",
                "original_name": "Checkbox grid? [row1]",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "checkbox_grid_row2_field",
                "original_name": "Checkbox grid? [row2]",
                "type": "text",
                "attrs": {}
            },
            {
                "name": "what_date_field",
                "original_name": "What date?",
                "type": "date",
                "attrs": {}
            },
            {
                "name": "what_time_field",
                "original_name": "What time?",
                "type": "text",
                "attrs": {}
            }
        ]
        self.dynmodel = DynamicModel.objects.create(
            name="RefineTest",
            csv_url="https://refine.test/csv",
            columns=self.columns,
        )
        self.dynmodel.save()

    def tearDown(self):
        super(RefineViewTestCase, self).tearDown()
        self.dynmodel.delete()

    def test_can_access_refine_page_authed(self):
        to_url = reverse(
            'csv_models:refine-and-import', args=[self.dynmodel.id]
        )
        response = self.client.get(to_url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_access_refine_page_unauthed(self):
        c = Client()
        to_url = reverse(
            'csv_models:refine-and-import', args=[self.dynmodel.id]
        )
        response = c.get(to_url)
        self.assertEqual(response.status_code, 302)

    @patch("django_models_from_csv.views.configuration.fetch_csv")
    def test_can_refine_existing_model(self, fetch_csv):
        fetch_csv.return_value = CSV
        to_url = reverse(
            'csv_models:refine-and-import', args=[self.dynmodel.id]
        )
        to_url += "?next=/next/url"
        self.assertEqual(self.dynmodel.columns[0]["type"], "text")
        self.columns[0]["type"] = "datetime"
        response = self.client.post(to_url, {
            "columns": json.dumps(self.columns),
        })
        next = get_setting("CSV_MODELS_WIZARD_REDIRECT_TO")
        if next:
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(next))
        else:
            self.assertEqual(response.status_code, 200)
        # make sure the field was actually updated
        self.dynmodel.refresh_from_db()
        self.assertEqual(self.dynmodel.columns[0]["type"], "datetime")


class ImportViewTestCase(ViewsTestCaseBase):
    def setUp(self):
        super(ImportViewTestCase, self).setUp()
        self.csv = CSV
        self.columns = COLUMNS
        self.err_string = "errors were encountered while importing"
        # column with some changes (timestamp: text -> datetime)
        self.dynmodel = DynamicModel.objects.create(
            name="ImportViewTest",
            csv_url="https://import.test/csv",
            columns=self.columns,
        )
        self.dynmodel.save()
        create_models()

    def tearDown(self):
        super(ImportViewTestCase, self).tearDown()
        self.dynmodel.delete()

    def test_can_access_import_page_authed(self):
        to_url = reverse(
            'csv_models:refine-and-import', args=[self.dynmodel.id]
        )
        response = self.client.get(to_url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_access_import_page_unauthed(self):
        c = Client()
        to_url = reverse(
            'csv_models:refine-and-import', args=[self.dynmodel.id]
        )
        response = c.get(to_url)
        self.assertEqual(response.status_code, 302)

    @skip("Until we can get the dynamic models created in test")
    @patch("django_models_from_csv.views.configuration.fetch_csv")
    def test_can_load_import_records_page(self, fetch_csv):
        fetch_csv.return_value = self.csv
        to_url = reverse(
            'csv_models:refine-and-import', args=[self.dynmodel.id]
        )
        response = self.client.post(to_url, {
            "columns": json.dumps(self.columns),
        })
        self.assertEqual(response.status_code, 200)
        err_found = self.err_string in str(response.content)
        self.assertTrue(not err_found, "Import rendered error page")


#class NoTransactionImportDataTestCase(SimpleTestCase):
#    databases = "__all__"
#
#    def test_can_import_records(self):
#        dynmodel = DynamicModel.objects.create(
#            name="ImportDataTest",
#            csv_url="https://import.test/csv",
#            columns=COLUMNS,
#        )
#        dynmodel.save()
#        create_models()
#
#        # connection = connections[DEFAULT_DB_ALIAS]
#        # connection.disable_constraint_checking()
#        create_models()
#        make_and_apply_migrations()
#
#        # make sure the field was actually updated
#        Model = getattr(csv_models, dynmodel.name)
#        self.assertEqual(Model.objects.count(), 1)
