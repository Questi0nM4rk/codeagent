---
name: pyright
description: Pyright type checker for Python. Activates when dealing with type inference issues, pyright configuration, or CI type checking.
---

# Pyright Skill

Fast Python type checker by Microsoft. Runs in CI via `uv run pyright src/`.

## Config

In `pyproject.toml`:

```toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "standard"
strictListInference = true
strictDictionaryInference = true
reportMissingTypeStubs = false
```

## Standard vs Strict

We use `standard` mode (not `strict`). Mypy handles strict checking via pre-commit. Pyright in standard mode catches different issues - especially around type inference and narrowing.

| Mode | What it catches |
| ---- | --------------- |
| basic | Obvious errors only |
| standard | Inference issues, missing returns, unreachable code |
| strict | Everything mypy strict does + more (too noisy with both) |

## Pyright vs Mypy

| Feature | pyright | mypy |
| ------- | ------- | ---- |
| Speed | Very fast | Slower |
| Inference | Better (stricter narrowing) | Good |
| Protocol support | Good | Better |
| Plugin system | No | Yes (pydantic, django) |
| IDE | VS Code native | PyCharm native |

## Common Errors

| Error | Fix |
| ----- | --- |
| `Cannot access member X for type Y` | Check type narrowing, add isinstance check |
| `Type X is not assignable to type Y` | Fix annotation or add proper cast |
| `Return type does not match` | Make return type match all code paths |
| `reportMissingTypeStubs` | Disabled in config - install stubs if you want |
| `reportGeneralTypeIssues` | Real type error - fix the code |

## Commands

```bash
# Type check src
uv run pyright src/

# Type check specific file
uv run pyright src/codeagent/mcp/server.py

# Verbose output
uv run pyright src/ --verbose
```

## Suppressing (rare)

```python
x = thing()  # pyright: ignore[reportGeneralTypeIssues]  # reason here
```

Include the specific error code and reason. Bare `# pyright: ignore` is not acceptable.
