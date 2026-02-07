---
name: vulture
description: Vulture dead code detection for Python. Activates when cleaning up unused code.
---

# Vulture Skill

Finds unused Python code (functions, variables, imports, classes).

## How It Runs

Pre-commit hook: `vulture --min-confidence 80 .` (pass_filenames: false - scans whole project).

80% confidence threshold means it only reports when it's fairly sure code is unused.

## What It Catches

- Unused functions and methods
- Unused variables and attributes
- Unused imports (complementary to ruff's F401)
- Unused classes
- Unreachable code after return/raise

## False Positives

Vulture can't detect dynamic usage (reflection, `getattr`, plugin systems). Common false positives:

- MCP tool functions (called via MCP protocol, not direct import)
- CLI entry points
- Pytest fixtures (used by injection)
- Abstract methods / protocol methods

### Whitelist

Create a `whitelist.py` to suppress false positives:

```python
# whitelist.py - vulture false positive suppressions
from codeagent.mcp.server import handle_search  # noqa: F401
from codeagent.cli.main import app  # noqa: F401
```

Then run: `vulture . whitelist.py`

## Commands

```bash
# Scan
vulture . --min-confidence 80

# More aggressive (lower confidence)
vulture . --min-confidence 60

# With whitelist
vulture . whitelist.py --min-confidence 80
```
