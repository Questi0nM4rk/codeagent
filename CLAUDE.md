# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CodeAgent** is a research-backed autonomous coding framework for Claude Code. It transforms Claude Code into an accuracy-optimized system with persistent memory, structured reasoning, and TDD enforcement.

**Core thesis**: Never guess. Accuracy over speed. Memory-first intelligence backed by 1,400+ academic papers.

## Development Commands

```bash
# Validate shell scripts
shellcheck install.sh bin/* framework/hooks/*.sh

# Test custom MCP servers
~/.codeagent/venv/bin/python -m pytest mcps/code-graph-mcp/
~/.codeagent/venv/bin/python -m pytest mcps/tot-mcp/
~/.codeagent/venv/bin/python -m pytest mcps/reflection-mcp/

# Infrastructure
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
User: /scan → /plan → /implement → /integrate → /review
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   Skills Layer      MCP Servers      Infrastructure
   (6 agents)       (code-graph,     (Neo4j, Qdrant,
                     tot, reflection)     Letta)
```

### Source Directories

| Directory | Purpose |
|-----------|---------|
| `bin/` | CLI entry points (codeagent, codeagent-start, etc.) |
| `framework/skills/` | 6 skill definitions (SKILL.md each) |
| `framework/commands/` | 5 slash command specs |
| `framework/hooks/` | Pre/post tool hooks (7 scripts) |
| `mcps/` | Custom Python MCP servers + installers |
| `infrastructure/` | Docker Compose for Neo4j, Qdrant, Letta |
| `templates/` | CLAUDE.md templates by language (cpp, dotnet, lua, rust) |
| `scripts/` | Utility scripts (backup, restore, health-check) |
| `Docs/` | Vision, implementation docs, workflows |

## Research Foundation

The custom MCPs implement findings from academic research:

| MCP | Backend | Research | Improvement |
|-----|---------|----------|-------------|
| `code-graph` | Neo4j | GraphRAG | +75% code retrieval |
| `tot` | In-memory | Tree-of-Thought | +70% complex reasoning |
| `reflection` | Qdrant | Reflexion (NeurIPS 2023) | +21% on code tasks |

**Letta memory**: 74% LOCOMO accuracy vs basic persistence.

## Skills System

Each skill has a SKILL.md in `framework/skills/`:

| Skill | Thinking | Behavior |
|-------|----------|----------|
| researcher | `think hard` | Query Letta → code-graph → external. Say "I don't know" if unfound |
| architect | `ultrathink` | Generate 3+ approaches with ToT, present tradeoffs |
| orchestrator | `think harder` | Analyze isolation boundaries. Only parallelize truly isolated tasks |
| implementer | `think hard` | TDD loop: test → fail → code → pass. Max 3 attempts before escalate |
| reviewer | `think hard` | External tools only. Never self-validate |
| learner | `think` | Extract patterns post-implementation, store in Letta |

## Parallelization Logic

From research: multi-agent fragments context for *shared* code.

```
PARALLEL (spawn subagents):        SEQUENTIAL (single agent):
  Agent A: UserController            Agent A: UserController (uses JwtService)
  Agent B: ProductController         Agent B: AuthController (modifies JwtService)
  → No shared code                   → Shared dependency
```

The orchestrator skill detects this automatically.

## Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `dangerous-command-check` | PreToolUse:Bash | Block rm -rf /, fork bombs, disk writes |
| `pre-commit` | PreToolUse:Bash(git commit) | Pre-commit validations |
| `pre-push` | PreToolUse:Bash(git push) | Security + tests before push |
| `auto-format` | PostToolUse:Write/Edit | Format by file type |
| `index-file` | PostToolUse:Write/Edit | Update code-graph |
| `post-implement` | PostToolUse:Write | Update graph after TDD |
| `session-end` | Stop | Cleanup temp files |

## Infrastructure

| Service | Version | Ports | Notes |
|---------|---------|-------|-------|
| Neo4j | 5.26.0-community | 7474, 7687 | APOC enabled |
| Qdrant | v1.16.2 | 6333, 6334 | Scalar quantization |
| Letta | 0.16.0 | 8283 | Depends on Qdrant health |

Health checks use Python-based testing (curl not available in Letta container).

## Installation Structure

### Global (install.sh)

```
~/.claude/
├── CLAUDE.md           # Personality + instructions
├── settings.json       # Permissions, hooks
├── skills/             # Symlinks to framework/skills/
├── commands/           # Symlinks to framework/commands/
└── hooks/              # Hook scripts

~/.codeagent/
├── bin/                # CLI tools (6 executables)
├── mcps/               # Custom MCP servers
├── templates/          # CLAUDE.md templates
├── infrastructure/     # docker-compose.yml
└── .env                # API keys
```

### Per-Project (codeagent init)

```
project/
├── .claude/
│   └── letta-agent     # Letta agent ID for project memory
└── docs/
    └── decisions/      # Architecture decision records
```

## Language Support

Code-graph MCP parses: C# (.NET), C/C++, Rust, Lua, Python, TypeScript/JavaScript, Go, Bash (9 languages).

## Design Principles

1. **Partner, not assistant** - Challenge assumptions, push back on bad ideas
2. **Memory-first** - Query Letta → code-graph → external. Never fabricate
3. **External validation** - Never self-review. Use linters, tests, security scanners
4. **TDD always** - Test → fail → code → pass
5. **Accuracy over speed** - Spend tokens for correctness
6. **Single agent for shared code** - Only parallelize isolated tasks
