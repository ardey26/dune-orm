

# 🐍 dune-orm

A Django-style ORM for querying Dune Analytics using Python. Compose queries fluently, render them as SQL, or execute directly via the Dune API.

## 🔧 Installation

```bash
pip install dune-orm
```

## 🚀 Usage

```python
from dune_orm import BaseModel

class Opportunities(BaseModel):
    __tablename__ = "name_space.table_name"

# Generate SQL only
sql = Opportunities.objects(convert_only=True).filter(name="ETH").limit(5)
print(sql)

# Execute query
result_url = Opportunities.objects().filter(name="ETH").limit(5)
print(result_url)
```

## 🧩 Features

- Familiar `.filter()`, `.exclude()`, `.order_by()` chaining
- Lazy evaluation with implicit SQL generation or execution
- `convert_only` flag to toggle SQL vs execution
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

MIT License. See [LICENSE](./LICENSE).