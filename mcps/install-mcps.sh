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

# ============================================
# Core MCPs (always install)
# ============================================
echo -e "${BLUE}Installing core MCPs...${NC}"

# Filesystem access
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem . 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} filesystem" || echo -e "  ${YELLOW}○${NC} filesystem (already installed or failed)"

# Git operations
claude mcp add git -- npx -y @modelcontextprotocol/server-git --repository . 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} git" || echo -e "  ${YELLOW}○${NC} git (already installed or failed)"

# Basic memory
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} memory" || echo -e "  ${YELLOW}○${NC} memory (already installed or failed)"

# ============================================
# Reasoning MCPs
# ============================================
echo ""
echo -e "${BLUE}Installing reasoning MCPs...${NC}"

# Sequential thinking for complex reasoning
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} sequential-thinking" || echo -e "  ${YELLOW}○${NC} sequential-thinking (already installed or failed)"

# ============================================
# Research MCPs
# ============================================
echo ""
echo -e "${BLUE}Installing research MCPs...${NC}"

# Context7 for library documentation
claude mcp add context7 -- npx -y @upstash/context7-mcp 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} context7" || echo -e "  ${YELLOW}○${NC} context7 (already installed or failed)"

# Fetch for direct URL access
claude mcp add fetch -- npx -y @anthropic/mcp-fetch 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} fetch" || echo -e "  ${YELLOW}○${NC} fetch (already installed or failed)"

# ============================================
# Validation MCPs
# ============================================
echo ""
echo -e "${BLUE}Installing validation MCPs...${NC}"

# Semgrep for security scanning
claude mcp add semgrep -- npx -y @semgrep/mcp-server 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} semgrep" || echo -e "  ${YELLOW}○${NC} semgrep (already installed or failed)"

# ============================================
# Optional MCPs (require API keys)
# ============================================
echo ""
echo -e "${BLUE}Installing optional MCPs (require API keys)...${NC}"

# GitHub (if token available)
if [ -n "$GITHUB_TOKEN" ]; then
    claude mcp add github --env GITHUB_TOKEN=$GITHUB_TOKEN -- npx -y @modelcontextprotocol/server-github 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} github" || echo -e "  ${YELLOW}○${NC} github (failed)"
else
    echo -e "  ${YELLOW}○${NC} github (GITHUB_TOKEN not set)"
fi

# Tavily for web research (if key available)
if [ -n "$TAVILY_API_KEY" ]; then
    claude mcp add tavily --env TAVILY_API_KEY=$TAVILY_API_KEY -- npx -y tavily-mcp 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} tavily" || echo -e "  ${YELLOW}○${NC} tavily (failed)"
else
    echo -e "  ${YELLOW}○${NC} tavily (TAVILY_API_KEY not set)"
fi

# ============================================
# Custom MCPs (CodeAgent specific)
# ============================================
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"

echo ""
echo -e "${BLUE}Installing CodeAgent custom MCPs...${NC}"

# Code-Graph MCP (if installed)
if [ -d "$INSTALL_DIR/mcps/code-graph-mcp" ]; then
    pip install -e "$INSTALL_DIR/mcps/code-graph-mcp" --quiet 2>/dev/null || true
    claude mcp add code-graph -- python -m code_graph_mcp.server 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} code-graph" || echo -e "  ${YELLOW}○${NC} code-graph (failed)"
else
    echo -e "  ${YELLOW}○${NC} code-graph (not yet implemented)"
fi

# Tree-of-Thought MCP (if installed)
if [ -d "$INSTALL_DIR/mcps/tot-mcp" ]; then
    pip install -e "$INSTALL_DIR/mcps/tot-mcp" --quiet 2>/dev/null || true
    claude mcp add tot -- python -m tot_mcp.server 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} tot" || echo -e "  ${YELLOW}○${NC} tot (failed)"
else
    echo -e "  ${YELLOW}○${NC} tot (not yet implemented)"
fi

# Reflection MCP (if installed)
if [ -d "$INSTALL_DIR/mcps/reflection-mcp" ]; then
    pip install -e "$INSTALL_DIR/mcps/reflection-mcp" --quiet 2>/dev/null || true
    claude mcp add reflection -- python -m reflection_mcp.server 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} reflection" || echo -e "  ${YELLOW}○${NC} reflection (failed)"
else
    echo -e "  ${YELLOW}○${NC} reflection (not yet implemented)"
fi

# Letta MCP (if server running)
if curl -s http://localhost:8283/health > /dev/null 2>&1; then
    claude mcp add letta -- npx -y @letta-ai/mcp-server 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} letta" || echo -e "  ${YELLOW}○${NC} letta (failed)"
else
    echo -e "  ${YELLOW}○${NC} letta (server not running - start with 'codeagent start')"
fi

echo ""
echo -e "${GREEN}MCP configuration complete!${NC}"
echo ""
echo "Run 'claude mcp list' to see all configured servers."
echo ""
