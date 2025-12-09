#!/bin/bash
# ============================================
# CodeAgent Index File Hook
# Indexes a single file into the code graph
# Called by PostToolUse hook when files are written
# ============================================

FILE="$1"

if [ -z "$FILE" ]; then
    exit 0
fi

# Only index if code-graph MCP is running
if curl -s http://localhost:3100/health > /dev/null 2>&1; then
    # Check if file type is supported
    case "$FILE" in
        *.cs|*.cpp|*.c|*.h|*.hpp|*.rs|*.lua|*.sh)
            curl -s -X POST http://localhost:3100/index \
                -H "Content-Type: application/json" \
                -d "{\"file\": \"$FILE\"}" \
                > /dev/null 2>&1 || true
            ;;
    esac
fi

exit 0
