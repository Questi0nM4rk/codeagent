---
name: python
description: Python development expertise. Activates when working with .py files, pyproject.toml, or discussing Python frameworks, type hints, or data processing.
---

# Python Development Skill

Domain knowledge for modern Python development with type safety.

## The Iron Law

```
TYPE HINTS EVERYWHERE + STRICT MYPY + RUFF
Every function has type hints. mypy --strict passes. ruff check passes.
```

## Core Principle

> "Python is dynamically typed. Your code doesn't have to be. Type hints prevent bugs."

## Stack

| Component | Technology |
|-----------|------------|
| Version | Python 3.11+ |
| Package Manager | uv (fast), pip |
| Type Checking | mypy --strict |
| Testing | pytest |
| Linting | ruff |
| Formatting | ruff format |

## Essential Commands

```bash
# Virtual environment (uv is faster)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Type check (strict)
mypy src/ --strict

# Lint + format
ruff check src/ --fix
ruff format src/

# Test with coverage
pytest --cov=src --cov-report=term-missing
```

## Patterns

### Type Hints

<Good>
```python
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")

def process_items(
    items: Iterable[T],
    func: Callable[[T], T],
) -> list[T]:
    """Process items with a transformation function."""
    return [func(item) for item in items]

# Protocol for structural typing
from typing import Protocol

class Repository(Protocol[T]):
    def get(self, id: str) -> T | None: ...
    def save(self, entity: T) -> None: ...
```
- Generic with TypeVar
- Callable with proper signature
- Protocol for duck typing
- Union with `|` syntax (3.10+)
</Good>

<Bad>
```python
def process_items(items, func):
    return [func(item) for item in items]
```
- No type hints
- Unclear expected types
- Hard to catch errors at development time
</Bad>

### Dataclasses

<Good>
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
- Frozen for immutability
- Validation in `__post_init__`
- Default factory for mutable defaults
</Good>

### Pydantic for Validation

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

### Result Pattern (No Exceptions)

<Good>
```python
from dataclasses import dataclass
from typing import Generic, TypeVar

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

# Usage
match divide(10, 2):
    case Ok(value):
        print(f"Result: {value}")
    case Err(error):
        print(f"Error: {error}")
```
- Explicit error handling
- Pattern matching (3.10+)
- No exception for expected failures
</Good>

### Async Patterns

```python
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

@asynccontextmanager
async def managed_connection() -> AsyncGenerator[Connection, None]:
    conn = await connect()
    try:
        yield conn
    finally:
        await conn.close()

async def fetch_all(urls: list[str]) -> list[Response]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

## Testing

<Good>
```python
import pytest
from unittest.mock import Mock

class TestUserService:
    @pytest.fixture
    def mock_repo(self) -> Mock:
        return Mock(spec=UserRepository)

    @pytest.fixture
    def service(self, mock_repo: Mock) -> UserService:
        return UserService(mock_repo)

    def test_get_user_returns_user_when_exists(
        self, service: UserService, mock_repo: Mock
    ) -> None:
        # Arrange
        mock_repo.get.return_value = User(id="1", email="test@example.com")

        # Act
        result = service.get_user("1")

        # Assert
        assert result is not None
        assert result.email == "test@example.com"

    def test_get_user_returns_none_when_not_found(
        self, service: UserService, mock_repo: Mock
    ) -> None:
        mock_repo.get.return_value = None

        result = service.get_user("1")

        assert result is None
```
- Type hints on fixtures
- Mock with spec for type checking
- Arrange/Act/Assert pattern
</Good>

### Parametrized Tests

```python
@pytest.mark.parametrize("input_str,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input_str: str, expected: str) -> None:
    assert input_str.upper() == expected
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Type hints are verbose" | They catch bugs. IDEs autocomplete them. Worth it. |
| "Python is dynamic" | Your bugs are too. Type hints prevent them. |
| "mypy --strict is too strict" | It catches real bugs. Fix them. |
| "I'll add types later" | Later never comes. Type from the start. |

## Red Flags - STOP

- Functions without type hints
- `# type: ignore` without explanation
- `Any` type used as escape hatch
- `except Exception:` (too broad)
- Missing `-> None` on functions returning nothing
- `print()` instead of `logging`
- Mutable default arguments (`def f(x=[]): ...`)

## Verification Checklist

- [ ] `mypy src/ --strict` passes
- [ ] `ruff check src/` passes
- [ ] `ruff format --check src/` passes
- [ ] `pytest --cov=src` shows adequate coverage
- [ ] All functions have type hints (including `-> None`)
- [ ] No `# type: ignore` without explanation
- [ ] Public APIs have docstrings

## Review Tools

```bash
mypy src/ --strict                    # Type check
ruff check src/                       # Lint
ruff format --check src/              # Format check
pytest --cov=src --cov-report=term    # Tests with coverage
bandit -r src/                        # Security
pip-audit                             # Dependency vulnerabilities
```

## When Stuck

| Problem | Solution |
|---------|----------|
| mypy error on library | Add type stubs or `# type: ignore[import]` with comment |
| Complex generic types | Start simple, add generics incrementally |
| Circular imports | Move types to separate `types.py` module |
| Async test issues | Use `@pytest.mark.asyncio` decorator |

## Related Skills

- `tdd` - Test-first development workflow
- `reviewer` - Uses mypy/ruff for validation
- `bash` - For scripting alongside Python
