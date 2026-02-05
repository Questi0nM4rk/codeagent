#!/bin/bash
# Worktree Context Hook for Claude Code
# Injects context about the current worktree into Claude's awareness
#
# This hook reads .worktree-context.json from the worktree root and outputs
# context that helps Claude understand which worktree it's in and what it's for.
#
# Usage: Called by Claude Code hooks system on tool use

set -euo pipefail

# Get git root (worktree root)
WORKTREE_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
CONTEXT_FILE="$WORKTREE_ROOT/.worktree-context.json"

# Only output if context file exists
if [[ ! -f "$CONTEXT_FILE" ]]; then
  exit 0
fi

# Parse context file
BRANCH=$(jq -r '.branch // "unknown"' "$CONTEXT_FILE")
PR_NUM=$(jq -r '.pr_number // empty' "$CONTEXT_FILE")
PR_TITLE=$(jq -r '.pr_title // empty' "$CONTEXT_FILE")
DESCRIPTION=$(jq -r '.description // empty' "$CONTEXT_FILE")
TASK_ID=$(jq -r '.task_id // empty' "$CONTEXT_FILE")

# Build output
echo "<worktree-context>"
echo "📍 Worktree: $WORKTREE_ROOT"
echo "   Branch: $BRANCH"

if [[ -n "$PR_NUM" ]]; then
  echo "   PR: #$PR_NUM - $PR_TITLE"
fi

if [[ -n "$TASK_ID" ]]; then
  echo "   Task: #$TASK_ID"
fi

if [[ -n "$DESCRIPTION" ]]; then
  echo ""
  echo "   $DESCRIPTION"
fi

echo "</worktree-context>"
