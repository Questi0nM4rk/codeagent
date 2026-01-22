# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CodeAgent** is a research-backed autonomous coding framework for Claude Code. Transforms Claude into an accuracy-optimized system with persistent memory, structured reasoning, and TDD enforcement.

**Core thesis**: Never guess. Accuracy over speed. Memory-first intelligence.

## Development Commands

```bash
# Validate shell scripts
shellcheck install.sh bin/* framework/hooks/*.sh

# Test reflection MCP (external repo)
cd ~/Projects/reflection-mcp && ~/.codeagent/venv/bin/python -m pytest

# Run reflection MCP standalone (requires package installed in venv)
~/.codeagent/venv/bin/python -m reflection_mcp

# Infrastructure control
codeagent start              # Start Qdrant
codeagent stop               # Stop services
codeagent status             # Health check (-w for watch, -r auto-restart)
codeagent logs -f qdrant     # Follow Qdrant logs

# Docker direct access
cd infrastructure && docker compose up -d
docker compose logs -f

# Install/reinstall
./install.sh                 # First install
./install.sh --force         # Force reinstall (keeps data)
./install.sh --reset         # Delete ALL data and reinstall
./install.sh --local         # Development mode (copy from local)
```

## Architecture

```
User: /scan → /plan → /implement → /integrate → /review
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   Skills Layer      MCP Servers      Infrastructure
   (6 agents)    (reflection, amem)    (Qdrant, local)
```

### Key Files

| File | Purpose |
|------|---------|
| `bin/codeagent` | Main CLI dispatcher (routes to subcommands) |
| `bin/codeagent-init` | Project initialization (creates .claude/, docs/) |
| `install.sh` | Full installation with dependency checks |
| `mcps/install-mcps.sh` | MCP registration to Claude Code |
| `mcps/mcp-registry.json` | MCP server definitions and install status |
| `infrastructure/docker-compose.yml` | Qdrant service definitions |
| `framework/settings.json.template` | Claude Code settings template |

### Source Directories

| Directory | Purpose |
|-----------|---------|
| `bin/` | CLI entry points (12 executables) |
| `framework/skills/` | Skill definitions (SKILL.md each) |
| `framework/commands/` | Slash command specs (5 commands) |
| `framework/hooks/` | Pre/post tool hooks (4 CodeAgent + 4 ai-guardrails) |
| `framework/agents/` | Agent definitions for Task tool |
| `mcps/` | Custom Python MCP servers + installers |
| `mcps/installers/` | Per-MCP installation scripts |
| `infrastructure/` | Docker Compose for Qdrant |
| `templates/` | CLAUDE.md templates by language |
| `scripts/` | Utility scripts (backup, restore, update) |
| `Docs/` | Vision, implementation docs, workflows |

## MCP System

### Registry Structure (mcps/mcp-registry.json)

Defines all MCPs with their installation requirements:
- `type`: npm | python | docker | builtin
- `package`: Package name for installation
- `args`: Command-line arguments
- `env`: Required environment variables
- `dependencies`: Other MCPs that must be running

### Custom MCP: Reflection

**Location**: `~/Projects/reflection-mcp/src/reflection_mcp/server.py` (external repo)

Implements Reflexion pattern (NeurIPS 2023) for +21% accuracy on code tasks.

**Tools provided:**
- `reflect_on_failure` - Analyze failures, generate structured insights
- `store_episode` - Store learning episode in episodic memory
- `retrieve_episodes` - Find similar past failures
- `generate_improved_attempt` - Guidance based on past lessons
- `mark_lesson_effective` - Track if applying lesson led to success
- `export_lessons` - Export for learner skill integration
- `get_model_effectiveness` - Get model success rates for intelligent model selection
- `get_reflection_history` - View reflection history for a task
- `get_common_lessons` - Get aggregated lessons by feedback type
- `get_episode_stats` - Get statistics about episodic memory

**Data storage**: `~/.codeagent/data/reflection-episodes/`

## A-MEM Memory System

Brain-like memory based on NeurIPS 2025 paper "A-MEM: Agentic Memory for LLM Agents".

### Two Memory Systems

| Aspect | **Reflection** | **A-MEM** |
|--------|---------------|-----------|
| **Memory Type** | Episodic (experiences) | Semantic (knowledge) |
| **What it stores** | Task attempts, failures, lessons | Patterns, architectures, decisions |
| **Question it answers** | "Did this fail before?" | "What architecture do we use?" |
| **Key feature** | Returns raw episodes | **Auto-links** memories, evolves over time |
| **Scope** | Per-session/task | Global (shared across all projects) |

### A-MEM Features

- **Automatic linking**: New memories connect to related existing ones (Zettelkasten-style)
- **Memory evolution**: New information updates existing memories' context
- **Rich metadata**: Auto-generated keywords, context, and tags
- **Global storage**: Shared at `~/.codeagent/memory/` across all projects

### A-MEM Tools Reference

```python
# Store (auto-generates keywords, context, tags, links)
mcp__amem__store_memory(content="JaCore uses repository pattern", tags=["architecture"])

# Search (semantic similarity + link traversal)
mcp__amem__search_memory(query="data access patterns", k=5)

# Read specific memory
mcp__amem__read_memory(memory_id="mem_0001")

# List and filter
mcp__amem__list_memories(limit=10, project="JaCore")

# Update (triggers re-evolution of links)
mcp__amem__update_memory(memory_id="mem_0001", content="Updated content")

# Statistics
mcp__amem__get_memory_stats()
```

