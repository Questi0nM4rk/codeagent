#!/bin/bash
# ============================================
# CodeAgent Greeter Hook
# Runs on first user prompt of session
# ============================================

# Only greet once per session
GREETER_FLAG="/tmp/.codeagent-greeted-$$"
if [ -f "$GREETER_FLAG" ]; then
    exit 0
fi
touch "$GREETER_FLAG"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${CYAN}╭─────────────────────────────────────────╮${NC}"
echo -e "${CYAN}│${NC}  ${GREEN}CodeAgent${NC} ready                       ${CYAN}│${NC}"
echo -e "${CYAN}│${NC}  /scan /plan /implement /review        ${CYAN}│${NC}"
echo -e "${CYAN}╰─────────────────────────────────────────╯${NC}"
echo ""
