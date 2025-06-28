import requests
from datetime import datetime
import time


class DuneQuery:
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

    def execute(self):
        if not self.API_KEY:
            raise ValueError("API_KEY is required for executing queries.")

        # Create the query
        url = "https://api.dune.com/api/v1/query"

        if not self.query_name:
            self.query_name = f"query_{self.table_name}_{datetime.now()}"

        if not self.query_description:
            self.query_description = f"Query for {self.table_name} at {datetime.now()}"

        payload = {
            "name": self.query_name,
            "description": self.query_description,
            "query_sql": self.query,
            "is_private": self.is_private
        }

        headers = {
            "X-DUNE-API-KEY": self.API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)

        data = response.json()
        query_id = data["query_id"]

        # Execute the query
        url = f"https://api.dune.com/api/v1/query/{query_id}/execute"
        headers = {"X-DUNE-API-KEY": self.API_KEY}
        requests.post(url, headers=headers)

        # Poll for results every 5 seconds until the query is complete
        query_url = f"https://api.dune.com/api/v1/query/{query_id}/results"

        MAX_ATTEMPTS = 12
        while MAX_ATTEMPTS > 0:
            print("Polling for results...")
            response = requests.get(query_url, headers=headers)
            data = response.json()
            if "result" in data and data["result"] and "rows" in data["result"]:
                rows = data["result"]["rows"]
                return rows if rows else []
            time.sleep(5)
            MAX_ATTEMPTS -= 1
        raise Exception(
            "Query execution timed out or failed to return results.")

    def build_filters(self):
        built_filters = " and ".join(
            f"{k} = '{v}'" for k, v in self.filters.items())
        return built_filters

    def build_exclude(self):
        built_exclude = " and ".join(
            f"{k} = '{v}'" for k, v in self.exclude_filters.items())
        return built_exclude

    def process_query(self):
        if not self.fields:
            self.query = f"select * from {self.table_name}"
        else:
            parsed_fields = ",".join(self.fields)
            self.query = f"select {parsed_fields} from {self.table_name}"

        if not self.query:
            self.all()

        if self.filters:
            built_filters = self.build_filters()
            self.query += f" where {built_filters}"

        if self.exclude_filters:
            built_exclude = self.build_exclude()
            self.query += f" where not {built_exclude}"

        if self.sort_by:
            self.query += f" order by {self.sort_by} {self.sort_order}"

        if self._limit:
            self.query += f" limit {self._limit}"

        if self.is_read_only:
            return DuneQuery(
                table_name=self.table_name,
                is_read_only=self.is_read_only,
                query=self.query,
                fields=self.fields,
                filters=self.filters,
                exclude_filters=self.exclude_filters,
                limit=self._limit,
                sort_by=self.sort_by,
                sort_order=self.sort_order,
                is_private=self.is_private,
                query_name=self.query_name,
                query_description=self.query_description
            )

        query_execution_status = self.execute()

        return query_execution_status

    def all(self):
        self.filters = {}
        self.fields = []
        return self.process_query()

    def values(self, *args):
        self.fields = args
        return self.process_query()

    def filter(self, **kwargs):
        self.filters = kwargs
        return self.process_query()

    def exclude(self, **kwargs):
        self.exclude_filters = kwargs
        return self.process_query()

    def get(self, **kwargs):
        self.filters = kwargs
        self._limit = 1
        return self.process_query()

    def order_by(self, order_by_field, ascending=True):
        self.sort_by = order_by_field
        self.sort_order = 'asc' if ascending else 'desc'

        return self.process_query()

    def limit(self, limit):
        self._limit = limit
        return self.process_query()
