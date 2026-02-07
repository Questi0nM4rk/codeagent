---
name: pytest
description: Pytest testing framework with coverage. Activates when writing tests, running test suites, or configuring test infrastructure.
---

# Pytest Skill

Test runner for all Python code. Always with coverage.

## Project Config

In `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 85
show_missing = true
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]
```

## Commands

```bash
# Run all tests with coverage
uv run pytest tests/ --cov=src --cov-fail-under=85

# Run specific test file
uv run pytest tests/test_memory.py -v

# Run specific test
uv run pytest tests/test_memory.py::test_store_and_retrieve -v

# Run with full output
uv run pytest tests/ -v --tb=long

# Run only failed tests from last run
uv run pytest --lf

# Run tests matching keyword
uv run pytest -k "test_search" -v
```

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures
├── test_memory.py       # Test module (test_*.py)
├── test_mcp_server.py
└── fixtures/            # Test data
    └── sample.json
```

## Writing Tests

### TDD: Test First

```python
from __future__ import annotations


def test_user_created_with_valid_email() -> None:
    """Test that user creation succeeds with valid email."""
    user = create_user(email="test@example.com")

    assert user.email == "test@example.com"
    assert user.id is not None
```

### Fixtures

```python
import pytest


@pytest.fixture()
def mock_db() -> MockDatabase:
    """Provide a clean mock database for each test."""
    db = MockDatabase()
    db.setup()
    yield db
    db.teardown()
```

### Async Tests

```python
import pytest


@pytest.mark.asyncio()
async def test_async_search() -> None:
    """Test async search returns results."""
    results = await search_memory("test query")

    assert len(results) > 0
```

### Parametrize

```python
@pytest.mark.parametrize("input_val,expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input_val: str, expected: str) -> None:
    assert input_val.upper() == expected
```

## Fixture Scopes

| Scope | Lifetime | Use For |
| ----- | -------- | ------- |
| function | each test (default) | most fixtures |
| class | each test class | shared setup in class |
| module | each test file | expensive file-level setup |
| session | entire run | database connections, servers |

## Coverage

CI enforces `--cov-fail-under=85` with branch coverage.

Exclude from coverage:
- `pragma: no cover` comment
- `if TYPE_CHECKING:` blocks (auto-excluded)

## Pre-commit Integration

`name-tests-test` hook enforces `test_*.py` naming with `--pytest-test-first`.

## Red Flags

- Tests without assertions
- Shared mutable state between tests
- Tests that depend on execution order
- `time.sleep()` in tests (use mocks)
- Testing implementation details instead of behavior
