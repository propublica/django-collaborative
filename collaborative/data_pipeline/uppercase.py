def run(row, columns=None):
    """
    Example plugin to the data pipeline. This simply uppercases every
    entry in a spreadsheet.

    When data is being imported, this function will be called for every
    row, if it has been enabled (uncommented) inside the DATA_PIPELINE
    list in your settings.py. You will also be provided the list of
    columns (and their user-defined settings) for the data source you
    are recieving a row for.

    This function shouldn't return any data, instead it should modify
    the row in place (to avoid copying each row of the spreadsheet for
    every pipeline processor).

    Note that the headers are slightly different from what you may see
    in your source spreadsheet, or in the collaborative admin pages --
    they are lowercased and "slugified" (underscores in place of spaces,
    etc).
    """
    for header in row:
        try:
            row[header] = row[header].upper()
        except AttributeError:
            # not a string
            pass
