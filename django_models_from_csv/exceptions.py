class UniqueColumnError(Exception):
   """
   Thrown when, while import, we encounter a duplicate column
   header.
   """
   pass

class DataSourceExistsError(Exception):
    """
    Thrown when a user attempts to re-create an already existing
    data source (by name).
    """
    pass
