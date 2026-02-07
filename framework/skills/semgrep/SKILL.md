---
name: semgrep
description: Semgrep SAST security scanner. Activates when dealing with security issues, vulnerability scanning, or CI security checks.
---

# Semgrep Skill

Static Application Security Testing (SAST). Catches security vulnerabilities via pattern matching.

## How It Runs

- **Pre-commit**: `semgrep --config auto --error --jobs 1` (excludes tests)
- **CI**: Separate step after pre-commit (runs in parallel with lint)
- **CI command**: `semgrep --config auto --error --exclude tests/`

`--config auto` uses Semgrep's curated ruleset (OWASP top 10, language-specific).

## What It Catches

- SQL injection patterns
- XSS vulnerabilities
- Command injection
- Path traversal
- Hardcoded secrets/credentials
- Insecure deserialization
- SSRF patterns
- Dangerous function calls (`eval`, `exec`, `os.system`)

## Common Findings

| Finding | Fix |
| ------- | --- |
| `python.lang.security.audit.exec-detected` | Don't use `exec()`. Refactor. |
| `python.lang.security.audit.eval-detected` | Don't use `eval()`. Use `ast.literal_eval()` if needed. |
| `python.lang.security.audit.subprocess-shell-true` | Use `subprocess.run(["cmd", "arg"])` not `shell=True` |
| `python.lang.security.deserialization.avoid-pickle` | Use JSON or msgpack instead |
| `generic.secrets.security.detected-generic-secret` | Move to env var or secrets manager |

## Suppressing (very rare)

```python
# nosemgrep: python.lang.security.audit.exec-detected
exec(trusted_code)  # Reason: sandboxed execution in test harness
```

Requires explicit justification. Security suppressions are reviewed in PR.

## Commands

```bash
# Scan current directory
semgrep --config auto --error

# Scan specific path
semgrep --config auto --error src/

# Exclude tests
semgrep --config auto --error --exclude tests/

# Verbose (show rule IDs)
semgrep --config auto --error --verbose
```
