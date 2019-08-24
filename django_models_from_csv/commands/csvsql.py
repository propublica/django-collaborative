import io
import tempfile

from csvkit.utilities.csvsql import CSVSQL
from django.db import connection


class FakeArgs():
    """
    A fake arguments class for use when calling the csvsql command.
    """
    # encoding= "utf-8"
    # skip_lines = 0
    # table_names = None
    # query = None
    # unique_constraint = None
    # connection_string = None
    # insert = False
    # no_create = False
    # create_if_not_exists = False
    # overwrite = None
    # before_insert = None
    # after_insert = None
    # chunk_size = None
    # sniff_limit = 1000
    # no_inference = False
    # date_format = None
    # datetime_format = None
    # locale = 'en_US'
    # db_schema = None
    # no_constraints = False
    after_insert = None
    before_insert = None
    blanks = False
    chunk_size = None
    connection_string = None
    create_if_not_exists = False
    date_format = None
    datetime_format = None
    db_schema = None
    delimiter = None
    dialect = None
    doublequote = True
    encoding = 'utf-8'
    escapechar = None
    field_size_limit = None
    insert = False
    line_numbers = False
    locale = 'en_US'
    no_constraints = False
    no_create = False
    no_header_row = False
    no_inference = False
    overwrite = False
    prefix = []
    query = None
    quotechar = None
    quoting = None
    skip_lines = 0
    skipinitialspace = False
    sniff_limit = None
    table_names = None
    tabs = False
    unique_constraint = None
    verbose = False
    zero_based = False


class CSVSQLWrap(CSVSQL):
    """
    Wraps the CSVSQL class, which contains the actual command, but
    disables command line args parsing, use of stdin/out, etc.
    """
    reader_kwargs = {}

    def __init__(self):
        self.args = FakeArgs()


def run_csvsql(csv):
    """
    Runs the equivalent of:
        csvsql -S -i sqlite sheet.csv

    Returns a string representing the output of csvsql, which
    is a SQL CREATE TABLE command.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f_in:
        f_in.write(csv)
        f_in.flush()
        try:
            # We have to close this in Windows
            f_in.close()
        except Exception as e:
            pass # this means we're on a unix env

        with io.StringIO() as f_out:
            csvsql = CSVSQLWrap()
            # csvsql.args.dialect = connection.vendor
            csvsql.args.dialect = "sqlite"
            csvsql.args.skipinitialspace = True
            csvsql.args.input_paths = [f_in.name]
            csvsql.output_file = f_out
            csvsql.main()
            return f_out.getvalue()