### Memory Evolution Example

```
# Store first memory
store_memory("JaCore uses repository pattern")
→ Keywords: [repository, pattern, JaCore]

# Store related memory
store_memory("Unit of Work wraps repository transactions")
→ Keywords: [unit, work, repository, transactions]
→ Auto-linked to "repository pattern" memory
→ Original memory's context updated to include "transactions"
```

### Project Tagging

Use `project:NAME` tag to filter memories by project:
```python
store_memory("...", tags=["project:JaCore", "architecture"])
search_memory("...", project="JaCore")  # Filters by project tag
```

## Skills System

Skills auto-activate based on file types and context. Each skill has a SKILL.md in `framework/skills/`:

| Skill | Thinking | Behavior |
|-------|----------|----------|
| researcher | `think hard` | Query A-MEM → external. Say "I don't know" if unfound |
| architect | `ultrathink` | Generate 3+ approaches, present tradeoffs |
| orchestrator | `think harder` | Analyze isolation boundaries. Only parallelize truly isolated tasks |
| implementer | `think hard` | TDD loop: test → fail → code → pass. Max 3 attempts before escalate |
| reviewer | `think hard` | External tools only. Never self-validate |
| learner | `think` | Extract patterns post-implementation, store in A-MEM |

## Slash Commands

| Command | Agent Pipeline | Output |
|---------|---------------|--------|
| `/scan` | indexer → memory-writer | Knowledge base in A-MEM |
| `/plan "task"` | researcher → architect → orchestrator | Plan file with parallel decision |
| `/implement` | implementer (parallel if plan allows) | TDD commits, test results |
| `/integrate` | validator | Merged work, consistency check |
| `/review` | reviewer | External tool validation |

## Hooks

| Hook | Trigger | Source |
|------|---------|--------|
| `dangerous-command-check` | PreToolUse:Bash | ai-guardrails |
| `pre-commit` | PreToolUse:Bash(git commit) | ai-guardrails |
| `pre-push` | PreToolUse:Bash(git push) | ai-guardrails |
| `auto-format` | PostToolUse:Write/Edit | ai-guardrails |
| `index-file` | PostToolUse:Write/Edit | CodeAgent |
| `session-end` | Stop | CodeAgent |

**Note**: Shared hooks are symlinked from `~/.ai-guardrails/lib/hooks/` at install time.

## Infrastructure

| Service | Version | Ports | Health Check |
|---------|---------|-------|--------------|
| Qdrant | v1.16.2 | 6333, 6334 | TCP socket (no curl in image) |

**Resource limits** (docker-compose.yml):
- Qdrant: 2GB RAM, 2 CPUs

**Local storage:**
- A-MEM: `~/.codeagent/memory/` (ChromaDB/JSON)

## Installation Structure

### Global (~/.codeagent/)

```
~/.codeagent/
├── bin/                # CLI executables (symlinked to ~/.local/bin/)
├── mcps/               # Custom MCP servers
├── infrastructure/     # docker-compose.yml
├── venv/               # Python virtualenv for MCPs
├── data/               # Persistent data (reflection episodes)
└── .env                # API keys (OPENAI_API_KEY, GITHUB_TOKEN, TAVILY_API_KEY)
```

### Claude Config (~/.claude/)

```
~/.claude/
├── CLAUDE.md           # Global personality + instructions
├── settings.json       # Permissions, hooks, MCP config
├── skills/             # Skill definitions
├── commands/           # Slash command specs
├── hooks/              # Hook scripts
└── agents/             # Agent definitions for Task tool
```

### Per-Project

Created by `codeagent init`:
```
project/
├── .claude/
│   └── project-info    # Project metadata for memory tagging
└── docs/
    └── decisions/      # Architecture decision records
```

## Troubleshooting

### Services not starting
```bash
codeagent status              # Check health
docker logs codeagent-qdrant  # View Qdrant logs
codeagent stop && codeagent start  # Restart
```

### Qdrant unhealthy
```bash
# Check container status
docker inspect --format='{{.State.Health.Status}}' codeagent-qdrant

# Restart with fresh containers
cd ~/.codeagent/infrastructure && docker compose down && docker compose up -d
```

### A-MEM issues
```bash
# Check storage directory
ls -la ~/.codeagent/memory/

# Test MCP (requires pip install -e ~/Projects/amem-mcp in venv)
~/.codeagent/venv/bin/python -c "from amem_mcp import server; print('OK')"
```

### MCP not connecting
```bash
claude mcp list                           # Check registered MCPs
~/.codeagent/mcps/install-mcps.sh --force # Force reinstall all MCPs
```

### Reflection MCP issues
```bash
# Test standalone (requires pip install -e ~/Projects/reflection-mcp in venv)
~/.codeagent/venv/bin/python -c "from reflection_mcp import server; print('OK')"

# Check data directory
ls -la ~/.codeagent/data/reflection-episodes/
```

## Design Principles

1. **Partner, not assistant** - Challenge assumptions, push back on bad ideas
2. **Memory-first** - Query A-MEM → external. Never fabricate
3. **External validation** - Never self-review. Use linters, tests, security scanners
4. **TDD always** - Test → fail → code → pass
5. **Accuracy over speed** - Spend tokens for correctness
6. **Single agent for shared code** - Only parallelize isolated tasks
