def run(row):
    """
    Example plugin to the data pipeline. This simply
    uppercases every entry in a spreadsheet.
    """
    for header in row:
        try:
            row[header] = row[header].upper()
        except AttributeError:
            # not a string
            pass
