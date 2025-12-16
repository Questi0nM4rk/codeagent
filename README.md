# CodeAgent

Research-backed autonomous coding framework for Claude Code. Transforms Claude Code into an accuracy-optimized system with persistent memory, structured reasoning, and TDD enforcement.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai/code)

## Features

| Feature | Description |
|---------|-------------|
| **Memory System** | Letta-powered memory with 74% LOCOMO accuracy |
| **Tree-of-Thought** | Explore multiple approaches before committing |
| **TDD Enforcement** | Strict test-first development workflow |
| **Code Knowledge Graph** | AST-based analysis with Neo4j |
| **Self-Reflection** | Learn from failures, improve over time |
| **External Validation** | Never self-review, always use tools |

## Quick Start

```bash
# Clone and install
git clone https://github.com/Questi0nM4rk/codeagent.git
cd codeagent
./install.sh

# Start infrastructure
codeagent start

# Initialize in your project
cd /your/project
codeagent init
```

## Requirements

- **Docker** with Docker Compose v2
- **Node.js 18+** for MCP servers
- **Python 3.10+** for custom MCPs
- **Claude Code CLI** (`claude` command)

## Commands

### CLI Commands

```bash
codeagent start     # Start Neo4j, Qdrant, Letta
codeagent stop      # Stop services
codeagent status    # Health check all services
codeagent config    # Configure API keys
codeagent init      # Initialize project (creates Letta agent)
```

### Slash Commands

Use in Claude Code conversations:

| Command | Description |
|---------|-------------|
| `/scan` | Build knowledge graph of codebase |
| `/plan "task"` | Research and design with Tree-of-Thought |
| `/implement` | TDD execution with quality gates |
| `/integrate` | Merge parallel work streams |
| `/review` | Validate with external tools |

## Skills

Six specialized skills auto-activate based on context:

| Skill | Purpose |
|-------|---------|
| `researcher` | Memory-first context gathering |
| `architect` | Tree-of-Thought solution design |
| `orchestrator` | Parallel execution analysis |
| `implementer` | Strict TDD workflow |
| `reviewer` | External tool validation |
| `learner` | Pattern extraction |

## MCP Servers

### Core MCPs

| MCP | Purpose |
|-----|---------|
| `sequential-thinking` | Step-by-step complex reasoning |
| `context7` | Up-to-date library documentation |

### Custom MCPs

| MCP | Backend | Purpose |
|-----|---------|---------|
| `code-graph` | Neo4j | AST-based code knowledge graph |
| `tot` | In-memory | Tree-of-Thought exploration |
| `reflection` | Qdrant | Self-reflection and episodic memory |

### Infrastructure MCPs

| MCP | Purpose |
|-----|---------|
| `letta` | Advanced memory system (74% LOCOMO accuracy) |

## Infrastructure

| Service | Version | Ports | Purpose |
|---------|---------|-------|---------|
| Neo4j | 5.26.0-community | 7474, 7687 | Code structure graph |
| Qdrant | v1.16.2 | 6333, 6334 | Vector embeddings |
| Letta | 0.16.0 | 8283 | Memory system |

**Embedding Cost**: ~$4/month (OpenAI `text-embedding-3-small`)

## Configuration

### API Keys

Configure with:

```bash
codeagent config
```

Keys stored in `~/.codeagent/.env`:

| Key | Required | Purpose |
|-----|----------|---------|
| `OPENAI_API_KEY` | Yes | Letta embeddings |
| `GITHUB_TOKEN` | No | GitHub MCP integration |
| `TAVILY_API_KEY` | No | Web research |

### Hooks

CodeAgent configures automatic hooks:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `dangerous-command-check` | Pre-Bash | Block dangerous commands |
| `pre-commit` | Pre-git commit | Run pre-commit checks |
| `pre-push` | Pre-git push | Run pre-push checks |
| `auto-format` | Post-Write/Edit | Format code by file type |
| `index-file` | Post-Write/Edit | Update code graph |
| `session-end` | Stop | Cleanup temporary files |

## Installation Structure

### Global

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

### Per-Project

Created by `codeagent init`:

```
project/
├── .claude/
│   └── letta-agent     # Letta agent ID
└── docs/
    └── decisions/      # Architecture decision records
```

## Workflow

```bash
# 1. Start infrastructure
codeagent start

# 2. Initialize project
cd /your/project
codeagent init
```

Then in Claude Code:

```
/scan                           # Build knowledge graph
/plan "Add authentication"      # Research + design
/implement                      # TDD implementation
/review                         # Validate
```

## Update

```bash
cd ~/.codeagent
git pull
./install.sh
```

## Uninstall

```bash
./uninstall.sh
```

## Philosophy

CodeAgent treats Claude as a **thinking partner**, not an assistant:

| Traditional | CodeAgent |
|-------------|-----------|
| "Sure, I'll implement that" | "Have you considered X?" |
| Guesses when uncertain | "I'm not confident about this" |
| Accepts all requests | "I'd push back because..." |

### Principles

1. **Partner before tool** - Challenge, discuss, collaborate
2. **Uncertainty before confidence** - Say "I don't know" when unsure
3. **Memory-first** - Query memory before external research
4. **External validation** - Never self-review code
5. **TDD always** - Test, fail, code, pass
6. **Accuracy over speed** - Spend tokens for correctness

## Troubleshooting

### Services not starting

```bash
codeagent status              # Check health
docker logs codeagent-letta   # View logs
codeagent stop && codeagent start
```

### MCPs not connecting

```bash
claude mcp list
~/.codeagent/mcps/install-mcps.sh --force
```

### Letta connection errors

```bash
# Verify API key
grep OPENAI_API_KEY ~/.codeagent/.env

# Reconfigure if missing
codeagent config

# Restart services
cd ~/.codeagent/infrastructure && docker compose restart letta
```

## License

MIT
