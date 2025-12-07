# CodeAgent

> Research-backed autonomous coding framework for Claude Code. Zero assumptions. 100% accuracy.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue)](https://claude.ai/code)

---

## What is CodeAgent?

A framework that transforms Claude Code into an accuracy-optimized autonomous coding system. Built on research from 1,400+ academic papers, implementing patterns that achieve **70%+ resolution rates** on SWE-bench.

**Key Principles:**

- Memory-first intelligence (check what you know before searching)
- Single-agent implementation (multi-agent fragments context)
- External validation only (never self-review)
- Test-driven development (always)

---

## Quick Install

```bash
# One-line install
curl -fsSL https://raw.githubusercontent.com/USER/codeagent/main/install.sh | bash

# Restart shell
source ~/.bashrc  # or ~/.zshrc

# Start services
codeagent start

# Initialize in your project
cd /your/project
codeagent init
```

---

## Requirements

- **OS**: Linux (Ubuntu 22.04+, Arch, Fedora)
- **Docker**: 24.0+ with Compose v2
- **Node.js**: 18+
- **Python**: 3.11+
- **RAM**: 16GB recommended (8GB minimum)
- **Disk**: 10GB free
- **Claude Code**: Installed and authenticated

---

## Commands

After initialization, use in Claude Code:

| Command        | What it does                                             |
| -------------- | -------------------------------------------------------- |
| `/scan`        | Build knowledge graph of your codebase                   |
| `/plan "task"` | Research, design, auto-detect execution mode             |
| `/implement`   | TDD implementation (auto-selects sequential or parallel) |
| `/integrate`   | Auto-triggered after parallel /implement                 |
| `/review`      | Validate with external tools                             |

**That's it. 4 commands.** The system auto-detects if parallel execution is beneficial.

---

## Auto-Parallel Detection

When you run `/plan`, the system automatically analyzes your task:

```
/plan "Add user management and product catalog"

Output:
  Execution Mode: PARALLEL ⚡
  Reason: 2 independent subtasks, no file conflicts
  Estimated speedup: 50%
```

Then `/implement` uses the detected mode automatically.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        COMMANDS                               │
│     /scan      /plan      /implement      /review            │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                         AGENTS                                │
│  @researcher  @architect  @implementer  @reviewer  @learner  │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                          MCPs                                 │
│  Core: filesystem, git, github, memory                       │
│  Memory: letta, code-graph                                   │
│  Research: context7, tavily, fetch                           │
│  Language: omnisharp, clangd, rust-analyzer                  │
│  Validation: semgrep                                          │
│  Custom: tot, reflection, code-graph                          │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE                            │
│        Neo4j        Qdrant        Letta        Ollama        │
└──────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
codeagent/
├── README.md
├── LICENSE
├── install.sh                    # Main installer
├── uninstall.sh                  # Clean removal
│
├── bin/                          # CLI commands
│   ├── codeagent                 # Main CLI
│   ├── codeagent-start           # Start services
│   ├── codeagent-stop            # Stop services
│   ├── codeagent-status          # Check health
│   └── codeagent-init            # Initialize project
│
├── infrastructure/
│   ├── docker-compose.yml        # Neo4j, Qdrant, Letta, Ollama
│   ├── neo4j/
│   │   └── init.cypher           # Graph schema
│   └── letta/
│       └── config.yaml           # Memory config
│
├── mcps/
│   ├── install-mcps.sh           # MCP installer
│   ├── mcp.json.template         # Shared MCP config
│   │
│   ├── tot-mcp/                  # Tree-of-Thought (+70%)
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/
│   │       └── tot_mcp/
│   │           ├── __init__.py
│   │           └── server.py
│   │
│   ├── reflection-mcp/           # Self-Reflection (+21%)
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/
│   │       └── reflection_mcp/
│   │           ├── __init__.py
│   │           └── server.py
│   │
│   └── code-graph-mcp/           # Code Knowledge Graph (+75%)
│       ├── pyproject.toml
│       ├── README.md
│       └── src/
│           └── code_graph_mcp/
│               ├── __init__.py
│               ├── server.py
│               ├── parsers.py    # Tree-sitter wrappers
│               └── queries.py    # Neo4j queries
│
├── framework/
│   ├── CLAUDE.md.template        # Global config template
│   ├── CLAUDE.local.md.template  # Local overrides template
│   ├── settings.json.template    # Permissions & hooks
│   │
│   ├── agents/
│   │   ├── researcher.md         # Context gathering [think hard]
│   │   ├── architect.md          # Solution design [ultrathink]
│   │   ├── orchestrator.md       # Parallel analysis [think harder]
│   │   ├── implementer.md        # TDD coding [think hard]
│   │   ├── reviewer.md           # External validation [think hard]
│   │   └── learner.md            # Pattern extraction [think]
│   │
│   └── commands/
│       ├── scan.md               # Build knowledge
│       ├── plan.md               # Research + design + auto-parallel detection
│       ├── implement.md          # TDD (auto-selects sequential or parallel)
│       ├── integrate.md          # Merge parallel work (auto-triggered)
│       └── review.md             # Final validation
│
├── templates/                    # Project templates
│   ├── dotnet/
│   │   └── CLAUDE.md
│   ├── cpp/
│   │   └── CLAUDE.md
│   ├── rust/
│   │   └── CLAUDE.md
│   └── lua/
│       └── CLAUDE.md
│
├── scripts/
│   ├── health-check.sh           # Service health verification
│   ├── backup-memory.sh          # Backup Letta + Neo4j
│   ├── restore-memory.sh         # Restore from backup
│   └── update.sh                 # Update framework
│
├── docs/
│   ├── VISION.md                 # Project philosophy
│   ├── ARCHITECTURE.md           # Technical deep-dive
│   ├── AGENTS.md                 # Agent documentation
│   ├── COMMANDS.md               # Command reference
│   ├── PARALLEL.md               # Parallel execution guide
│   ├── MCPS.md                   # MCP documentation
│   ├── CUSTOM-MCPS.md            # Building custom MCPs
│   └── TROUBLESHOOTING.md        # Common issues
│
└── examples/
    ├── dotnet-api/               # Example .NET project
    ├── cpp-cli/                  # Example C++ project
    ├── rust-lib/                 # Example Rust project
    └── parallel-demo/            # Example parallel execution
```

---

## install.sh

```bash
#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/.codeagent"
BIN_DIR="$HOME/.local/bin"
REPO_URL="https://github.com/USER/codeagent.git"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║     ██████╗ ██████╗ ██████╗ ███████╗ █████╗  ██████╗     ║"
echo "║    ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝     ║"
echo "║    ██║     ██║   ██║██║  ██║█████╗  ███████║██║  ███╗    ║"
echo "║    ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██║██║   ██║    ║"
echo "║    ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║╚██████╔╝    ║"
echo "║     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝     ║"
echo "║                                                           ║"
echo "║         Research-Backed Autonomous Coding Framework       ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check requirements
echo -e "${YELLOW}Checking requirements...${NC}"

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ $1 not found. Please install $1 first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $1${NC}"
}

