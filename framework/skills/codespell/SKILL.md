---
name: codespell
description: Codespell typo checker. Activates when dealing with spelling errors in code and documentation.
---

# Codespell Skill

Catches common typos in code, comments, and documentation.

## How It Runs

Pre-commit hook: `codespell --check-filenames`

Excludes: `poetry.lock`, `package-lock.json`, `.secrets.baseline`

## Common Catches

Catches misspellings in code, comments, strings, and filenames. Examples: reversed letters, doubled letters, missing letters in common words like "receive", "occurred", "separate", "definitely".

## False Positives

Add to `.codespellrc` or `pyproject.toml`:

```toml
[tool.codespell]
ignore-words-list = "crate"
skip = "*.lock,*.min.js"
```

Or inline:

```python
# codespell:ignore
variable_with_weird_spelling = "value"
```

## Commands

```bash
# Check
codespell .

# Check with filenames
codespell --check-filenames .

# Fix interactively
codespell -i 3 -w .
```
