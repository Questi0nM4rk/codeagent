---
name: bash
description: Bash and shell scripting expertise. Activates when working with .sh, .bash files or discussing shell scripts, CLI tools, or system administration.
---

# Bash/Shell Development Skill

Domain knowledge for shell scripting and CLI development.

## The Iron Law

```
SET -EUO PIPEFAIL + SHELLCHECK CLEAN + QUOTE EVERYTHING
Every script starts with strict mode. shellcheck passes. All variables quoted.
```

## Core Principle

> "Shell scripts fail silently. Strict mode and shellcheck make failures loud."

## When to Use

**Always:**
- Writing shell scripts (.sh, .bash)
- Creating CLI tools and wrappers
- Automating system tasks
- Writing installation scripts

**Exceptions (ask human partner):**
- POSIX-only environments (use `sh` not `bash`)
- Performance-critical scripts (consider Python/Go)

## Stack

| Component   | Technology   |
| ----------- | ------------ |
| Shells | Bash 5+, Zsh |
| Linting | shellcheck |
| Formatting | shfmt |
| Testing | bats-core |

## Essential Commands

```bash
# Lint
shellcheck script.sh
shellcheck -x script.sh  # Follow sources

# Format
shfmt -w script.sh
shfmt -d script.sh  # Diff mode

# Test
bats tests/
bats tests/test_script.bats
```

## Patterns

### Script Template

### Good Example
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

log_info() { echo "[INFO] $*"; }
log_error() { echo "[ERROR] $*" >&2; }
die() { log_error "$@"; exit 1; }

usage() {
    cat << EOF
Usage: ${SCRIPT_NAME} [options] <args>

Options:
    -h, --help      Show this help
    -v, --verbose   Verbose output
EOF
}

main() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true; shift ;;
            *) break ;;
        esac
    done

    # Main logic here
}

main "$@"
```
- Strict mode enabled
- Proper quoting throughout
- Clear structure with main function
- Error handling built-in

### Bad Example
```bash
#!/bin/bash

for file in $(ls *.txt); do
    cat $file
done
```
- No strict mode
- Parsing `ls` output (breaks on spaces)
- Unquoted variables
- No error handling

### Error Handling

### Good Example: Cleanup and Retry Logic
```bash
# Trap for cleanup
cleanup() {
    rm -f "${TEMP_FILE:-}"
}
trap cleanup EXIT

# Check command exists
command_exists() {
    command -v "$1" &> /dev/null
}

if ! command_exists docker; then
    die "Docker is required but not installed"
fi

# Retry with backoff
retry() {
    local max_attempts=$1 delay=$2
    shift 2
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if "$@"; then return 0; fi
        log_info "Attempt $attempt failed. Retrying in ${delay}s..."
        sleep "$delay"
        ((attempt++))
        delay=$((delay * 2))
    done
    return 1
}
```
- Cleanup trap for temp files
- Command existence check
- Retry logic for flaky operations

### Input Validation

```bash
# Required argument
[[ -z "${1:-}" ]] && die "Missing required argument"

# File exists
[[ -f "$file" ]] || die "File not found: $file"

# Directory exists
[[ -d "$dir" ]] || die "Directory not found: $dir"

# Is executable
[[ -x "$script" ]] || die "Not executable: $script"

# Numeric check
[[ "$value" =~ ^[0-9]+$ ]] || die "Not a number: $value"
```

### Arrays and Loops

### Good Example: Safe Array and File Iteration
```bash
# Array declaration
declare -a files=("file1.txt" "file2.txt")

# Iterate array (quoted!)
for file in "${files[@]}"; do
    echo "Processing: $file"
done

# Read file lines safely
while IFS= read -r line; do
    echo "$line"
done < "$file"

# Find and iterate (null-safe)
while IFS= read -r -d '' file; do
    echo "Found: $file"
done < <(find . -name "*.sh" -print0)
```
- Proper array quoting
- Safe file iteration
- Null-terminated find

### String Operations

```bash
# Substitution
filename="${path##*/}"      # basename
dirname="${path%/*}"        # dirname
extension="${file##*.}"     # extension
name="${file%.*}"           # name without extension

# Default values
value="${VAR:-default}"     # Use default if unset/empty
value="${VAR:=default}"     # Set and use default

# Comparison
[[ "$str" == "value" ]]     # Equal
[[ "$str" =~ ^[0-9]+$ ]]    # Regex match
[[ -z "$str" ]]             # Is empty
[[ -n "$str" ]]             # Is not empty
```

## Testing Patterns

### bats-core

### Good Example
```bash
#!/usr/bin/env bats

setup() {
    export TEMP_DIR="$(mktemp -d)"
}

teardown() {
    rm -rf "$TEMP_DIR"
}

@test "script prints usage with -h" {
    run ./script.sh -h
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage:" ]]
}

@test "script fails without arguments" {
    run ./script.sh
    [ "$status" -eq 1 ]
}

@test "script processes file" {
    echo "test content" > "$TEMP_DIR/test.txt"
    run ./script.sh "$TEMP_DIR/test.txt"
    [ "$status" -eq 0 ]
}
```
- Setup/teardown for isolation
- Status code verification
- Output pattern matching

## Common Rationalizations

| Excuse   | Reality   |
| -------- | --------- |
| "set -e is too strict" | It catches real errors. Handle expected failures explicitly. |
| "Quoting is ugly" | Unquoted vars break on spaces. Always quote. |
| "shellcheck is pedantic" | It prevents real bugs. Fix the warnings. |
| "It works on my machine" | It won't work with different filenames. Quote everything. |

## Red Flags - STOP

- Missing `set -euo pipefail`
- Unquoted variables: `$var` instead of `"$var"`
- Parsing `ls` output: `for f in $(ls)`
- Using backticks instead of `$()`
- `[ ]` instead of `[[ ]]`
- Missing `local` in functions
- `cd` without `|| exit`
- `rm -rf $VAR/` (unquoted, could delete root)

If you see these, stop and fix before continuing.

## Verification Checklist

- [ ] Script starts with `set -euo pipefail`
- [ ] `shellcheck script.sh` passes clean
- [ ] `shfmt -d script.sh` shows no diff
- [ ] All variables are quoted: `"$var"`
- [ ] Functions use `local` for variables
- [ ] Temp files cleaned up via trap
- [ ] Tests pass with `bats`

## Review Tools

```bash
shellcheck -x script.sh           # Lint (follow sources)
shfmt -d script.sh                # Format check
bats tests/                       # Run tests
bash -n script.sh                 # Syntax check only
```

## When Stuck

| Problem   | Solution   |
| --------- | ---------- |
| shellcheck false positive | Add `# shellcheck disable=SCXXXX` with comment explaining why |
| Need to continue on error | Use `command \|\| true` or `set +e` temporarily |
| Complex argument parsing | Use `getopts` or switch to Python |
| Associative arrays | Require Bash 4+, check version first |

## Related Skills

- `tdd` - Test-first development workflow
- `reviewer` - Uses shellcheck/shfmt for validation
- `python` - For complex scripts beyond shell capabilities
