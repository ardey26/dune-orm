

# 🐍 dune-orm

A Django-style ORM for querying Dune Analytics using Python. Compose queries fluently, render them as SQL, or execute directly via the Dune API.

## 🔧 Installation

```bash
pip install dune-orm
```

## 🚀 Usage

```python
from dune_orm import DuneQuery

# Generates DuneSQL only
query = DuneQuery(table_name="table")
query.all()

# Executes query and returns Dune query URL
query = DuneQuery(table_name="table", API_KEY="<api_key_here>")
query.all()

```

## 🧩 Features

- Familiar `.filter()`, `.exclude()`, `.order_by()` chaining
- Lazy evaluation with implicit SQL generation or execution
- `is_read_only` flag to toggle SQL vs execution
- Clean Django-style API

## 📁 Project Structure

- `src/dune_orm/` – ORM internals
- `tests/` – unit tests (WIP)
- `examples/` – usage demos (WIP)

## 🧪 Testing

```bash
pytest
```

## 🪪 License

MIT License. See [LICENSE](https://github.com/ardey26/dune-orm/blob/main/LICENSE).
