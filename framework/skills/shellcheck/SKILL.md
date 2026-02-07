---
name: shellcheck
description: Shell script linting and formatting via shellcheck + shfmt. Activates when working with .sh, .bash, .zsh files.
---

# Shellcheck + Shfmt Skill

Two tools: shellcheck (lint), shfmt (format). Both in pre-commit hooks.

## Shellcheck

Static analysis for shell scripts. Catches quoting bugs, undefined variables, portability issues.

### Pre-commit Config

- `--severity=info` - all severity levels
- `-x` - follow sourced files

### Every Script Must Have

```bash
#!/bin/bash
set -euo pipefail
```

### Common Errors

| Code | Issue | Fix |
| ---- | ----- | --- |
| SC2086 | Unquoted variable | `"$var"` not `$var` |
| SC2046 | Unquoted command sub | `"$(cmd)"` not `$(cmd)` |
| SC2004 | Unnecessary `$` in arithmetic | `$((x + 1))` not `$(($x + 1))` |
| SC2155 | Declare and assign separately | `local x; x=$(cmd)` |
| SC2034 | Variable appears unused | Remove or export |
| SC2064 | Trap quotes at definition | Use single quotes in trap |

### Suppressing (rare)

```bash
# shellcheck disable=SC2317  # Function invoked via trap
```

## Shfmt

Formatter for shell scripts.

### Settings (via pre-commit args)

- `-i 2` - 2-space indent
- `-ci` - indent switch cases
- `-bn` - binary ops start of line
- `-d` - diff mode (check only in CI)

### Commands

```bash
# Lint
shellcheck script.sh

# Format check
shfmt -d -i 2 -ci -bn script.sh

# Format (write)
shfmt -w -i 2 -ci -bn script.sh
```
