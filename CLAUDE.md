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
~/.codeagent/venv/bin/python -m pytest mcps/reflection-mcp/

# Infrastructure
codeagent start        # Start Qdrant, Letta
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
   (6 agents)       (reflection)       (Qdrant, Letta)
```

### Source Directories

| Directory | Purpose |
|-----------|---------|
| `bin/` | CLI entry points (codeagent, codeagent-start, etc.) |
| `framework/skills/` | 6 skill definitions (SKILL.md each) |
| `framework/commands/` | 5 slash command specs |
| `framework/hooks/` | Pre/post tool hooks (7 scripts) |
| `mcps/` | Custom Python MCP servers + installers |
| `infrastructure/` | Docker Compose for Qdrant, Letta |
| `templates/` | CLAUDE.md templates by language (cpp, dotnet, lua, rust) |
| `scripts/` | Utility scripts (backup, restore, health-check) |
| `Docs/` | Vision, implementation docs, workflows |

## Research Foundation

The custom MCPs implement findings from academic research:

| MCP | Backend | Research | Improvement |
|-----|---------|----------|-------------|
| `reflection` | Qdrant | Reflexion (NeurIPS 2023) | +21% on code tasks |

**Letta memory**: 74% LOCOMO accuracy vs basic persistence.

## Letta Memory System

### Two Memory Systems: Letta vs Reflection

| Aspect | **Reflection** | **Letta** |
|--------|---------------|-----------|
| **Memory Type** | Episodic (experiences) | Semantic (knowledge) |
| **What it stores** | Task attempts, failures, lessons | Patterns, architectures, decisions |
| **Question it answers** | "Did this fail before?" | "What architecture do we use?" |
| **Key feature** | Returns raw episodes | **Synthesizes** answers via LLM |

**Simple rule:**
- **Reflection**: Learning from mistakes ("what happened")
- **Letta**: Project knowledge base ("what do we know")

### Letta Tools Reference

**Query memory:**
```
mcp__letta__prompt_agent(agent_id, message)  # Ask Letta, get synthesized answer
mcp__letta__list_passages(agent_id, search)  # Search archival memory
```

**Store memory:**
```
mcp__letta__create_passage(agent_id, text)   # Add to archival memory
```

**Update memory:**
```
mcp__letta__modify_passage(agent_id, memory_id, update_data)
mcp__letta__delete_passage(agent_id, memory_id)
```

### Memory Format Standard

Store memories in this format for consistent retrieval:

```markdown
## [Category]: [Name]
Type: architectural|code|testing|process
Context: [when this applies]
Files: [reference files]

### Description
[What this pattern/decision solves]

### Implementation
[How it was done]

### Rationale
[Why this approach was chosen]
```

### When to Use Each

| Scenario | Use | Why |
|----------|-----|-----|
| Test failed, need similar failures | **Reflection** | Track failure chains |
| Need to know project architecture | **Letta** | Get synthesized answer |
| Track that approach X didn't work | **Reflection** | Episodic memory |
| Store a design decision | **Letta** | Project knowledge |
| Check if I tried this before | **Reflection** | Task-specific history |
| Ask "why did we choose X?" | **Letta** | Contextual answer |

### Project Agent ID

Each project has a Letta agent ID stored in `.claude/letta-agent`.
Use this ID for all Letta calls in that project.

## Skills System

Each skill has a SKILL.md in `framework/skills/`:

| Skill | Thinking | Behavior |
|-------|----------|----------|
| researcher | `think hard` | Query Letta → external. Say "I don't know" if unfound |
| architect | `ultrathink` | Generate 3+ approaches, present tradeoffs |
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
| `session-end` | Stop | Cleanup temp files |

## Infrastructure

| Service | Version | Ports | Notes |
|---------|---------|-------|-------|
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

## Design Principles

1. **Partner, not assistant** - Challenge assumptions, push back on bad ideas
2. **Memory-first** - Query Letta → external. Never fabricate
3. **External validation** - Never self-review. Use linters, tests, security scanners
4. **TDD always** - Test → fail → code → pass
5. **Accuracy over speed** - Spend tokens for correctness
6. **Single agent for shared code** - Only parallelize isolated tasks
