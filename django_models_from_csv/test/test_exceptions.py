from django.test import SimpleTestCase

from django_models_from_csv.exceptions import (
    DataSourceExistsError, UniqueColumnError
)


class ImportExceptionsTestCase(SimpleTestCase):
    def test_can_instantiate_duplicate_source_exists_error(self):
        name = "column name"
        err = DataSourceExistsError(name)
        self.assertTrue(name in str(err))

    def test_can_raise_duplicate_source_exists_error(self):
        name = "column name"
        with self.assertRaises(DataSourceExistsError):
            raise DataSourceExistsError(name)

    def test_can_instantiate_unique_name_error(self):
        name = "column name"
        err = UniqueColumnError(name)
        self.assertTrue(name in str(err))

    def test_can_raise_unique_name_error(self):
        name = "column name"
        with self.assertRaises(UniqueColumnError):
            raise UniqueColumnError(name)
