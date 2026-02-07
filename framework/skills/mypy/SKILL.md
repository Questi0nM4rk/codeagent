---
name: mypy
description: Mypy strict static type checking for Python. Activates when dealing with type errors, mypy configuration, or type stub issues.
---

# Mypy Skill

Static type checker for Python. Runs in `--strict` mode via pre-commit hook.

## How It Runs

Pre-commit hook using `mirrors-mypy` v1.14.1. Not via `uv run mypy` - the hook manages its own virtualenv.

Args: `--strict --warn-unreachable --warn-redundant-casts --warn-unused-ignores --no-implicit-reexport --disallow-untyped-decorators`

## Strict Mode Means

- All functions must have type annotations
- No `Any` implicit or explicit
- No untyped function calls
- No untyped class definitions
- No untyped decorators
- Warn on unreachable code
- No implicit re-exports (use `__all__` or explicit import)

## Mypy vs Pyright

Both run. They catch different things:

| Aspect | mypy | pyright |
| ------ | ---- | ------- |
| Mode | `--strict` | `standard` |
| Runs via | pre-commit hook | `uv run pyright` / CI |
| Config | CLI args in hook | `pyproject.toml [tool.pyright]` |
| Strengths | Protocol checking, plugin system | Speed, inference, IDE integration |

## Common Errors and Fixes

| Error | Fix |
| ----- | --- |
| `Missing return statement` | Add explicit `return None` or `-> None` |
| `has no attribute` | Check spelling, or add type stub |
| `Incompatible types in assignment` | Fix the type or add proper annotation |
| `Missing type parameters for generic` | Add `[T]` to generic types |
| `Import of X is not allowed` | Use `from __future__ import annotations` + `TYPE_CHECKING` |
| `Module has no attribute` | Install type stubs: `uv add types-X --dev` |

## Type Stubs

When mypy can't find types for a library:

```bash
# Search for stubs
uv search types-requests

# Install
uv add types-requests types-pyyaml --dev
```

Common stubs: `types-requests`, `types-pyyaml`, `types-toml`, `types-setuptools`.

If no stub exists, add to pre-commit hook's `additional_dependencies` or use `# type: ignore[import-untyped]` with a comment explaining why.

## Suppressing

```python
x = some_untyped_lib.call()  # type: ignore[no-any-return]  # no stubs for lib
```

Always include the error code and a comment. Bare `# type: ignore` is not acceptable.

## Commands

```bash
# Full strict check
mypy src/ --strict

# Check single file
mypy src/codeagent/mcp/server.py --strict

# Show error codes (for targeted ignore)
mypy src/ --strict --show-error-codes
```
