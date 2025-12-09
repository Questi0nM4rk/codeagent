#!/bin/bash
# ============================================
# CodeAgent Post-Implement Hook
# Runs after /implement completes
# Updates code graph with modified files
# ============================================

echo "Running post-implementation tasks..."

# Get list of modified files from git
MODIFIED_FILES=$(git diff --name-only HEAD~1 2>/dev/null || git diff --name-only --cached 2>/dev/null || echo "")

if [ -z "$MODIFIED_FILES" ]; then
    echo "  No modified files detected"
    exit 0
fi

# Index modified files into code graph (if code-graph MCP is running)
if curl -s http://localhost:3100/health > /dev/null 2>&1; then
    echo "  Updating code graph..."

    for file in $MODIFIED_FILES; do
        # Only index supported file types
        case "$file" in
            *.cs|*.cpp|*.c|*.h|*.hpp|*.rs|*.lua|*.sh)
                if [ -f "$file" ]; then
                    echo "    Indexing: $file"
                    # Call code-graph MCP to index the file
                    curl -s -X POST http://localhost:3100/index \
                        -H "Content-Type: application/json" \
                        -d "{\"file\": \"$(pwd)/$file\"}" \
                        > /dev/null 2>&1 || true
                fi
                ;;
        esac
    done

    echo "  Code graph updated"
else
    echo "  Code graph MCP not running, skipping indexing"
fi

# Extract patterns for memory (learner agent will handle this)
echo "  Pattern extraction will be handled by @learner agent"

echo "Post-implementation complete"
exit 0
