# Lint Exception Policy

## Philosophy

> "Everything is an error or it's ignored."

AI agents tend to add inline suppressions (`# noqa`, `# type: ignore`, etc.) as quick fixes rather than addressing root causes. This policy prevents that by:

1. **Blocking inline suppression comments** - The pre-commit hook `detect-suppression-comments.sh` rejects them
2. **Ignoring suppression comments at tool level** - Tools are configured to ignore inline comments even if they slip through
3. **Centralizing exceptions in config files** - Only the user can modify these files

## How It Works

| Tool | Inline Comment | Ignored? | Exception File |
|------|---------------|----------|----------------|
| Ruff | `# noqa` | ✅ Yes (`ignore-noqa = true`) | `ruff.toml` `[lint.per-file-ignores]` |
| Semgrep | `# nosemgrep` | ✅ Yes (`--disable-nosem`) | `.semgrepignore` |
| detect-secrets | `# pragma: allowlist secret` | ⚠️ Detected | `.secrets.baseline` |
| Mypy | `# type: ignore` | ⚠️ Detected | `mypy.ini` or `pyproject.toml` |
| ESLint | `// eslint-disable` | ⚠️ Detected | `.eslintrc` |
| Shellcheck | `# shellcheck disable` | ⚠️ Detected | `.shellcheckrc` |

## For AI Agents

When you encounter a lint error that seems like a false positive:

1. **DO NOT** add `# noqa`, `# type: ignore`, or any suppression comment
2. **DO** explain the issue to the user
3. **DO** ask the user to add an exception to the appropriate config file

Example response:

```text
This line triggers ruff rule S106 (hardcoded password), but this is a test
file with fake credentials.

To allow this, please add to ruff.toml:

[lint.per-file-ignores]
"tests/test_auth.py" = ["S106"]
```

## Exception Files (User-Controlled)

### Ruff (`ruff.toml`)

```toml
[lint.per-file-ignores]
# Test files can use assert and magic numbers
"tests/**/*.py" = ["S101", "PLR2004"]

# CLI files need boolean args for Typer
"**/cli/**/*.py" = ["FBT001", "FBT003"]
```

### Semgrep (`.semgrepignore`)

```gitignore
# Ignore test fixtures
tests/fixtures/

# Ignore specific file
src/legacy/old_auth.py
```

### detect-secrets (`.secrets.baseline`)

Managed via CLI:

```bash
# Scan and create baseline
detect-secrets scan > .secrets.baseline

# Audit and mark false positives
detect-secrets audit .secrets.baseline
```

### Mypy (`pyproject.toml`)

```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_decorators = false
```

## Protected Files

These config files should NOT be edited by AI agents without explicit user approval:

- `ruff.toml` / `pyproject.toml` (ruff config)
- `.semgrepignore`
- `.secrets.baseline`
- `mypy.ini` / `pyproject.toml` (mypy config)
- `.eslintrc.*`
- `.shellcheckrc`
- `biome.json`

## Rationale

1. **Prevents "ignore fatigue"** - When suppression is easy, agents add them without thinking
2. **Forces root cause analysis** - Is this a real issue or a config problem?
3. **Maintains audit trail** - Changes to config files are tracked in git
4. **Keeps code clean** - No noisy inline comments

## When Exceptions Are Appropriate

✅ **Appropriate:**

- Framework limitations (e.g., Typer requires boolean args)
- Test isolation patterns (e.g., imports inside test functions)
- Intentional security in test fixtures (e.g., fake credentials)

❌ **Not Appropriate:**

- "It's too hard to fix"
- "The rule is annoying"
- "I'll fix it later"
