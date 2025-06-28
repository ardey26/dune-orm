

import requests
import time
from datetime import datetime

class DuneQueryExecutor:
    """Handles submission and polling of Dune API queries."""

    def execute(self):
        """Submit the built query to Dune, poll for results, and return rows."""
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
        exec_url = f"https://api.dune.com/api/v1/query/{query_id}/execute"
        requests.post(exec_url, headers={"X-DUNE-API-KEY": self.API_KEY})

        # Poll for results
        result_url = f"https://api.dune.com/api/v1/query/{query_id}/results"
        attempts = 12
        while attempts > 0:
            response = requests.get(result_url, headers={"X-DUNE-API-KEY": self.API_KEY})
            data = response.json()
            if data.get("result", {}).get("rows") is not None:
                rows = data["result"]["rows"]
                return rows if rows else []
            time.sleep(5)
            attempts -= 1

        raise Exception("Query execution timed out or failed to return results.")