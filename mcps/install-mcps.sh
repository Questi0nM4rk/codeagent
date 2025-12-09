#!/bin/bash
# ============================================
# CodeAgent MCP Installation
# Configures Model Context Protocol servers
# ============================================

set -e

INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
FORCE_REINSTALL=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE_REINSTALL=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Load API keys from .env file if it exists
ENV_FILE="$INSTALL_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

echo -e "${BLUE}Configuring MCP servers for Claude Code...${NC}"
echo ""

# Check if claude CLI is available
if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}Claude Code CLI not found. MCPs will need manual configuration.${NC}"
    echo "Install Claude Code from: https://claude.ai/code"
    exit 0
fi

# Helper function to add MCP (removes first if --force)
add_mcp() {
    local name="$1"
    shift
    local args="$@"

    if [ "$FORCE_REINSTALL" = true ]; then
        claude mcp remove "$name" 2>/dev/null || true
    fi

    if claude mcp add $name -- $args 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "  ${YELLOW}○${NC} $name (already installed or failed)"
        return 1
    fi
}

# ============================================
# Core MCPs (always install)
# ============================================
echo -e "${BLUE}Installing core MCPs...${NC}"

# Filesystem access
add_mcp filesystem npx -y @modelcontextprotocol/server-filesystem .

# Git operations
add_mcp git npx -y @modelcontextprotocol/server-git --repository .

# Basic memory
add_mcp memory npx -y @modelcontextprotocol/server-memory

# ============================================
# Reasoning MCPs
# ============================================
echo ""
echo -e "${BLUE}Installing reasoning MCPs...${NC}"

# Sequential thinking for complex reasoning
add_mcp sequential-thinking npx -y @modelcontextprotocol/server-sequential-thinking

# ============================================
# Research MCPs
# ============================================
echo ""
echo -e "${BLUE}Installing research MCPs...${NC}"

# Context7 for library documentation
add_mcp context7 npx -y @upstash/context7-mcp

# Fetch for direct URL access
add_mcp fetch npx -y @anthropic/mcp-fetch

# ============================================
# Validation MCPs
# ============================================
echo ""
echo -e "${BLUE}Installing validation MCPs...${NC}"

# Semgrep for security scanning
add_mcp semgrep npx -y @semgrep/mcp-server

# ============================================
# Optional MCPs (require API keys)
# ============================================
echo ""
echo -e "${BLUE}Installing optional MCPs (require API keys)...${NC}"

# Helper for MCPs with env vars
add_mcp_with_env() {
    local name="$1"
    local env_var="$2"
    local env_val="$3"
    shift 3
    local args="$@"

    if [ "$FORCE_REINSTALL" = true ]; then
        claude mcp remove "$name" 2>/dev/null || true
    fi

    if claude mcp add "$name" --env "$env_var=$env_val" -- $args 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "  ${YELLOW}○${NC} $name (already installed or failed)"
        return 1
    fi
}

# GitHub (if token available)
if [ -n "$GITHUB_TOKEN" ]; then
    add_mcp_with_env github GITHUB_TOKEN "$GITHUB_TOKEN" npx -y @modelcontextprotocol/server-github
else
    echo -e "  ${YELLOW}○${NC} github (GITHUB_TOKEN not set)"
fi

# Tavily for web research (if key available)
if [ -n "$TAVILY_API_KEY" ]; then
    add_mcp_with_env tavily TAVILY_API_KEY "$TAVILY_API_KEY" npx -y tavily-mcp
else
    echo -e "  ${YELLOW}○${NC} tavily (TAVILY_API_KEY not set)"
fi

# ============================================
# Custom MCPs (CodeAgent specific)
# ============================================
VENV_PIP="$INSTALL_DIR/venv/bin/pip"
VENV_PYTHON="$INSTALL_DIR/venv/bin/python"
MCP_DIR="$INSTALL_DIR/mcps"

echo ""
echo -e "${BLUE}Installing CodeAgent custom MCPs...${NC}"

# Helper for custom Python MCPs
install_custom_mcp() {
    local name="$1"
    local mcp_path="$2"
    local module="$3"

    if [ ! -d "$mcp_path" ] || [ ! -f "$mcp_path/pyproject.toml" ]; then
        echo -e "  ${YELLOW}○${NC} $name (not found at $mcp_path)"
        return 1
    fi

    echo -e "  Installing $name dependencies..."

    if [ "$FORCE_REINSTALL" = true ]; then
        claude mcp remove "$name" 2>/dev/null || true
        "$VENV_PIP" install -e "$mcp_path" --force-reinstall --quiet 2>/dev/null || true
    else
        "$VENV_PIP" install -e "$mcp_path" --quiet 2>/dev/null || true
    fi

    if claude mcp add "$name" -- "$VENV_PYTHON" -m "$module" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "  ${YELLOW}○${NC} $name (already installed or failed)"
        return 1
    fi
}

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "  ${YELLOW}○${NC} Python venv not found - custom MCPs require venv"
    echo -e "  ${YELLOW}○${NC} Run install.sh to create venv"
else
    # Install MCP SDK first
    "$VENV_PIP" install mcp --quiet 2>/dev/null || true

    # Custom MCPs
    install_custom_mcp "code-graph" "$MCP_DIR/code-graph-mcp" "code_graph_mcp.server"
    install_custom_mcp "tot" "$MCP_DIR/tot-mcp" "tot_mcp.server"
    install_custom_mcp "reflection" "$MCP_DIR/reflection-mcp" "reflection_mcp.server"
fi

# Letta MCP (if server running)
if curl -s http://localhost:8283/ > /dev/null 2>&1; then
    add_mcp letta npx -y @letta-ai/mcp-server
else
    echo -e "  ${YELLOW}○${NC} letta (server not running - start with 'codeagent start')"
fi

echo ""
echo -e "${GREEN}MCP configuration complete!${NC}"
echo ""
echo "Run 'claude mcp list' to see all configured servers."
echo ""
