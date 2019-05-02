from django.test import TestCase

from django_models_from_csv.utils.csv import (
    extract_key_from_csv_url
)


class FetchCSVTestCase(TestCase):
    def setUp(self):
        self.csv_url = "https://docs.google.com/spreadsheets/d/18I8_so8_lCWEQLZ8LsBfOgz_SRRSIokZ06duc/edit?usp=sharing"

    def test_can_extract_key_from_csv_url(self):
        key = extract_key_from_csv_url(self.csv_url)
        self.assertEqual(key, "18I8_so8_lCWEQLZ8LsBfOgz_SRRSIokZ06duc")
