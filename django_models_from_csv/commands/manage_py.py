from django.core.management.commands import (
    makemigrations, migrate, inspectdb
)
from django.db import DEFAULT_DB_ALIAS

from django_models_from_csv.utils.common import get_setting


def run_inspectdb(table_name=None):
    """
    Run inspectdb against our secondary in-memory database. Basically,
    we're running the equivalent of this manage.py command:

        ./manage.py inspectdb --database schemabuilding

    Returns the generated models.py
    """
    cmd = inspectdb.Command()
    options = {
        'verbosity': 1,
        'settings': None,
        'pythonpath': None,
        'traceback': False,
        'no_color': False,
        'force_color': False,
        'table': [table_name] or [],
        'database': get_setting("CSV_MODELS_TEMP_DB"),
        'include_partitions': False,
        'include_views': False
    }
    # This command returns a generator of models.py text lines
    gen = cmd.handle_inspection(options)
    return "\n".join(list(gen))


def run_makemigrations(module):
    """
    Run the equivalent of ./manage.py makemigrations [module]
    """
    mkmigrate_cmd = makemigrations.Command()
    args = (module,)
    options =  {
        'verbosity': 1,
        'settings': None,
        'pythonpath': None,
        'traceback': False,
        'no_color': False,
        'force_color': False,
        'dry_run': False,
        'merge': False,
        'empty': False,
        'interactive': True,
        'name': None,
        'include_header': True,
        'check_changes': False
    }
    mkmigrate_cmd.handle(*args, **options)


def turn_fk_checks(on=True):
    conn = connections[DEFAULT_DB_ALIAS]
    cursor = conn.cursor()
    sql = "PRAGMA foreign_keys = %s;" % (
        "ON" if on else "OFF"
    )
    cursor.execute(sql)


def run_migrate():
    """
    Run the equivalent of ./manage.py migrate
    """
    migrate_cmd = migrate.Command()
    args = ()
    options = {
        'verbosity': 3,
        'interactive': False,
        'database': DEFAULT_DB_ALIAS,
        'run_syncdb': True,
        'app_label': None,
        'plan': None,
        'fake': False,
        'fake_initial': False,
    }
    migrate_cmd.handle(*args, **options)


def make_and_apply_migrations():
    """
    Runs the equivalent of makemigrations on our dynamic
    models.py and then applies the migrations via migrate.
    """
    # TODO: replace with migration-less DB management
    run_makemigrations("django_models_from_csv")
    run_migrate()
