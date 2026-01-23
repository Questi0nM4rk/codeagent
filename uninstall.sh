#!/bin/bash
# ============================================
# CodeAgent Uninstall
# Remove CodeAgent completely
# ============================================

INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
BIN_DIR="$HOME/.local/bin"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}CodeAgent Uninstall${NC}"
echo "==================="
echo ""
echo -e "${YELLOW}This will remove:${NC}"
echo "  - CodeAgent installation ($INSTALL_DIR)"
echo "  - CLI commands from $BIN_DIR"
echo "  - Docker containers and volumes (optional)"
echo ""
echo -e "${YELLOW}This will NOT remove:${NC}"
echo "  - Your ~/.claude/ directory"
echo "  - Your project .claude/ directories"
echo "  - Backups in ~/.codeagent-backups/"
echo ""

read -p "Continue with uninstall? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

# Stop services
echo ""
echo -e "${BLUE}Stopping services...${NC}"
if [ -f "$INSTALL_DIR/infrastructure/docker-compose.yml" ]; then
  cd "$INSTALL_DIR/infrastructure" || exit 1
  docker compose down 2>/dev/null || true
fi

# Ask about Docker volumes
echo ""
read -p "Remove Docker volumes (deletes all memory data)? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${BLUE}Removing Docker volumes...${NC}"
  docker volume rm codeagent_qdrant_data 2>/dev/null || true
  rm -rf "$HOME/.codeagent/memory" 2>/dev/null || true
  echo -e "${GREEN}✓${NC} Volumes removed"
else
  echo -e "${YELLOW}○${NC} Volumes preserved"
fi

# Remove CLI commands
echo ""
echo -e "${BLUE}Removing CLI commands...${NC}"
rm -f "$BIN_DIR/codeagent"
rm -f "$BIN_DIR/codeagent-start"
rm -f "$BIN_DIR/codeagent-stop"
rm -f "$BIN_DIR/codeagent-status"
rm -f "$BIN_DIR/codeagent-init"
echo -e "${GREEN}✓${NC} CLI commands removed"

# Remove MCPs
echo ""
echo -e "${BLUE}Removing MCP configurations...${NC}"
if command -v claude &>/dev/null; then
  claude mcp remove context7 2>/dev/null || true
  claude mcp remove code-execution 2>/dev/null || true
  claude mcp remove reflection 2>/dev/null || true
  claude mcp remove amem 2>/dev/null || true
  claude mcp remove tavily 2>/dev/null || true
  claude mcp remove figma 2>/dev/null || true
  claude mcp remove supabase 2>/dev/null || true
  claude mcp remove github 2>/dev/null || true
  echo -e "${GREEN}✓${NC} MCPs removed"
fi

# Remove installation directory
echo ""
echo -e "${BLUE}Removing installation directory...${NC}"
rm -rf "$INSTALL_DIR"
echo -e "${GREEN}✓${NC} Installation removed"

# Clean shell config
echo ""
echo -e "${BLUE}Cleaning shell configuration...${NC}"
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$rc" ]; then
    # Remove CodeAgent lines
    sed -i '/# CodeAgent/d' "$rc" 2>/dev/null || true
    sed -i '/CODEAGENT_HOME/d' "$rc" 2>/dev/null || true
  fi
done
echo -e "${GREEN}✓${NC} Shell config cleaned"

echo ""
echo -e "${GREEN}CodeAgent has been uninstalled.${NC}"
echo ""
echo "To reinstall: curl -fsSL <install_url> | bash"
echo ""
