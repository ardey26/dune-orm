import requests
from datetime import datetime

class DuneQuery:
    def __init__(self, 
                 name_space, 
                 table_name, 
                 is_read_only=False, 
                 query = None, 
                 fields = [], 
                 filters = {}, 
                 exclude_filters = {},
                 limit = 0,
                 sort_by = None,
                 sort_order = "asc",
                 is_private = False,
                 query_name = None,
                 query_description = None,

                 API_KEY = None
                 ):


        self.name_space = name_space
        self.table_name = table_name
        self.is_read_only = is_read_only

        self.query = query
        self.fields = fields
        self.filters = filters
        self.exclude_filters = exclude_filters
        self.limit = limit

        self.sort_by = sort_by
        self.sort_order = sort_order

        self.parsed_table_name = f"dune.{name_space}.{table_name}"

        self.query_name = query_name
        self.query_description = query_description
        self.private = is_private

        # API_KEY is optional, if not provided, the table will be read-only
        # and no API calls will be made.
        # If provided, the table will be writable and API calls will be made.
        # Note: API_KEY is not used in this example, but can be used to authenticate with the Dune API.
        self.API_KEY = API_KEY
        if self.API_KEY is None:
            self.is_read_only = True

    def __str__(self):
        return self.query

    def execute(self):
        if not self.API_KEY:
            raise ValueError("API_KEY is required for executing queries.")
        
        url = "https://api.dune.com/api/v1/query"

        if not self.query_name:
            self.query_name = f"query_{self.name_space}_{self.table_name}_{datetime.now()}"

        if not self.query_description:
            self.query_description = f"Query for {self.name_space}.{self.table_name} at {datetime.now()}"

        payload = {
            "name": self.query_name,
            "description": self.query_description,
            "query_sql": self.query,
            "is_private": self.private
        }

        headers = {
            "X-DUNE-API-KEY": self.API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, json=payload)

        if not response.status == 200:
            return
        
        data = response.json()
        query_id = data["query_id"]

        query_url = f"https://api.dune.com/api/v1/query/{query_id}/results"

        response = requests.get(query_url, headers=headers)

        if not response.status == 200:
            return
        
        data = response.json()
        results = data["result"]
        
        if not results:
            return []
        
        rows = results["rows"]
        if not rows:
            return []
        
        return rows

    def build_filters(self):
        built_filters = " and ".join(f"{k} = '{v}'" for k, v in self.filters.items())
        return built_filters

    def build_exclude(self): 
        built_exclude = " and ".join(f"{k} = '{v}'" for k, v in self.exclude_filters.items())
        return built_exclude

    def process_query(self):
        if not self.fields:
            self.query = f"select * from {self.parsed_table_name}"
        else:
            parsed_fields = ",".join(self.fields)
            self.query = f"select {parsed_fields} from {self.parsed_table_name}"

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

        if self.limit:
            self.query += f" limit {self.limit}"

        if self.is_read_only:
            return DuneQuery(
                        name_space=self.name_space,
                        table_name=self.table_name,
                        is_read_only=self.is_read_only,
                        query=self.query,
                        fields=self.fields,
                        filters=self.filters,
                        exclude_filters=self.exclude_filters,
                        limit=self.limit,
                        sort_by=self.sort_by,
                        sort_order=self.sort_order,
                        is_private=self.is_private,
                        query_name=self.query_name,
                        query_description=self.query_description
                    )

        query_execution_status = self.execute(self.query)

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
        self.limit = 1
        return self.process_query()

    def order_by(self, order_by_field, ascending=True):
        self.sort_by = order_by_field
        self.sort_order = 'asc' if ascending else 'desc'

        return self.process_query()