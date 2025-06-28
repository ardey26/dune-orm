# 🐍 Dune-ORM: Django-Style ORM for Dune Analytics

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/ardey26/dune-orm/blob/main/LICENSE)

Dune-ORM is a Python ORM designed to simplify querying Dune Analytics. Inspired by Django's intuitive query syntax, it allows you to compose complex DuneSQL queries fluently using Python, render them as raw SQL, or execute them directly via the Dune API.

Say goodbye to verbose SQL strings and embrace the elegance of Python for your Dune Analytics needs!

## ✨ Features

*   **Familiar Django-Style API:** Leverage `filter()`, `exclude()`, `order_by()`, and other familiar methods for intuitive query construction.
*   **Lazy Evaluation:** Queries are only generated or executed when explicitly requested, optimizing performance.
*   **Flexible Output:** Easily toggle between generating raw DuneSQL or executing queries directly against the Dune API.
*   **Clean & Readable Code:** Write more maintainable and understandable Dune Analytics queries in Python.

## 🚀 Installation

Getting started with Dune-ORM is straightforward:

```bash
pip install dune-orm
```

## 📚 Usage

Dune-ORM offers a seamless experience for both SQL generation and direct query execution.

### Generating DuneSQL

By default, `DuneQuery` instances are in "read-only" mode, meaning they will generate DuneSQL without attempting to execute it. This is perfect for prototyping or integrating with existing SQL workflows.

```python
from dune_orm import DuneQuery

# Initialize a query for the 'my_table' table
query = DuneQuery(table_name="my_table")

# Apply filters and order by
filtered_query = query.filter(
    col1="value1", col2__gt=100
).order_by("-timestamp")

# Render the query to DuneSQL
dune_sql = filtered_query.all()
print(dune_sql)
# Expected output (simplified):
# SELECT * FROM my_table WHERE col1 = 'value1' AND col2 > 100 ORDER BY timestamp DESC
```

### Executing Queries via Dune API

To execute queries directly and retrieve results (or a link to the Dune query), provide your Dune API Key during `DuneQuery` initialization.

```python
from dune_orm import DuneQuery
import os

# Get your API key from an environment variable (recommended)
DUNE_API_KEY = os.getenv("DUNE_API_KEY", "<your_dune_api_key_here>")

# Initialize with your API key
query_executor = DuneQuery(table_name="another_table", API_KEY=DUNE_API_KEY)

# Execute the query
result_url = query_executor.filter(name="example").limit(5).all()
print(f"Dune Query URL: {result_url}")
# Expected output: A URL to your executed query on Dune Analytics
```

**Note:** For production environments, it's highly recommended to load your `API_KEY` from environment variables rather than hardcoding it.

## 🛠️ Project Structure

*   `src/dune_orm/` – The core ORM logic and modules.
*   `tests/` – Comprehensive unit tests to ensure reliability (Work in Progress).
*   `examples/` – Practical usage demonstrations and code snippets (Work in Progress).

## 🧪 Testing

To run the test suite:

```bash
pytest
```

## 🤝 Contributing

We welcome contributions! If you have suggestions for improvements, new features, or bug fixes, please open an issue or submit a pull request.

## 🪪 License

This project is open-sourced under the MIT License. See the [LICENSE](https://github.com/ardey26/dune-orm/blob/main/LICENSE) file for more details.

---
