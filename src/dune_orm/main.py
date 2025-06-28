from builder import DuneQueryBuilder
from executor import DuneQueryExecutor
from query import DuneSQLQueryBuilder


class DuneQuery(DuneQueryBuilder, DuneQueryExecutor, DuneSQLQueryBuilder):
    """
        DuneQuery is a class that allows you to build and execute SQL queries
        against Dune Analytics tables. It supports filtering, sorting, and
        limiting results, and can be used to create both read-only and writable
        queries.

        Attributes:
            table_name (str): The name of the Dune Analytics table to query.
            is_read_only (bool): If True, the query is read-only and no API calls
                will be made. If False, the query can be executed and results
                will be fetched from the Dune API.
            query (str): The SQL query to execute.
            fields (list): A list of fields to select in the query.
            filters (dict): A dictionary of filters to apply to the query.
            exclude_filters (dict): A dictionary of filters to exclude from the query.
            limit (int): The maximum number of rows to return from the query.
            sort_by (str): The field to sort the results by.
            sort_order (str): The order to sort the results in ('asc' or 'desc').
            is_private (bool): If True, the query is private and not shared publicly.
            query_name (str): The name of the query for identification.
            query_description (str): A description of the query.
            API_KEY (str): The API key for authenticating with the Dune API.
    """
    def __init__(self,
                 table_name,
                 is_read_only=False,
                 query=None,
                 fields=[],
                 filters={},
                 exclude_filters={},
                 limit=0,
                 sort_by=None,
                 sort_order="asc",
                 is_private=True,
                 query_name=None,
                 query_description=None,

                 API_KEY=None
                 ):

        self.table_name = table_name
        self.is_read_only = is_read_only

        self.query = query
        self.fields = fields
        self.filters = filters
        self.exclude_filters = exclude_filters
        self._limit = limit

        self.sort_by = sort_by
        self.sort_order = sort_order

        self.query_name = query_name
        self.query_description = query_description
        self.is_private = is_private

        # API_KEY is optional, if not provided, the table will be read-only
        # and no API calls will be made.
        # If provided, the table will be writable and API calls will be made.
        # Note: API_KEY is not used in this example, but can be used to authenticate with the Dune API.
        self.API_KEY = API_KEY
        if self.API_KEY is None:
            self.is_read_only = True

    def __str__(self):
        return self.query

    def __repr__(self):
        return str(self)