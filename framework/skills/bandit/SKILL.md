---
name: bandit
description: Bandit Python security linter. Activates when dealing with Python security issues or bandit findings.
---

# Bandit Skill

Python-specific security linter. Complementary to semgrep - focuses on Python idioms.

## How It Runs

Pre-commit hook: `bandit -ll -ii -r` (excludes tests).

- `-ll` = low severity and above (all severities)
- `-ii` = low confidence and above (all confidence)
- `-r` = recursive

## Common Findings

| Code | Issue | Fix |
| ---- | ----- | --- |
| B101 | `assert` used outside tests | Use proper validation: `if not x: raise ValueError()` |
| B105 | Hardcoded password | Move to env var |
| B108 | Hardcoded `/tmp` path | Use `tempfile.mkdtemp()` |
| B301 | Pickle usage | Use JSON or msgpack |
| B403 | Import pickle | Don't import it |
| B602 | `subprocess` with `shell=True` | Use list args: `subprocess.run(["cmd", "arg"])` |
| B608 | SQL injection via string format | Use parameterized queries |

## Suppressing

```python
x = subprocess.run(cmd, shell=False)  # nosec B603 - shell=False is safe
```

Use `# nosec BXXX` with the specific code and a reason.

## Commands

```bash
# Scan
bandit -r src/ -ll -ii

# Scan with verbose
bandit -r src/ -ll -ii -v

# Specific tests only
bandit -r src/ -t B602,B608
```
