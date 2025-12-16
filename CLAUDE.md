# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**CodeAgent** is a research-backed autonomous coding framework for Claude Code. It provides skills, commands, MCP servers, and Docker infrastructure to transform Claude Code into an accuracy-optimized system.

## Development Commands

```bash
# Validate shell scripts
shellcheck install.sh bin/* framework/hooks/*.sh

# Test custom MCP servers
~/.codeagent/venv/bin/python -m pytest mcps/code-graph-mcp/
~/.codeagent/venv/bin/python -m pytest mcps/tot-mcp/
~/.codeagent/venv/bin/python -m pytest mcps/reflection-mcp/

# Infrastructure management
codeagent start        # Start Neo4j, Qdrant, Letta
codeagent stop         # Stop services
codeagent status       # Health check
codeagent config       # Configure API keys

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

## Source Directories

| Directory | Purpose |
|-----------|---------|
| `bin/` | CLI entry points (codeagent, codeagent-start, etc.) |
| `framework/skills/` | 6 skill definitions |
| `framework/commands/` | 5 slash commands |
| `framework/hooks/` | Pre/post tool hooks |
| `mcps/` | Custom Python MCP servers |
| `infrastructure/` | Docker Compose for Neo4j, Qdrant, Letta |
| `templates/` | CLAUDE.md templates by language |

## Custom MCPs

| MCP | Backend | Purpose |
|-----|---------|---------|
| `code-graph-mcp` | Neo4j | AST-based code knowledge graph |
| `tot-mcp` | In-memory | Tree-of-Thought reasoning |
| `reflection-mcp` | Qdrant | Self-reflection and episodic memory |

## Skills System

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
| `/plan "task"` | Research and design |
| `/implement` | TDD execution |
| `/integrate` | Merge parallel work |
| `/review` | External validation |

## Infrastructure

| Service | Version | Ports |
|---------|---------|-------|
| Neo4j | 5.26.0-community | 7474, 7687 |
| Qdrant | v1.16.2 | 6333, 6334 |
| Letta | 0.16.0 | 8283 |

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | Letta embeddings |
| `GITHUB_TOKEN` | No | GitHub MCP |
| `TAVILY_API_KEY` | No | Web research |

## Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `dangerous-command-check` | PreToolUse:Bash | Block dangerous commands |
| `pre-commit` | PreToolUse:Bash(git commit) | Pre-commit checks |
| `pre-push` | PreToolUse:Bash(git push) | Pre-push checks |
| `auto-format` | PostToolUse:Write/Edit | Format code |
| `index-file` | PostToolUse:Write/Edit | Update code graph |
| `session-end` | Stop | Cleanup temp files |

## Installation Structure

### Global (install.sh)

```
~/.claude/
├── CLAUDE.md           # Personality + instructions
├── settings.json       # Permissions, hooks
├── skills/             # 6 skill definitions
├── commands/           # 5 slash commands
└── hooks/              # Hook scripts

~/.codeagent/
├── bin/                # CLI tools
├── mcps/               # Custom MCP servers
├── templates/          # CLAUDE.md templates
├── infrastructure/     # docker-compose.yml
└── .env                # API keys
```

### Per-Project (codeagent init)

```
project/
├── .claude/
│   └── letta-agent     # Letta agent ID
└── docs/
    └── decisions/      # ADRs
```

## Design Principles

1. **Partner, not assistant** - Challenge assumptions
2. **Memory-first** - Query Letta/code-graph before research
3. **External validation** - Never self-review
4. **TDD always** - Test, fail, code, pass
5. **Accuracy over speed** - Spend tokens for correctness
