from unittest import skip
from unittest.mock import patch

from django.test import TestCase

from django_models_from_csv.models import (
    DynamicModel, create_model_attrs, create_models
)


class SignalAttachDefaultsTestCase(TestCase):

    def find_col(self, dynmodel, name):
        for col in dynmodel.columns:
            if col["name"] == name:
                return col

    @skip("Skip this until signals are set up")
    # @patch("django_models_from_csv.utils.dynmodel.fetch_csv")
    # fetch_csv.return_value = self.csv
    def test_signal_runs_with_save(self):
        self.dynmodel = DynamicModel.objects.create(
            name="SignalTest",
            columns=[{
                "name": "timestamp",
                "type": "datetime",
                "original_name": "When did this happen",
            },{
                "name": "name",
                "type": "text",
                "original_name": "Enter your name",
            }]
        )
        col = self.find_col(self.dynmodel, "metadata")
        self.assertTrue(col is not None)


