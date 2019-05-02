import io
import tempfile

from csvkit.utilities.csvsql import CSVSQL


class FakeArgs():
    """
    A fake arguments class for use when calling the csvsql command.
    """
    encoding= "utf-8"
    skip_lines = 0
    table_names = None
    query = None
    unique_constraint = None
    connection_string = None
    insert = False
    no_create = False
    create_if_not_exists = False
    overwrite = None
    before_insert = None
    after_insert = None
    chunk_size = None
    sniff_limit = 1000
    no_inference = False
    date_format = None
    datetime_format = None
    locale = 'en_US'
    db_schema = None
    no_constraints = False


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
    f_in = tempfile.NamedTemporaryFile(mode='w', delete=False)
    f_in.write(csv)
    f_in.flush()
    try:
        # We have to close this in Windows
        f_in.close()
    except Exception as e:
        pass # this means we're on a unix env
    f_out = io.StringIO()
    csvsql = CSVSQLWrap()
    csvsql.args.dialect = "sqlite"
    csvsql.args.skipinitialspace = True
    csvsql.args.input_paths = [f_in.name]
    csvsql.output_file = f_out
    csvsql.main()
    return f_out.getvalue()
