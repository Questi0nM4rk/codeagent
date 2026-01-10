#!/bin/bash
# ============================================
# Session End Hook
# Runs when Claude Code session ends
# ============================================

# Cleanup greeter flag
rm -f /tmp/.codeagent-greeted-* 2>/dev/null || true

# Could add:
# - Session stats logging
# - Memory sync to A-MEM
# - Cleanup temp files

exit 0
