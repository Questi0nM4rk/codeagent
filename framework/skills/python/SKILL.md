---
name: python
description: Python development expertise. Activates when working with .py files, pyproject.toml, or discussing Python frameworks, type hints, or data processing.
---

# Python Development Skill

Domain knowledge for modern Python development.

## Stack

- **Version**: Python 3.11+
- **Package Manager**: uv, pip, poetry
- **Type Checking**: mypy, pyright
- **Testing**: pytest
- **Linting**: ruff, flake8
- **Formatting**: black, ruff format

## Commands

### Development

```bash
# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Using uv (fast)
uv venv
uv pip install -r requirements.txt
uv pip install package

# Run
python src/main.py
python -m module_name

# Type checking
mypy src/
pyright src/

# Linting
ruff check src/
ruff check src/ --fix
flake8 src/

# Formatting
ruff format src/
black src/
black --check src/
```

### Testing

```bash
# Run all tests
pytest
pytest -v
pytest -v --tb=short

# Single test
pytest tests/test_module.py
pytest tests/test_module.py::test_function
pytest -k "test_name"

# With coverage
pytest --cov=src --cov-report=html
pytest --cov=src --cov-report=term-missing

# Parallel
pytest -n auto
```

### Package Management

```bash
# pip
pip install package
pip install -e .
pip freeze > requirements.txt

# poetry
poetry add package
poetry install
poetry build

# uv
uv pip install package
uv pip sync requirements.txt
```

## Patterns

### Type Hints

```python
from typing import Protocol, TypeVar, Generic
from collections.abc import Callable, Iterable

T = TypeVar("T")

def process_items(items: Iterable[T], func: Callable[[T], T]) -> list[T]:
    return [func(item) for item in items]

# Protocol for structural typing
class Repository(Protocol[T]):
    def get(self, id: str) -> T | None: ...
    def save(self, entity: T) -> None: ...
```

### Dataclasses

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class User:
    id: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if "@" not in self.email:
            raise ValueError("Invalid email")
```

### Pydantic Models

```python
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
```

### Async Patterns

```python
import asyncio
from contextlib import asynccontextmanager

async def fetch_all(urls: list[str]) -> list[Response]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

@asynccontextmanager
async def managed_connection():
    conn = await connect()
    try:
        yield conn
    finally:
        await conn.close()
```

### Error Handling

```python
from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)
```

## Testing Patterns

### pytest

```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    @pytest.fixture
    def mock_repo(self):
        return Mock(spec=UserRepository)

    @pytest.fixture
    def service(self, mock_repo):
        return UserService(mock_repo)

    def test_get_user_returns_user(self, service, mock_repo):
        mock_repo.get.return_value = User(id="1", email="test@example.com")

        result = service.get_user("1")

        assert result is not None
        assert result.email == "test@example.com"

    def test_get_user_not_found(self, service, mock_repo):
        mock_repo.get.return_value = None

        result = service.get_user("1")

        assert result is None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input: str, expected: str):
    assert input.upper() == expected
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data()
    assert result is not None
```

## Review Tools

```bash
# Lint
ruff check src/ --output-format=github

# Type check
mypy src/ --strict

# Format check
ruff format --check src/
black --check src/

# Security
bandit -r src/
pip-audit

# Import sorting
isort --check-only src/
ruff check --select I src/
```

## File Organization

```
project/
├── pyproject.toml
├── src/
│   └── package/
│       ├── __init__.py
│       ├── main.py
│       ├── models.py
│       ├── services.py
│       └── repository.py
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   └── test_services.py
└── scripts/
    └── run.py
```

## Common Conventions

- Use type hints everywhere
- Prefer `pathlib.Path` over `os.path`
- Use `dataclasses` or `pydantic` for data structures
- Use `contextlib` for resource management
- Prefer `logging` over `print`
- Use `enum.Enum` for constants
- Document public APIs with docstrings
