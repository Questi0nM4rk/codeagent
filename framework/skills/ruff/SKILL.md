---
name: ruff
description: Ruff pedantic Python linter and formatter. Activates when working with .py files, ruff.toml, or fixing Python lint errors.
---

# Ruff Skill

Ruff replaces flake8, isort, pyflakes, pycodestyle, bandit (partially), and more. Single tool.

## Config Location

`ruff.toml` in project root. Owned by **ai-guardrails** - don't edit directly.

## Philosophy

`select = ["ALL"]` - every rule enabled. Disable explicitly in `ignore` or `per-file-ignores`.

## Critical Settings

| Setting | Value | Why |
| ------- | ----- | --- |
| target-version | py311 | Minimum Python |
| line-length | 88 | Black default |
| fix | false | Never auto-fix in CI, force manual review |
| convention | google | Google-style docstrings |

## Required in Every File

```python
from __future__ import annotations  # MUST be first import
```

Enforced by `required-imports` in `[lint.isort]`. Violation: `I002`.

## Banned APIs

These are hard errors via `[lint.flake8-tidy-imports.banned-api]`:

| Banned | Use Instead |
| ------ | ----------- |
| `typing.Optional` | `X \| None` |
| `typing.Union` | `X \| Y` |
| `typing.List` | `list[X]` |
| `typing.Dict` | `dict[X, Y]` |
| `typing.Set` | `set[X]` |
| `typing.Tuple` | `tuple[X, ...]` |

Also: relative imports banned (`ban-relative-imports = "all"`).

## Complexity Limits

| Metric | Limit |
| ------ | ----- |
| Cyclomatic complexity | 10 |
| Function args | 5 |
| Boolean expressions | 3 |
| Branches | 10 |
| Local variables | 10 |
| Nested blocks | 3 |
| Positional args | 5 |
| Return statements | 4 |
| Statements | 30 |

## Per-file Ignores

**Tests** (`tests/**/*.py`): `S101` (assert), `ARG001/2` (unused args), `PLR2004` (magic values), `PLC0415` (lazy imports), `FBT001/2/3` (boolean args), `SLF001` (private access), `D103` (docstrings).

**`__init__.py`**: `D104` (package docstring), `F401` (unused imports for re-exports).

**`conftest.py`**: `D100`, `D103` (docstrings), `FBT001/2` (boolean fixtures).

## Type Checking Pattern

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence  # TC001 compliant
```

`[lint.flake8-type-checking]` with `strict = true`. Exception: `pydantic.BaseModel` subclasses need runtime types.

## Formatter Settings

- Double quotes everywhere
- Space indent
- LF line endings
- Format code inside docstrings (`docstring-code-format = true`)

## Commands

```bash
# Lint (check only)
ruff check src/ tests/

# Lint + auto-fix
ruff check src/ tests/ --fix

# Format check
ruff format --check src/ tests/

# Format (write)
ruff format src/ tests/
```

## Common Errors and Fixes

| Error | Fix |
| ----- | --- |
| I002 | Add `from __future__ import annotations` at top |
| A002 | Rename parameter shadowing builtin (`type` → `item_type`) |
| D103 | Add docstring to public function |
| UP007 | Change `Optional[X]` to `X \| None` |
| TC001 | Move import into `if TYPE_CHECKING:` block |
| PLR0913 | Too many args - refactor or `# noqa: PLR0913` for MCP tools |
| BLE001 | Broad exception - `# noqa: BLE001` at MCP boundaries only |
