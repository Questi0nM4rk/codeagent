#!/bin/bash
# ============================================
# CodeAgent Index File Hook
# Tracks changed files for incremental indexing
# Called by PostToolUse hook when files are written
# ============================================

FILE="$1"
CODEAGENT_HOME="${CODEAGENT_HOME:-$HOME/.codeagent}"
CHANGED_FILES="$CODEAGENT_HOME/data/changed-files.txt"

if [ -z "$FILE" ]; then
  exit 0
fi

# Create data directory if needed
mkdir -p "$CODEAGENT_HOME/data"

# Check if file type is supported (9 languages)
case "$FILE" in
  # Original languages
  *.cs | *.cpp | *.c | *.h | *.hpp | *.rs | *.lua | *.sh)
    echo "$FILE" >>"$CHANGED_FILES"
    ;;
  # New languages (Python, TypeScript, JavaScript, Go)
  *.py | *.ts | *.tsx | *.js | *.jsx | *.go)
    echo "$FILE" >>"$CHANGED_FILES"
    ;;
esac

# Deduplicate the file list
if [ -f "$CHANGED_FILES" ]; then
  sort -u "$CHANGED_FILES" -o "$CHANGED_FILES"
fi

exit 0
