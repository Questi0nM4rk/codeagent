#!/usr/bin/env bash
# =============================================================================
# Format and Stage Hook
# =============================================================================
# Auto-formats changed files and re-stages them before other pre-commit hooks.
# Skipped in CI environments to avoid modifying the working tree.
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

# Format Python files with ruff if available
python_files=$(echo "$staged_files" | grep -E '\.py$' || true)
if [[ -n "$python_files" ]] && command -v ruff &>/dev/null; then
    echo "$python_files" | xargs -r ruff format --quiet 2>/dev/null || true
    echo "$python_files" | xargs -r git add
fi

# Format JavaScript/TypeScript files with prettier if available
js_files=$(echo "$staged_files" | grep -E '\.(js|jsx|ts|tsx|json|md|yaml|yml)$' || true)
if [[ -n "$js_files" ]] && command -v prettier &>/dev/null; then
    echo "$js_files" | xargs -r prettier --write --log-level error 2>/dev/null || true
    echo "$js_files" | xargs -r git add
fi

# Format Rust files with rustfmt if available
rust_files=$(echo "$staged_files" | grep -E '\.rs$' || true)
if [[ -n "$rust_files" ]] && command -v rustfmt &>/dev/null; then
    echo "$rust_files" | xargs -r rustfmt --edition 2021 2>/dev/null || true
    echo "$rust_files" | xargs -r git add
fi

# Format Go files with gofmt if available
go_files=$(echo "$staged_files" | grep -E '\.go$' || true)
if [[ -n "$go_files" ]] && command -v gofmt &>/dev/null; then
    echo "$go_files" | xargs -r gofmt -w 2>/dev/null || true
    echo "$go_files" | xargs -r git add
fi

# Format C/C++ files with clang-format if available
cpp_files=$(echo "$staged_files" | grep -E '\.(c|cpp|cc|cxx|h|hpp|hxx)$' || true)
if [[ -n "$cpp_files" ]] && command -v clang-format &>/dev/null; then
    echo "$cpp_files" | xargs -r clang-format -i 2>/dev/null || true
    echo "$cpp_files" | xargs -r git add
fi

# Format Lua files with stylua if available
lua_files=$(echo "$staged_files" | grep -E '\.lua$' || true)
if [[ -n "$lua_files" ]] && command -v stylua &>/dev/null; then
    echo "$lua_files" | xargs -r stylua 2>/dev/null || true
    echo "$lua_files" | xargs -r git add
fi

# Format shell scripts with shfmt if available
shell_files=$(echo "$staged_files" | grep -E '\.(sh|bash)$' || true)
if [[ -n "$shell_files" ]] && command -v shfmt &>/dev/null; then
    echo "$shell_files" | xargs -r shfmt -w -i 4 2>/dev/null || true
    echo "$shell_files" | xargs -r git add
fi

exit 0
