---
name: taplo
description: Taplo TOML formatter. Activates when working with .toml files like pyproject.toml or Cargo.toml.
---

# Taplo Skill

TOML formatter and validator. Ensures consistent `pyproject.toml`, `Cargo.toml`, etc.

## How It Runs

Pre-commit hook: `taplo-format --check`

Also runs in `format-and-stage` hook locally (auto-formats and re-stages).

## What It Does

- Consistent key ordering
- Consistent quoting
- Expands inline arrays/tables when they exceed line width
- Normalizes whitespace
- Validates TOML syntax

## Known Issue: Stash Conflict

Taplo reformats `pyproject.toml` (e.g., expanding inline arrays to multiline), which can conflict with the `format-and-stage` hook's stash mechanism when untracked files exist. **Workaround**: gitignore all untracked files before committing.

## Commands

```bash
# Format check (CI)
taplo format --check .

# Format (write)
taplo format .

# Format single file
taplo format pyproject.toml

# Validate syntax only
taplo lint .
```