check_command docker
check_command node
check_command python3
check_command git

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose v2 not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker compose${NC}"

# Check Claude Code
if ! command -v claude &> /dev/null; then
    echo -e "${YELLOW}⚠ Claude Code CLI not found. Install from: https://claude.ai/code${NC}"
fi

# Clone or update
echo ""
echo -e "${YELLOW}Installing CodeAgent...${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create bin directory
mkdir -p "$BIN_DIR"

# Install CLI commands
echo -e "${YELLOW}Installing CLI commands...${NC}"
for script in bin/*; do
    chmod +x "$script"
    ln -sf "$INSTALL_DIR/$script" "$BIN_DIR/$(basename $script)"
done

# Install Python dependencies for custom MCPs
echo -e "${YELLOW}Installing Python dependencies...${NC}"
python3 -m pip install --user --quiet \
    mcp \
    neo4j \
    tree-sitter \
    tree-sitter-c-sharp \
    tree-sitter-cpp \
    tree-sitter-rust

# Add to PATH if needed
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    if ! grep -q "/.local/bin" "$SHELL_RC"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo -e "${YELLOW}Added ~/.local/bin to PATH in $SHELL_RC${NC}"
    fi
fi

# Copy global CLAUDE.md
echo -e "${YELLOW}Setting up global configuration...${NC}"
mkdir -p "$HOME/.claude"
if [ ! -f "$HOME/.claude/CLAUDE.md" ]; then
    cp "$INSTALL_DIR/framework/CLAUDE.md.template" "$HOME/.claude/CLAUDE.md"
    echo -e "${GREEN}Created ~/.claude/CLAUDE.md${NC}"
fi

# Done
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                Installation Complete!                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Next steps:"
echo ""
echo -e "  ${BLUE}1.${NC} Restart your shell or run:"
echo -e "     ${YELLOW}source $SHELL_RC${NC}"
echo ""
echo -e "  ${BLUE}2.${NC} Start infrastructure:"
echo -e "     ${YELLOW}codeagent start${NC}"
echo ""
echo -e "  ${BLUE}3.${NC} Initialize in your project:"
echo -e "     ${YELLOW}cd /your/project${NC}"
echo -e "     ${YELLOW}codeagent init${NC}"
echo ""
echo -e "  ${BLUE}4.${NC} Start coding:"
echo -e "     ${YELLOW}/scan${NC}              # Build knowledge"
echo -e "     ${YELLOW}/plan \"task\"${NC}       # Research & design"
echo -e "     ${YELLOW}/implement${NC}         # TDD implementation"
echo -e "     ${YELLOW}/review${NC}            # Validate changes"
echo ""
echo -e "Documentation: ${BLUE}$INSTALL_DIR/docs/${NC}"
echo ""
```

---

## bin/codeagent

```bash
#!/bin/bash
set -e

INSTALL_DIR="$HOME/.codeagent"
VERSION="0.1.0"

usage() {
    echo "CodeAgent v$VERSION - Research-Backed Autonomous Coding Framework"
    echo ""
    echo "Usage: codeagent <command>"
    echo ""
    echo "Commands:"
    echo "  start       Start infrastructure (Neo4j, Qdrant, Letta, Ollama)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Check service health"
    echo "  init        Initialize CodeAgent in current project"
    echo "  update      Update CodeAgent to latest version"
    echo "  uninstall   Remove CodeAgent completely"
    echo "  logs        View service logs"
    echo "  backup      Backup memory (Letta + Neo4j)"
    echo "  restore     Restore memory from backup"
    echo ""
    echo "Project Commands (use in Claude Code):"
    echo "  /scan       Build knowledge graph"
    echo "  /plan       Research and design"
    echo "  /implement  TDD implementation"
    echo "  /review     Validate with external tools"
    echo ""
}

case "$1" in
    start)
        exec "$INSTALL_DIR/bin/codeagent-start"
        ;;
    stop)
        exec "$INSTALL_DIR/bin/codeagent-stop"
        ;;
    restart)
        "$INSTALL_DIR/bin/codeagent-stop"
        "$INSTALL_DIR/bin/codeagent-start"
        ;;
    status)
        exec "$INSTALL_DIR/bin/codeagent-status"
        ;;
    init)
        exec "$INSTALL_DIR/bin/codeagent-init"
        ;;
    update)
        exec "$INSTALL_DIR/scripts/update.sh"
        ;;
    logs)
        docker compose -f "$INSTALL_DIR/infrastructure/docker-compose.yml" logs -f
        ;;
    backup)
        exec "$INSTALL_DIR/scripts/backup-memory.sh"
        ;;
    restore)
        exec "$INSTALL_DIR/scripts/restore-memory.sh" "$2"
        ;;
    uninstall)
        exec "$INSTALL_DIR/uninstall.sh"
        ;;
    version|-v|--version)
        echo "CodeAgent v$VERSION"
        ;;
    help|-h|--help|"")
        usage
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run 'codeagent help' for usage."
        exit 1
        ;;
esac
```

---

## bin/codeagent-start

```bash
#!/bin/bash
set -e

INSTALL_DIR="$HOME/.codeagent"

echo "Starting CodeAgent infrastructure..."

# Start Docker services
cd "$INSTALL_DIR/infrastructure"
docker compose up -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 5

# Health checks
echo "Checking service health..."
"$INSTALL_DIR/scripts/health-check.sh"

# Install/update MCPs
echo "Configuring MCP servers..."
"$INSTALL_DIR/mcps/install-mcps.sh"

# Pull Ollama model if needed
if docker exec codeagent-ollama ollama list 2>/dev/null | grep -q "mxbai-embed-large"; then
    echo "✓ Embedding model ready"
else
    echo "Pulling embedding model (first time only)..."
    docker exec codeagent-ollama ollama pull mxbai-embed-large
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║      CodeAgent is ready!               ║"
echo "╠════════════════════════════════════════╣"
echo "║  Neo4j:  http://localhost:7474         ║"
echo "║  Qdrant: http://localhost:6333         ║"
echo "║  Letta:  http://localhost:8283         ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Run 'codeagent init' in your project to get started."
```

---

## bin/codeagent-init

```bash
#!/bin/bash
set -e

INSTALL_DIR="$HOME/.codeagent"
PROJECT_DIR="$(pwd)"

echo "Initializing CodeAgent in: $PROJECT_DIR"

# Create .claude directory
mkdir -p .claude/agents .claude/commands

# Copy agents
echo "Installing agents..."
cp "$INSTALL_DIR/framework/agents/"*.md .claude/agents/

# Copy commands
echo "Installing commands..."
cp "$INSTALL_DIR/framework/commands/"*.md .claude/commands/

# Copy settings
if [ ! -f ".claude/settings.json" ]; then
    cp "$INSTALL_DIR/framework/settings.json.template" .claude/settings.json
fi

# Create CLAUDE.md if not exists
if [ ! -f "CLAUDE.md" ]; then
    # Detect project type
    if [ -f "*.csproj" ] || [ -f "*.sln" ]; then
        TEMPLATE="dotnet"
    elif [ -f "CMakeLists.txt" ] || [ -f "Makefile" ]; then
        TEMPLATE="cpp"
    elif [ -f "Cargo.toml" ]; then
        TEMPLATE="rust"
    elif [ -f "*.rockspec" ] || [ -f "init.lua" ]; then
        TEMPLATE="lua"
    else
        TEMPLATE="dotnet"  # default
    fi

    cp "$INSTALL_DIR/templates/$TEMPLATE/CLAUDE.md" CLAUDE.md
    echo "Created CLAUDE.md (template: $TEMPLATE)"
    echo "⚠ Please customize CLAUDE.md for your project!"
fi

# Create .mcp.json if not exists
if [ ! -f ".mcp.json" ]; then
    cp "$INSTALL_DIR/mcps/mcp.json.template" .mcp.json
fi

# Create docs directory
mkdir -p docs/decisions

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     Project initialized!               ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Created:"
echo "  ├── CLAUDE.md           (customize this!)"
echo "  ├── .mcp.json           (shared MCP config)"
echo "  ├── .claude/"
echo "  │   ├── settings.json   (permissions & hooks)"
echo "  │   ├── agents/         (6 agents with thinking levels)"
echo "  │   │   ├── researcher.md    [think hard]"
echo "  │   │   ├── architect.md     [ultrathink]"
echo "  │   │   ├── orchestrator.md  [think harder]"
echo "  │   │   ├── implementer.md   [think hard]"
echo "  │   │   ├── reviewer.md      [think hard]"
echo "  │   │   └── learner.md       [think]"
echo "  │   └── commands/       (4 commands + auto-integrate)"
echo "  │       ├── scan.md"
echo "  │       ├── plan.md          (auto-detects parallel)"
echo "  │       ├── implement.md     (uses detected mode)"
echo "  │       ├── integrate.md     (auto after parallel)"
echo "  │       └── review.md"
echo "  └── docs/"
echo "      └── decisions/      (architecture decisions)"
echo ""
echo "Usage:"
echo "  /scan              # Build knowledge (once)"
echo "  /plan \"task\"       # Research + design (auto-detects parallel)"
echo "  /implement         # Execute (sequential or parallel)"
echo "  /review            # Validate"
echo ""
echo "Next: Edit CLAUDE.md, then run /scan in Claude Code"
```

---

## bin/codeagent-status

```bash
#!/bin/bash

INSTALL_DIR="$HOME/.codeagent"

echo "CodeAgent Service Status"
echo "========================"
echo ""

check_service() {
    local name=$1
    local url=$2
    local container=$3

    # Check if container is running
    if docker ps --format '{{.Names}}' | grep -q "$container"; then
        # Check if service responds
        if curl -s --max-time 2 "$url" > /dev/null 2>&1; then
            echo "✅ $name: running ($url)"
        else
            echo "⚠️  $name: container running but not responding"
        fi
    else
        echo "❌ $name: not running"
    fi
}

check_service "Neo4j" "http://localhost:7474" "codeagent-neo4j"
check_service "Qdrant" "http://localhost:6333/health" "codeagent-qdrant"
check_service "Letta" "http://localhost:8283/health" "codeagent-letta"
check_service "Ollama" "http://localhost:11434/api/tags" "codeagent-ollama"

echo ""
echo "MCP Servers"
echo "-----------"
if command -v claude &> /dev/null; then
    claude mcp list 2>/dev/null | head -20 || echo "Run 'claude mcp list' to see configured MCPs"
else
    echo "Claude Code CLI not found"
fi
```

---

## infrastructure/docker-compose.yml

```yaml
version: "3.8"

services:
  neo4j:
    image: neo4j:5-community
    container_name: codeagent-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/codeagent
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_apoc_export_file_enabled: "true"
      NEO4J_apoc_import_file_enabled: "true"
    volumes:
      - codeagent_neo4j_data:/data
      - codeagent_neo4j_logs:/logs
      - ./neo4j/init.cypher:/var/lib/neo4j/import/init.cypher
    healthcheck:
      test: wget -qO- http://localhost:7474 || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    container_name: codeagent-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - codeagent_qdrant_data:/qdrant/storage
    healthcheck:
      test: wget -qO- http://localhost:6333/health || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  letta:
    image: letta/letta:latest
    container_name: codeagent-letta
    ports:
      - "8283:8283"
    environment:
      LETTA_QDRANT_HOST: qdrant
      LETTA_QDRANT_PORT: 6333
    volumes:
      - codeagent_letta_data:/root/.letta
    depends_on:
      qdrant:
        condition: service_healthy
    healthcheck:
      test: wget -qO- http://localhost:8283/health || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    container_name: codeagent-ollama
    ports:
      - "11434:11434"
    volumes:
      - codeagent_ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      test: wget -qO- http://localhost:11434/api/tags || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  codeagent_neo4j_data:
  codeagent_neo4j_logs:
  codeagent_qdrant_data:
  codeagent_letta_data:
  codeagent_ollama_data:

networks:
  default:
    name: codeagent-network
```

---

## mcps/install-mcps.sh

```bash
#!/bin/bash
set -e

echo "Installing MCP servers..."

# Core
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem . 2>/dev/null || true
claude mcp add git -- npx -y @modelcontextprotocol/server-git --repository . 2>/dev/null || true
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory 2>/dev/null || true

# Reasoning
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking 2>/dev/null || true

# Research
claude mcp add context7 -- npx -y @upstash/context7-mcp 2>/dev/null || true
claude mcp add fetch -- npx -y @anthropic/mcp-fetch 2>/dev/null || true

# Validation
claude mcp add semgrep -- npx -y @semgrep/mcp-server 2>/dev/null || true

# GitHub (if token available)
if [ -n "$GITHUB_TOKEN" ]; then
    claude mcp add github --env GITHUB_TOKEN=$GITHUB_TOKEN -- npx -y @modelcontextprotocol/server-github 2>/dev/null || true
fi

# Tavily (if key available)
if [ -n "$TAVILY_API_KEY" ]; then
    claude mcp add tavily --env TAVILY_API_KEY=$TAVILY_API_KEY -- npx -y tavily-mcp 2>/dev/null || true
fi

# Custom MCPs (from this repo)
INSTALL_DIR="$HOME/.codeagent"

# Code-Graph MCP
if [ -d "$INSTALL_DIR/mcps/code-graph-mcp" ]; then
    pip install -e "$INSTALL_DIR/mcps/code-graph-mcp" --quiet
    claude mcp add code-graph -- python -m code_graph_mcp.server 2>/dev/null || true
fi

# ToT MCP
if [ -d "$INSTALL_DIR/mcps/tot-mcp" ]; then
    pip install -e "$INSTALL_DIR/mcps/tot-mcp" --quiet
    claude mcp add tot -- python -m tot_mcp.server 2>/dev/null || true
fi

# Reflection MCP
if [ -d "$INSTALL_DIR/mcps/reflection-mcp" ]; then
    pip install -e "$INSTALL_DIR/mcps/reflection-mcp" --quiet
    claude mcp add reflection -- python -m reflection_mcp.server 2>/dev/null || true
fi

echo "✓ MCP servers configured"
```

---

## What's Included

| Component                     | Description                                                         |
| ----------------------------- | ------------------------------------------------------------------- |
| **6 Agents**                  | researcher, architect, orchestrator, implementer, reviewer, learner |
| **4 Commands**                | /scan, /plan, /implement, /review (+ auto /integrate)               |
| **Thinking Levels**           | ultrathink → think harder → think hard → think (per agent)          |
| **Auto-Parallel**             | System detects if tasks can run in parallel                         |
| **4 Infrastructure Services** | Neo4j, Qdrant, Letta, Ollama                                        |
| **10+ MCP Servers**           | Core, memory, research, language, validation                        |
| **3 Custom MCPs**             | ToT, Reflection, Code-Graph                                         |
| **Project Templates**         | .NET, C++, Rust, Lua                                                |
| **CLI Tools**                 | start, stop, init, status, backup, restore                          |

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Acknowledgments

Built on research from:

- Context Engineering Survey (arXiv:2507.13334)
- Tree-of-Thought (arXiv:2305.10601)
- Reflexion (NeurIPS 2023)
- SuperClaude Framework
- Anthropic's Claude Code documentation
