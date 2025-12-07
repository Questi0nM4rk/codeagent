# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CodeAgent** is a research-backed autonomous coding framework for Claude Code. It provides skills, commands, and infrastructure to transform Claude Code into an accuracy-optimized system.

## Quick Start

```bash
# Install
./install.sh

# Start infrastructure
codeagent start

# Initialize in a project
cd /your/project
codeagent init

# Use in Claude Code
/scan              # Build knowledge graph
/plan "task"       # Research & design
/implement         # TDD execution
/review            # Validate
```

## Repository Structure

```
codeagent/
├── install.sh                    # Main installer (handles existing configs)
├── uninstall.sh                  # Clean removal
├── CLAUDE.md                     # This file
│
├── bin/                          # CLI commands
│   ├── codeagent                 # Main CLI entry point
│   ├── codeagent-start           # Start Docker services
│   ├── codeagent-stop            # Stop services
│   ├── codeagent-status          # Health check
│   └── codeagent-init            # Initialize project
│
├── infrastructure/
│   ├── docker-compose.yml        # Neo4j, Qdrant, Letta (OpenAI embeddings)
│   └── neo4j/init.cypher         # Graph schema
│
├── framework/
│   ├── skills/                   # Claude Code skills (native feature)
│   │   ├── researcher/SKILL.md   # Context gathering
│   │   ├── architect/SKILL.md    # Solution design (ToT)
│   │   ├── orchestrator/SKILL.md # Parallel analysis
│   │   ├── implementer/SKILL.md  # TDD coding
│   │   ├── reviewer/SKILL.md     # External validation
│   │   └── learner/SKILL.md      # Pattern extraction
│   ├── commands/                 # Slash commands
│   │   ├── scan.md
│   │   ├── plan.md
│   │   ├── implement.md
│   │   ├── integrate.md
│   │   └── review.md
│   └── settings.json.template    # Permissions, hooks, MCP config
│
├── mcps/
│   ├── install-mcps.sh           # Configure MCP servers
│   ├── tot-mcp/                  # Tree-of-Thought (placeholder)
│   ├── reflection-mcp/           # Self-Reflection (placeholder)
│   └── code-graph-mcp/           # Code knowledge graph (placeholder)
│
├── templates/                    # Project CLAUDE.md templates
│   ├── dotnet/CLAUDE.md
│   ├── rust/CLAUDE.md
│   ├── cpp/CLAUDE.md
│   └── lua/CLAUDE.md
│
├── scripts/
│   ├── health-check.sh
│   ├── backup-memory.sh
│   ├── restore-memory.sh
│   └── update.sh
│
└── Docs/                         # Design documentation
    ├── ProjectVision.md
    ├── Implementation.md
    └── GitHubRepoStructure.md
```

## Claude Code Integration

### Skills (Native Feature)

Skills are Claude Code's extension system. Each skill is a directory with `SKILL.md`:

```yaml
---
name: skill-name
description: When to activate this skill
---

# Instructions Claude follows when skill is active
```

Skills activate automatically based on their description matching the user's request.

### Commands

Slash commands in `.claude/commands/`:

```yaml
---
description: What this command does
---

# Command instructions
```

### Settings

`settings.json` format:

```json
{
  "permissions": {
    "allow": ["Bash(npm:*)", "Read(**/*)", "mcp__github"],
    "deny": ["Bash(rm -rf:*)", "Read(./.env)"]
  },
  "hooks": {
    "PostToolUse": [{"matcher": "Edit", "hooks": [...]}]
  },
  "mcpServers": {
    "github": {"command": "npx", "args": [...]}
  }
}
```

## Key Commands

### CLI Commands

```bash
codeagent start      # Start Neo4j, Qdrant, Letta
codeagent stop       # Stop services
codeagent status     # Health check
codeagent init       # Initialize project
codeagent backup     # Backup memory
codeagent restore    # Restore backup
```

### Slash Commands

| Command | Description |
|---------|-------------|
| `/scan` | Build knowledge graph |
| `/plan "task"` | Research → Design |
| `/implement` | TDD execution |
| `/integrate` | Merge parallel work |
| `/review` | External validation |

## Skills System

| Skill | Purpose |
|-------|---------|
| researcher | Memory-first context gathering |
| architect | Tree-of-Thought solution design |
| orchestrator | Parallel execution analysis |
| implementer | Strict TDD workflow |
| reviewer | External tool validation |
| learner | Pattern extraction |

## Infrastructure

| Service | Port | Purpose |
|---------|------|---------|
| Neo4j | 7474, 7687 | Code graph |
| Qdrant | 6333 | Vectors |
| Letta | 8283 | Memory (74% LOCOMO) |

**Embeddings**: OpenAI `text-embedding-3-small` (~$4/month)

## Environment Variables

```bash
OPENAI_API_KEY      # Required for embeddings
CODEAGENT_HOME      # Install dir (default: ~/.codeagent)
GITHUB_TOKEN        # Optional: GitHub MCP
TAVILY_API_KEY      # Optional: Web research
```

## Design Philosophy

1. **Memory-first**: Query memory before external research
2. **Single-agent implementation**: Multi-agent fragments context
3. **External validation**: Never self-review
4. **TDD always**: Test → Fail → Code → Pass
5. **Accuracy over speed**: Spend tokens for correctness
