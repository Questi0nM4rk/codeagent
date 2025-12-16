# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CodeAgent** (v0.1.0) is a research-backed autonomous coding framework for Claude Code. It provides skills, commands, MCP servers, and Docker infrastructure to transform Claude Code into an accuracy-optimized system.

## Quick Start

```bash
./install.sh           # Install everything
codeagent start        # Start infrastructure
cd /your/project && codeagent init   # Initialize in any project
```

## Development Commands

```bash
# Validate shell scripts
shellcheck install.sh bin/* scripts/*.sh mcps/*.sh

# Test custom MCP servers
~/.codeagent/venv/bin/python -m pytest mcps/code-graph-mcp/
~/.codeagent/venv/bin/python -m pytest mcps/tot-mcp/
~/.codeagent/venv/bin/python -m pytest mcps/reflection-mcp/

# Infrastructure management
codeagent start        # Start Neo4j, Qdrant, Letta
codeagent stop         # Stop services
codeagent status       # Health check
codeagent logs -f      # Follow logs

# Manual Docker control
cd infrastructure && docker compose up -d
docker compose logs -f
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code CLI                          │
├─────────────────────────────────────────────────────────────┤
│  Skills           │  Commands        │  Hooks               │
│  ~/.claude/       │  ~/.claude/      │  ~/.claude/          │
│  skills/          │  commands/       │  hooks/              │
├─────────────────────────────────────────────────────────────┤
│                     MCP Servers                              │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌────────────────┐   │
│  │code-graph│ │   tot   │ │reflection│ │ letta + npm    │   │
│  │ (Neo4j)  │ │  (ToT)  │ │(episodic)│ │(context7, etc) │   │
│  └──────────┘ └─────────┘ └──────────┘ └────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│              Docker Infrastructure                           │
│  Neo4j:7687       │    Qdrant:6333   │    Letta:8283        │
└─────────────────────────────────────────────────────────────┘
```

## Installation Structure

CodeAgent uses a **global-first** architecture. Everything is installed globally except project-specific memory.

### Global (installed by `install.sh`)

```
~/.claude/                    # Claude Code global config
├── CLAUDE.md                 # Personality + CodeAgent instructions
├── settings.json             # Permissions, hooks, MCPs
├── skills/                   # 6 auto-activating skills
└── commands/                 # 5 slash commands

~/.codeagent/                 # CodeAgent installation
├── bin/                      # CLI tools
├── mcps/                     # Custom MCP servers
├── templates/                # CLAUDE.md templates
├── infrastructure/           # docker-compose.yml
└── .env                      # API keys
```

### Per-Project (created by `codeagent init`)

```
project/
├── CLAUDE.md                 # Project instructions (created by /init)
├── .claude/
│   └── letta-agent           # Letta agent ID (project memory)
└── docs/
    └── decisions/            # Architecture decision records
```

## Source Directories

| Directory | Purpose |
|-----------|---------|
| `bin/` | CLI entry points (codeagent, codeagent-start, etc.) |
| `framework/skills/` | 6 skill definitions → installed to `~/.claude/skills/` |
| `framework/commands/` | 5 slash commands → installed to `~/.claude/commands/` |
| `framework/hooks/` | Git and post-edit hooks |
| `mcps/` | Custom Python MCP servers + installers |
| `infrastructure/` | Docker Compose for Neo4j, Qdrant, Letta |
| `templates/` | CLAUDE.md templates by language (dotnet, rust, cpp, lua) |
| `scripts/` | Maintenance scripts (backup, restore, update, health-check) |

## Custom MCPs

Python MCP servers in `mcps/`:

| MCP | Backend | Purpose |
|-----|---------|---------|
| `code-graph-mcp` | Neo4j | AST-based code knowledge graph (75% retrieval improvement) |
| `tot-mcp` | In-memory | Tree-of-Thought reasoning (+70% on complex tasks) |
| `reflection-mcp` | Qdrant | Self-reflection and episodic memory (+21% on HumanEval) |

Install: `mcps/install-mcps.sh` registers all MCPs in global Claude Code scope.

## Skills System

Skills auto-activate based on context. Each has a thinking level:

| Skill | Thinking | Purpose |
|-------|----------|---------|
| researcher | `think hard` | Memory-first context gathering |
| architect | `ultrathink` | Tree-of-Thought solution design |
| orchestrator | `think harder` | Parallel execution analysis |
| implementer | `think hard` | Strict TDD workflow |
| reviewer | `think hard` | External tool validation |
| learner | `think` | Pattern extraction |

## Slash Commands

| Command | Description |
|---------|-------------|
| `/scan` | Build knowledge graph of codebase |
| `/plan "task"` | Research → Design (auto-detects parallel) |
| `/implement` | TDD execution (sequential or parallel) |
| `/integrate` | Merge parallel work streams |
| `/review` | Validate with external tools |

## Infrastructure

| Service | Ports | Purpose |
|---------|-------|---------|
| Neo4j | 7474, 7687 | Code structure graph |
| Qdrant | 6333, 6334 | Vector embeddings |
| Letta | 8283 | Memory system (74% LOCOMO) |

**Embeddings**: OpenAI `text-embedding-3-small` (~$4/month)

## Environment Variables

```bash
OPENAI_API_KEY      # Required: Letta embeddings
CODEAGENT_HOME      # Default: ~/.codeagent
GITHUB_TOKEN        # Optional: GitHub MCP
TAVILY_API_KEY      # Optional: Web research
```

## Design Philosophy

1. **Partner, not assistant** - Challenge assumptions, push back on bad ideas
2. **Memory-first** - Query Letta/code-graph before external research
3. **External validation** - Never self-review, use tools (semgrep, linters)
4. **TDD always** - Test → Fail → Code → Pass
5. **Accuracy over speed** - Spend tokens for correctness

## Detailed Documentation

- `Docs/Implementation.md` - Full technical specification
- `Docs/ProjectVision.md` - Research backing and design decisions
- `Docs/McpInstallWorkflow.md` - MCP installation details
- `README.md` - User-facing documentation
