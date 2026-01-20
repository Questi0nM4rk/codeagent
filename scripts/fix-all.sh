#!/usr/bin/env bash
# =============================================================================
# Auto-fix all linting/formatting issues that can be fixed automatically
# =============================================================================
# Usage: ./scripts/fix-all.sh [--check]
#   --check  Dry-run mode (show what would be fixed without changing files)
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

CHECK_MODE=false
if [[ "${1:-}" == "--check" ]]; then
  CHECK_MODE=true
  echo -e "${BLUE}Running in check mode (dry-run)${NC}"
fi

# Track what was fixed
FIXED=()
FAILED=()
SKIPPED=()

run_fixer() {
  local name="$1"
  local check_cmd="$2"
  local fix_cmd="$3"
  local files="${4:-}"

  echo -e "\n${BLUE}━━━ $name ━━━${NC}"

  # Check if there are files to process
  if [[ -n "$files" ]]; then
    # shellcheck disable=SC2086
    if ! ls $files &>/dev/null 2>&1; then
      echo -e "${YELLOW}Skipped (no matching files)${NC}"
      SKIPPED+=("$name")
      return 0
    fi
  fi

  if $CHECK_MODE; then
    if eval "$check_cmd" 2>&1; then
      echo -e "${GREEN}OK${NC}"
    else
      echo -e "${YELLOW}Would fix issues${NC}"
      FIXED+=("$name")
    fi
  else
    if eval "$fix_cmd" 2>&1; then
      echo -e "${GREEN}Fixed${NC}"
      FIXED+=("$name")
    else
      echo -e "${RED}Failed${NC}"
      FAILED+=("$name")
    fi
  fi
}

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Auto-Fix All Linting Issues                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# =============================================================================
# Shell Scripts (shfmt)
# =============================================================================
SHELL_DIRS="bin/ scripts/ framework/hooks/ mcps/ tests/ .githooks/"
SHELL_FILES="install.sh uninstall.sh"

run_fixer "shfmt (shell formatting)" \
  "shfmt -i 2 -ci -bn -d $SHELL_DIRS $SHELL_FILES" \
  "shfmt -i 2 -ci -bn -w $SHELL_DIRS $SHELL_FILES"

# =============================================================================
# Python (ruff)
# =============================================================================
run_fixer "ruff (python lint)" \
  "ruff check --select=ALL --ignore=D,ANN,COM812,ISC001 ." \
  "ruff check --fix --select=ALL --ignore=D,ANN,COM812,ISC001 ." \
  "**/*.py"

run_fixer "ruff format (python)" \
  "ruff format --check ." \
  "ruff format ." \
  "**/*.py"

# =============================================================================
# TypeScript/JavaScript (biome)
# =============================================================================
run_fixer "biome (typescript/javascript)" \
  "npx @biomejs/biome check --error-on-warnings ." \
  "npx @biomejs/biome check --apply --error-on-warnings ." \
  "**/*.{ts,tsx,js,jsx}"

# =============================================================================
# Markdown (markdownlint)
# =============================================================================
run_fixer "markdownlint (markdown)" \
  "npx markdownlint-cli2 '**/*.md'" \
  "npx markdownlint-cli2 --fix '**/*.md'" \
  "**/*.md"

# =============================================================================
# Trailing whitespace & line endings (pre-commit hooks)
# =============================================================================
if command -v pre-commit &>/dev/null; then
  echo -e "\n${BLUE}━━━ pre-commit auto-fixers ━━━${NC}"

  if $CHECK_MODE; then
    echo -e "${YELLOW}Run without --check to apply fixes${NC}"
  else
    # These hooks auto-fix by default
    pre-commit run trailing-whitespace --all-files || true
    pre-commit run end-of-file-fixer --all-files || true
    pre-commit run mixed-line-ending --all-files || true
    echo -e "${GREEN}Applied whitespace/line-ending fixes${NC}"
    FIXED+=("whitespace/line-endings")
  fi
else
  SKIPPED+=("pre-commit hooks (not installed)")
fi

# =============================================================================
# Summary
# =============================================================================
echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                         Summary                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

if [[ ${#FIXED[@]} -gt 0 ]]; then
  echo -e "${GREEN}Fixed:${NC} ${FIXED[*]}"
fi
if [[ ${#SKIPPED[@]} -gt 0 ]]; then
  echo -e "${YELLOW}Skipped:${NC} ${SKIPPED[*]}"
fi
if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo -e "${RED}Failed:${NC} ${FAILED[*]}"
  exit 1
fi

echo -e "\n${BLUE}Note:${NC} shellcheck has no auto-fix. Run 'shellcheck <file>' to see issues."
echo -e "${BLUE}Tip:${NC} Run 'pre-commit run --all-files' to verify all checks pass."
