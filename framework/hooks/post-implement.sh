#!/bin/bash
# ============================================
# CodeAgent Post-Implement Hook
# Runs after /implement completes
# ============================================

echo "Running post-implementation tasks..."

# Get list of modified files from git
MODIFIED_FILES=$(git diff --name-only HEAD~1 2>/dev/null || git diff --name-only --cached 2>/dev/null || echo "")

if [ -z "$MODIFIED_FILES" ]; then
    echo "  No modified files detected"
    exit 0
fi

echo "  Modified files:"
for file in $MODIFIED_FILES; do
    if [ -f "$file" ]; then
        echo "    - $file"
    fi
done

# Pattern extraction will be handled by learner agent
echo "  Pattern extraction will be handled by @learner agent"

echo "Post-implementation complete"
exit 0
