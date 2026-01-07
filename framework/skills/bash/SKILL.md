---
name: bash
description: Bash and shell scripting expertise. Activates when working with .sh, .bash files or discussing shell scripts, CLI tools, or system administration.
---

# Bash/Shell Development Skill

Domain knowledge for shell scripting and CLI development.

## Stack

- **Shells**: Bash 5+, Zsh
- **Linting**: shellcheck
- **Formatting**: shfmt
- **Testing**: bats-core

## Commands

### Running

```bash
# Run script
bash script.sh
./script.sh  # requires chmod +x

# Debug mode
bash -x script.sh      # Print commands
bash -v script.sh      # Print input lines
bash -n script.sh      # Syntax check only

# Strict mode
set -euo pipefail
```

### Linting and Formatting

```bash
# shellcheck
shellcheck script.sh
shellcheck -x script.sh  # Follow sources
shellcheck -f gcc script.sh
shellcheck -s bash script.sh

# shfmt
shfmt -w script.sh
shfmt -d script.sh      # Diff mode
shfmt -i 4 script.sh    # 4 space indent
shfmt -l .              # List files that differ
```

### Testing

```bash
# bats
bats tests/
bats tests/test_script.bats
bats --tap tests/
```

## Patterns

### Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Script description
# Usage: script.sh [options] <args>

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

die() {
    log_error "$@"
    exit 1
}

usage() {
    cat << EOF
Usage: ${SCRIPT_NAME} [options] <args>

Options:
    -h, --help      Show this help
    -v, --verbose   Verbose output
EOF
}

main() {
    local verbose=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    # Main logic here
}

main "$@"
```

### Error Handling

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
    local max_attempts=$1
    local delay=$2
    shift 2
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if "$@"; then
            return 0
        fi
        log_warn "Attempt $attempt failed. Retrying in ${delay}s..."
        sleep "$delay"
        ((attempt++))
        delay=$((delay * 2))
    done

    return 1
}
```

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

```bash
# Array declaration
declare -a files=("file1.txt" "file2.txt" "file3.txt")

# Iterate array
for file in "${files[@]}"; do
    echo "Processing: $file"
done

# Read file lines
while IFS= read -r line; do
    echo "$line"
done < "$file"

# Find and iterate
while IFS= read -r -d '' file; do
    echo "Found: $file"
done < <(find . -name "*.sh" -print0)
```

### Functions

```bash
# Function with local variables
process_file() {
    local file="$1"
    local -r readonly_var="constant"

    [[ -f "$file" ]] || return 1

    # Process file
    echo "Processing: $file"
}

# Return values
get_value() {
    local result="computed value"
    echo "$result"
}
value=$(get_value)

# Multiple return values
get_stats() {
    local -n _count=$1
    local -n _size=$2
    _count=10
    _size=1024
}
get_stats count size
echo "Count: $count, Size: $size"
```

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

# String comparison
[[ "$str" == "value" ]]     # Equal
[[ "$str" != "value" ]]     # Not equal
[[ "$str" =~ ^[0-9]+$ ]]    # Regex match
[[ -z "$str" ]]             # Is empty
[[ -n "$str" ]]             # Is not empty
```

## Testing Patterns

### bats-core

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
    [[ "$output" =~ "Processing:" ]]
}
```

## Review Tools

```bash
# Lint
shellcheck -x script.sh

# Format check
shfmt -d script.sh

# Security scan (basic)
grep -n 'eval\|exec' script.sh
```

## File Organization

```
scripts/
├── bin/
│   ├── main-script.sh
│   └── helper.sh
├── lib/
│   ├── common.sh
│   └── logging.sh
├── tests/
│   └── test_main.bats
└── README.md
```

## Common Conventions

- Always use `set -euo pipefail`
- Quote all variables: `"$var"`
- Use `[[ ]]` instead of `[ ]`
- Use `$(command)` instead of backticks
- Prefer `local` for function variables
- Use `readonly` for constants
- Check exit codes explicitly when needed
- Use `shellcheck` directives for false positives
