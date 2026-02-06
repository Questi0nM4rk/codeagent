---
name: quality-gates
description: Code quality enforcement via ai-guardrails. Activates when dealing with CI, pre-commit hooks, linting configuration, or code quality failures.
---

# Quality Gates Skill

How code quality is enforced in this ecosystem. All enforcement lives in **ai-guardrails**, not in individual projects.

## The Iron Law

```
ai-guardrails owns ALL quality enforcement.
Projects consume it via `ai-guardrails-init`.
Never hack quality configs directly in a project.
```

## Architecture

```
ai-guardrails repo (upstream)
  ├── configs/          → ruff.toml, biome.json, etc.
  ├── templates/
  │   ├── pre-commit/   → hook definitions per language
  │   └── workflows/    → CI templates (check.yml)
  └── lib/hooks/        → format-and-stage, dangerous-command-check
        │
        ▼  ai-guardrails-init --force --ci
        │
project repo (consumer)
  ├── .pre-commit-config.yaml  (generated)
  ├── .github/workflows/check.yml (installed)
  ├── .editorconfig (installed)
  └── ruff.toml (installed, if Python)
```

## Adding or Changing Quality Rules

1. **Edit in ai-guardrails repo** (never in the consumer project)
2. Test: `bats tests/bats/` and `pytest tests/`
3. Commit, push, PR in ai-guardrails
4. In consumer project: `ai-guardrails-init --force --ci`
5. Verify: `pre-commit run --all-files`

## Pre-commit Hooks (Execution Order)

```
format-and-stage  → auto-format + re-stage (local only, skipped in CI)
gitleaks          → secret detection
detect-secrets    → enhanced secret scanning
semgrep           → SAST security scan
ruff              → Python lint (ALL rules, --no-fix in CI)
ruff-format       → Python format check
bandit            → Python security
vulture           → Python dead code
biome             → TS/JS lint+format (if detected)
shellcheck        → Shell lint (if detected)
shfmt             → Shell format (if detected)
markdownlint      → Markdown lint
trailing-whitespace, end-of-file, merge-conflicts, large-files
```

## CI Pipeline (check.yml)

Two jobs run in parallel:

### lint

- Pre-commit all hooks (skip format-and-stage, semgrep)
- Semgrep separately (`--config auto --error`)

### test

- `uv sync --all-extras`
- `uv run pytest tests/ --cov=src --cov-branch --cov-fail-under=85`
- `uv run pyright src/`

## Ruff Configuration Highlights

- `select = ["ALL"]` — every rule enabled, disable explicitly
- `line-length = 88`
- `target-version = "py311"`
- `from __future__ import annotations` required (`I002`)
- Key per-file-ignores: tests get relaxed `S101`, `PLR2004`, `ARG`
- `__init__.py` allows unused imports (`F401`)

## Common Commands

```bash
# Run all checks locally
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Python lint + format
uv run ruff check src/ tests/ --fix
uv run ruff format src/ tests/

# Type check
uv run pyright src/
uv run mypy src/ --strict

# Test with coverage
uv run pytest tests/ --cov=src --cov-fail-under=85
```

## When Pre-commit Fails

1. Read the error — it tells you exactly what's wrong
2. Fix in your code (never disable the check)
3. `git add -u` and commit again
4. If a rule is genuinely wrong for your project, fix it **in ai-guardrails**

## Acceptable Suppressions

These are the ONLY acceptable `# noqa:` patterns:

| Pattern | When |
| ------- | ---- |
| `# noqa: BLE001` | MCP tool boundaries (catch-all for tool error response) |
| `# noqa: PLR0913` | MCP tool functions (many parameters by design) |
| `# noqa: PLC0415` | Lazy imports for performance |
| `# noqa: PLW0603` | Dependency injection via global |

Everything else: fix the code, don't suppress the warning.
