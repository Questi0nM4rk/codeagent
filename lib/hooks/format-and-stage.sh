#!/bin/bash
# ============================================
# Format and Stage Hook
# Auto-formats staged files and re-stages them
# Skipped in CI (GITHUB_ACTIONS=true)
# ============================================

set -euo pipefail

# Skip in CI - formatting is checked, not applied
if [ "${GITHUB_ACTIONS:-false}" = "true" ] || [ "${CI:-false}" = "true" ]; then
  exit 0
fi

# Get list of staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACMR)

if [ -z "$staged_files" ]; then
  exit 0
fi

format_file() {
  local file="$1"

  [ ! -f "$file" ] && return 0

  case "$file" in
    *.py)
      ruff format "$file" 2>/dev/null || true
      ;;
    *.rs)
      rustfmt "$file" 2>/dev/null || true
      ;;
    *.cpp | *.c | *.h | *.hpp | *.cc)
      clang-format -i "$file" 2>/dev/null || true
      ;;
    *.lua)
      stylua "$file" 2>/dev/null || true
      ;;
    *.sh | *.bash)
      shfmt -w -i 2 -ci -bn "$file" 2>/dev/null || true
      ;;
    *.ts | *.tsx | *.js | *.jsx | *.json | *.css | *.scss | *.md | *.yaml | *.yml)
      npx biome format --write "$file" 2>/dev/null || npx prettier --write "$file" 2>/dev/null || true
      ;;
    *.go)
      gofmt -w "$file" 2>/dev/null || true
      ;;
    *.cs)
      dotnet format --include "$file" 2>/dev/null || true
      ;;
  esac
}

# Format each staged file
for file in $staged_files; do
  format_file "$file"
done

# Re-stage formatted files
for file in $staged_files; do
  [ -f "$file" ] && git add "$file"
done

exit 0
