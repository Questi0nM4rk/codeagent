#!/usr/bin/env bash
# =============================================================================
# Detect Suppression Comments Hook
# =============================================================================
# Philosophy: "Everything is an error or it's ignored"
# Suppression comments create gray areas - fix the issue or change the config.
#
# Detects and rejects common lint/type suppression patterns:
# - Python: # noqa, # type: ignore, # pylint: disable, # pragma: no cover
# - JavaScript/TypeScript: // eslint-disable, // @ts-ignore, // @ts-expect-error
# - C/C++: // NOLINT, #pragma warning(disable
# - C#: #pragma warning disable, // ReSharper disable
# - Rust: #[allow(...)], #![allow(...)]
# - Go: //nolint
# - Semgrep: # nosemgrep, // nosemgrep
# - Shell: # shellcheck disable
# - Lua: ---@diagnostic disable
# =============================================================================

set -euo pipefail

# Exit code
exit_code=0

# Patterns to detect (extended regex)
# Each pattern is on its own line for maintainability
patterns=(
  # Python
  '#[[:space:]]*noqa'
  '#[[:space:]]*type:[[:space:]]*ignore'
  '#[[:space:]]*pylint:[[:space:]]*disable'
  '#[[:space:]]*pragma:[[:space:]]*no[[:space:]]*cover'
  '#[[:space:]]*pragma:[[:space:]]*allowlist' # detect-secrets allowlist
  '#[[:space:]]*mypy:[[:space:]]*ignore'

  # JavaScript/TypeScript
  '//[[:space:]]*eslint-disable'
  '//[[:space:]]*@ts-ignore'
  '//[[:space:]]*@ts-expect-error'
  '//[[:space:]]*@ts-nocheck'
  '/\*[[:space:]]*eslint-disable'

  # C/C++
  '//[[:space:]]*NOLINT'
  '#pragma[[:space:]]+warning[[:space:]]*\([[:space:]]*disable'

  # C#
  '#pragma[[:space:]]+warning[[:space:]]+disable'
  '//[[:space:]]*ReSharper[[:space:]]+disable'

  # Rust (allow attributes)
  '#\[allow\('
  '#!\[allow\('

  # Go
  '//[[:space:]]*nolint'

  # Semgrep
  '#[[:space:]]*nosemgrep'
  '//[[:space:]]*nosemgrep'

  # Shell
  '#[[:space:]]*shellcheck[[:space:]]+disable'

  # Lua
  '---@diagnostic[[:space:]]+disable'
)

# Build combined pattern
combined_pattern=$(printf '%s\n' "${patterns[@]}" | paste -sd '|' -)

# Check each file passed to the hook
for file in "$@"; do
  if [[ ! -f "$file" ]]; then
    continue
  fi

  # Search for suppression comments
  if grep -EnH "$combined_pattern" "$file" 2>/dev/null; then
    exit_code=1
  fi
done

if [[ "$exit_code" -ne 0 ]]; then
  echo ""
  echo "ERROR: Suppression comments detected!"
  echo ""
  echo "Philosophy: 'Everything is an error or it's ignored'"
  echo ""
  echo "Instead of suppressing warnings:"
  echo "  1. Fix the underlying issue, OR"
  echo "  2. Update the linter configuration to ignore this rule globally"
  echo ""
  echo "If this is a false positive, add a comment explaining WHY the"
  echo "suppression is necessary and update .pre-commit-config.yaml to"
  echo "exclude this specific file/pattern from this check."
  echo ""
fi

exit "$exit_code"
