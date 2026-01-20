#!/bin/bash
# ============================================
# CodeAgent Update
# Update to latest version
# ============================================

set -e

INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}CodeAgent Update${NC}"
echo "================"
echo ""

cd "$INSTALL_DIR"

# Check if git repo
if [ ! -d ".git" ]; then
  echo -e "${YELLOW}Warning: Not a git repository. Skipping update.${NC}"
  echo "For manual update, download the latest version from GitHub."
  exit 0
fi

# Backup current version
CURRENT_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
echo -e "Current version: ${BLUE}$CURRENT_VERSION${NC}"

# Pull latest
echo ""
echo -e "${BLUE}Pulling latest changes...${NC}"
git fetch origin
git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || {
  echo -e "${YELLOW}Pull failed. You may have local changes.${NC}"
  echo "Run 'git stash' first if needed."
  exit 1
}

# Get new version
NEW_VERSION=$(cat VERSION 2>/dev/null || echo "unknown")
echo -e "New version: ${GREEN}$NEW_VERSION${NC}"

# Make scripts executable
chmod +x bin/* scripts/* mcps/*.sh 2>/dev/null || true

# Update symlinks
BIN_DIR="$HOME/.local/bin"
for script in bin/*; do
  if [ -f "$script" ]; then
    ln -sf "$INSTALL_DIR/$script" "$BIN_DIR/$(basename $script)"
  fi
done

# Update MCPs if Claude Code available
if command -v claude &>/dev/null; then
  echo ""
  echo -e "${BLUE}Updating MCP configuration...${NC}"
  "$INSTALL_DIR/mcps/install-mcps.sh" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}Update complete!${NC}"
echo ""

if [ "$CURRENT_VERSION" != "$NEW_VERSION" ]; then
  echo "Changes in this version:"
  git log --oneline "$CURRENT_VERSION".."$NEW_VERSION" 2>/dev/null | head -10 || true
fi
