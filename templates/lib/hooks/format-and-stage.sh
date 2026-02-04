#!/usr/bin/env bash
# =============================================================================
# Format and Stage Hook
# =============================================================================
# Auto-formats changed files and re-stages them before other pre-commit hooks.
# Skipped in CI environments to avoid modifying the working tree.
#
# Uses git stash to preserve unstaged changes during formatting.
# =============================================================================

set -euo pipefail

# Skip in CI environments
if [[ "${CI:-}" == "true" ]] || [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
    echo "Skipping format-and-stage in CI environment"
    exit 0
fi

# Get staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACMR)

if [[ -z "$staged_files" ]]; then
    exit 0
fi

# Stash unstaged changes to prevent accidentally staging them
stashed=false
if ! git diff --quiet; then
    git stash push --keep-index --quiet -m "format-and-stage: temp stash"
    stashed=true
fi

# Cleanup function to restore stash on exit
cleanup() {
    if [[ "$stashed" == "true" ]]; then
        git stash pop --quiet 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Format Python files with ruff if available
python_files=$(echo "$staged_files" | grep -E '\.py$' || true)
if [[ -n "$python_files" ]] && command -v ruff &>/dev/null; then
    echo "$python_files" | xargs ruff format --quiet 2>/dev/null || true
    echo "$python_files" | xargs git add
fi

# Format JavaScript/TypeScript files with prettier if available
js_files=$(echo "$staged_files" | grep -E '\.(js|jsx|ts|tsx|json|md|yaml|yml)$' || true)
if [[ -n "$js_files" ]] && command -v prettier &>/dev/null; then
    echo "$js_files" | xargs prettier --write --log-level error 2>/dev/null || true
    echo "$js_files" | xargs git add
fi

# Format Rust files with rustfmt if available
rust_files=$(echo "$staged_files" | grep -E '\.rs$' || true)
if [[ -n "$rust_files" ]] && command -v rustfmt &>/dev/null; then
    echo "$rust_files" | xargs rustfmt --edition 2021 2>/dev/null || true
    echo "$rust_files" | xargs git add
fi

# Format Go files with gofmt if available
go_files=$(echo "$staged_files" | grep -E '\.go$' || true)
if [[ -n "$go_files" ]] && command -v gofmt &>/dev/null; then
    echo "$go_files" | xargs gofmt -w 2>/dev/null || true
    echo "$go_files" | xargs git add
fi

# Format C/C++ files with clang-format if available
cpp_files=$(echo "$staged_files" | grep -E '\.(c|cpp|cc|cxx|h|hpp|hxx)$' || true)
if [[ -n "$cpp_files" ]] && command -v clang-format &>/dev/null; then
    echo "$cpp_files" | xargs clang-format -i 2>/dev/null || true
    echo "$cpp_files" | xargs git add
fi

# Format Lua files with stylua if available
lua_files=$(echo "$staged_files" | grep -E '\.lua$' || true)
if [[ -n "$lua_files" ]] && command -v stylua &>/dev/null; then
    echo "$lua_files" | xargs stylua 2>/dev/null || true
    echo "$lua_files" | xargs git add
fi

# Format shell scripts with shfmt if available
# Indent can be configured via SHFMT_INDENT env var (default: 4)
shell_files=$(echo "$staged_files" | grep -E '\.(sh|bash)$' || true)
if [[ -n "$shell_files" ]] && command -v shfmt &>/dev/null; then
    indent="${SHFMT_INDENT:-4}"
    echo "$shell_files" | xargs shfmt -w -i "$indent" 2>/dev/null || true
    echo "$shell_files" | xargs git add
fi

exit 0
