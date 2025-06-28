import requests
import time
from datetime import datetime
from typing import List
from enum import Enum
import logging
logger = logging.getLogger(__name__)


class ExecutionID(str):
    pass

class QueryResult(object):
    pass


class QueryID(int):
    """Represents a unique identifier for a Dune Analytics query."""

    def __new__(cls, value: int):
        if value <= 0:
            raise ValueError("QueryID must be a positive integer")
        return super().__new__(cls, value)

    def __str__(self):
        return str(self)


class RawDuneQuery(str):
    """Represents a raw SQL query to be executed on Dune Analytics."""

    def __new__(cls, value: str):
        if not value.strip().lower().startswith("select"):
            raise ValueError("RawDuneQuery must start with 'SELECT'")
        return super().__new__(cls, value)

    def __str__(self):
        return self


class ExecutionStatus(str, Enum):
    """Represents the status of a query execution."""
    QUERY_STATE_PENDING = "QUERY_STATE_PENDING"
    QUERY_STATE_EXECUTING = "QUERY_STATE_EXECUTING"
    QUERY_STATE_FAILED = "QUERY_STATE_FAILED"
    QUERY_STATE_COMPLETED = "QUERY_STATE_COMPLETED"
    QUERY_STATE_CANCELED = "QUERY_STATE_CANCELED"
    QUERY_STATE_EXPIRED = "QUERY_STATE_EXPIRED"
    QUERY_STATE_COMPLETED_PARTIAL = "QUERY_STATE_COMPLETED_PARTIAL"


class DuneQueryExecutor:
    """Handles submission and polling of Dune API queries."""

    # Polling configuration
    DEFAULT_MAX_ATTEMPTS = 12
    DEFAULT_POLL_INTERVAL = 5  # seconds

    status = None
    query_url = "https://dune.com/queries/"

    def get_query(self) -> str:
        """Return the raw Dune SQL command."""
        if not self.query:
            raise ValueError("No query has been built or set.")

        return RawDuneQuery(self.query)

    def get_query_url(self) -> str:
        """Return the URL for the Dune query."""
        if not self.query_url:
            raise ValueError("Query URL is not set.")
        return self.query_url

    def create_query(self) -> str:
        """Submit SQL to Dune and return the query ID."""
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
        response.raise_for_status()
        data = response.json()
        query_id = QueryID(data["query_id"])

        if not query_id:
            raise Exception("Failed to create query. Response: " + str(data))
        
        self.query_url = f"{self.query_url}{query_id}"

        return query_id

    def execute_query(self, query_id: QueryID) -> ExecutionID:
        """Trigger execution of a previously created query."""
        exec_url = f"https://api.dune.com/api/v1/query/{query_id}/execute"
        response = requests.post(
            exec_url, headers={"X-DUNE-API-KEY": self.API_KEY})
        response.raise_for_status()
        data = response.json()
        return ExecutionID(data.get("execution_id", None))

    def get_execution_status(self, execution_id: ExecutionID) -> bool:
        """Check if the query has completed (rows available)."""
        url = f"https://api.dune.com/api/v1/execution/{execution_id}/status"

        headers = {"X-DUNE-API-KEY": self.API_KEY}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        status_str = data.get("status", "")

        try:
            status = ExecutionStatus(status_str)
        except ValueError:
            raise ValueError(f"Invalid execution status: {status_str}")

        self.status = status

        if status in (ExecutionStatus.QUERY_STATE_COMPLETED, ExecutionStatus.QUERY_STATE_COMPLETED_PARTIAL):
            return True
        elif status in (ExecutionStatus.QUERY_STATE_FAILED, ExecutionStatus.QUERY_STATE_CANCELED, ExecutionStatus.QUERY_STATE_EXPIRED):
            raise Exception(f"Query execution failed with status: {status}")

    def get_results(self, query_id: QueryID) -> List[QueryResult]:
        """
            Retrieve the query results (rows).
            This method will raise an exception if the query has not completed successfully.
            It requires the API_KEY to be set in the DuneQueryExecutor instance.
            It returns a list of dictionaries representing the rows returned by the query.
            If the query has not completed or has failed, it raises an exception with an appropriate message
        """

        if self.status not in (ExecutionStatus.QUERY_STATE_COMPLETED, ExecutionStatus.QUERY_STATE_COMPLETED_PARTIAL):
            raise Exception(
                f"Cannot fetch results, current status: {self.status}")

        result_url = f"https://api.dune.com/api/v1/query/{query_id}/results"
        response = requests.get(result_url, headers={
                                "X-DUNE-API-KEY": self.API_KEY})
        response.raise_for_status()
        data = response.json()
        return data.get("result", {}).get("rows", [])

    def execute(self) -> List[QueryResult]:
        """
            Submit the built query to Dune, poll for results, and return rows.
            This method will raise an exception if the query fails or times out.
            It requires the API_KEY to be set in the DuneQueryExecutor instance.
            It will poll the Dune API for up to 60 seconds (12 attempts of 5 seconds each)
            before timing out.
            If the query is successful, it returns the rows as a list of dictionaries.
            If the query fails or times out, it raises an exception with an appropriate message.
        """
        if not self.API_KEY:
            raise ValueError("API_KEY is required for executing queries.")

        query_id = self.create_query()
        execution_id = self.execute_query(query_id)

        max_attempts = getattr(self, 'max_attempts', self.DEFAULT_MAX_ATTEMPTS)
        poll_interval = getattr(self, 'poll_interval', self.DEFAULT_POLL_INTERVAL)
        attempts = max_attempts

        logger.info(f"Starting polling for execution {execution_id}, up to {max_attempts} attempts every {poll_interval}s")

        while attempts > 0:
            logger.debug(f"Polling attempt {max_attempts - attempts + 1}/{max_attempts}")
            if self.get_execution_status(query_id):
                return self.get_results(query_id)
            time.sleep(poll_interval)
            attempts -= 1

        raise Exception(
            "Query execution timed out or failed to return results.")
