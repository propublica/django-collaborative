"""
Manager for creating, updating and dropping the actual database tables
and columns backing a dynamically generated model.

This is taken and modified from django-dynamic-models library:
https://github.com/rvinzent/django-dynamic-models
"""
from django.db import connection


class ModelSchemaEditor:
    def __init__(self, initial_model=None):
        self.initial_model = initial_model
        self.editor = connection.schema_editor

    def update_table(self, new_model):
        print("Update table", new_model)
        if self.initial_model and self.has_changed(new_model):
            print("Has changed. Altering table...")
            self.alter_table(new_model)
        elif not self.initial_model:
            print("New table detected. Creating...")
            self.create_table(new_model)
        print("Done")
        self.initial_model = new_model

    def has_changed(self, model):
        return self.initial_model != model

    def create_table(self, new_model):
        """Create a database table for this model."""
        print("create_table", new_model)
        with self.editor() as editor:
            print("editor", editor)
            editor.create_model(new_model)

    def alter_table(self, new_model):
        """Change the model's db_table to the currently set name."""
        print("alter_table", new_model)
        old_name = self.initial_model._meta.db_table
        print("old_name", old_name)
        new_name = new_model._meta.db_table
        print("new_name", new_name)
        with self.editor() as editor:
            print("editor", editor)
            editor.alter_db_table(new_model, old_name, new_name)

    def drop_table(self, model):
        """Delete a database table for the model."""
        print("drop_table", model)
        with self.editor() as editor:
            print('editor', editor)
            editor.delete_model(model)


class FieldSchemaEditor:
    def __init__(self, initial_field=None):
        self.initial_field = initial_field
        self.editor = connection.schema_editor

    def update_column(self, model, new_field):
        print("updating_column", new_field)
        if self.initial_field and self.has_changed(new_field):
            print("Changed field detected changing to", new_field)
            self.alter_column(model, new_field)
        elif not self.initial_field:
            print("New field detected", new_field)
            self.add_column(model, new_field)
        self.initial_field = new_field

    def has_changed(self, field):
        """Check if the field schema has changed."""
        return self.initial_field != field

    def add_column(self, model, field):
        """Add a field to this model's database table."""
        print("add_column", model, field)
        with self.editor() as editor:
            print("editor", editor)
            editor.add_field(model, field)

    def alter_column(self, model, new_field):
        """Alter field schema including constraints on the model's table."""
        with self.editor() as editor:
            editor.alter_field(model, self.initial_field, new_field)

    def drop_column(self, model, field):
        """Remove a field from the model's database table."""
        with self.editor() as editor:
            editor.remove_field(model, field)
