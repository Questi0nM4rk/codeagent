# CodeAgent

Research-backed autonomous coding framework for Claude Code. Transforms Claude Code into an accuracy-optimized system with memory, structured reasoning, and TDD enforcement.

## Features

- **Memory-First Research** - Letta-powered memory system (74% LOCOMO accuracy) for context retention
- **Tree-of-Thought Planning** - Explore multiple approaches before committing to a solution
- **TDD Enforcement** - Strict test-first development workflow
- **External Validation** - Never self-review, always use external tools
- **Code Knowledge Graph** - AST-based code analysis with Neo4j
- **Self-Reflection** - Learn from failures and improve over time

## Quick Install

```bash
# Clone and install
git clone https://github.com/Questi0nM4rk/codeagent.git
cd codeagent
./install.sh

# Or one-liner
curl -fsSL https://raw.githubusercontent.com/Questi0nM4rk/codeagent/main/install.sh | bash
```

### What Gets Installed

- CLI commands (`codeagent`, `codeagent-start`, etc.) in `~/.local/bin/`
- Framework files in `~/.codeagent/`
- Claude Code skills and commands in `~/.claude/`
- MCP servers (global user scope)
- Docker infrastructure (Neo4j, Qdrant, Letta)

## Requirements

- **Docker** with Docker Compose v2
- **Node.js 18+** (for MCP servers)
- **Python 3.10+** (for custom MCPs)
- **Claude Code CLI** (`claude` command)

## Usage

### Start Infrastructure

```bash
codeagent start    # Start Neo4j, Qdrant, Letta containers
codeagent status   # Check health of all services
codeagent stop     # Stop services
```

### Slash Commands

Use these in Claude Code conversations:

| Command | Description |
|---------|-------------|
| `/scan` | Build knowledge graph of your codebase |
| `/plan "task"` | Research + design with Tree-of-Thought |
| `/implement` | TDD execution with quality gates |
| `/integrate` | Merge parallel work streams |
| `/review` | External tool validation |

### Skills

CodeAgent provides 6 specialized skills that activate automatically based on context:

| Skill | Purpose | Activates When |
|-------|---------|----------------|
| `researcher` | Memory-first context gathering | Exploring codebase, gathering info |
| `architect` | Tree-of-Thought solution design | Planning features, making decisions |
| `orchestrator` | Parallel execution analysis | Multiple subtasks detected |
| `implementer` | Strict TDD workflow | Writing code, implementing features |
| `reviewer` | External tool validation | Reviewing code, validating changes |
| `learner` | Pattern extraction | After successful implementations |

## MCP Servers

CodeAgent installs and configures these MCP servers (all in global user scope):

### Core MCPs

| MCP | Purpose |
|-----|---------|
| `sequential-thinking` | Step-by-step complex reasoning |
| `context7` | Up-to-date library documentation |

### Custom MCPs (Python)

| MCP | Purpose |
|-----|---------|
| `code-graph` | AST-based code analysis with Neo4j backend |
| `tot` | Tree-of-Thought structured exploration |
| `reflection` | Self-reflection and episodic memory for learning |

### Infrastructure MCPs

| MCP | Purpose | Requires |
|-----|---------|----------|
| `letta` | Advanced memory system (74% LOCOMO accuracy) | `codeagent start` |

### Optional MCPs (require API keys)

| MCP | Purpose | Environment Variable |
|-----|---------|---------------------|
| `github` | GitHub repository integration | `GITHUB_TOKEN` |
| `tavily` | Web search and research | `TAVILY_API_KEY` |

## Infrastructure

| Service | Ports | Purpose |
|---------|-------|---------|
| Neo4j | 7474 (HTTP), 7687 (Bolt) | Code structure graph database |
| Qdrant | 6333, 6334 | Vector embeddings storage |
| Letta | 8283 | Memory system with agents |

**Cost**: ~$4/month for OpenAI embeddings (`text-embedding-3-small`)

## Configuration

### Environment Variables

Set in `~/.codeagent/.env`:

```bash
OPENAI_API_KEY      # Required - for Letta memory embeddings
GITHUB_TOKEN        # Optional - for GitHub MCP
TAVILY_API_KEY      # Optional - for web research MCP
```

### Hooks

CodeAgent configures automatic hooks in `~/.claude/settings.json`:

- **Pre-commit/push hooks** - Run custom scripts before git operations
- **Post-edit hooks** - Auto-format code based on file type (.cs, .rs, .cpp, .lua, .sh)
- **File indexing** - Update code graph on file changes

### Project Initialization

Run `codeagent init` in any project to set up project-specific configuration:

```
your-project/
├── CLAUDE.md                 # Project-specific instructions
└── .claude/
    ├── settings.json         # Project settings
    ├── skills/               # 6 skill definitions
    └── commands/             # 5 slash commands
```

## Workflow Example

```bash
# 1. Start infrastructure (first time or after reboot)
codeagent start

# 2. Initialize your project
cd /your/project
codeagent init

# 3. In Claude Code:
/scan                            # Build knowledge graph (first time)
/plan "Add user authentication"  # Research + design
/implement                       # TDD implementation
/review                          # Validate with external tools
```

## Reinstall / Update

```bash
# Update to latest version
cd ~/.codeagent
git pull
./install.sh

# Force reinstall (wipes all Claude Code config, backs up first)
./install.sh --force
```

## Uninstall

```bash
./uninstall.sh
```

This removes:
- CLI commands from `~/.local/bin/`
- Framework files from `~/.codeagent/`
- MCP registrations

Optionally removes:
- Docker containers and volumes
- Claude Code configurations (`~/.claude/`)

## Philosophy

### Partner, Not Assistant

CodeAgent treats Claude as a **thinking partner**, not a compliant tool:

> "It's better to say 'I don't know' than to guess and be wrong."
> "It's better to push back on a bad idea now than to revert it later."

| Traditional Assistant | CodeAgent Partner |
|----------------------|-------------------|
| "Sure, I'll implement that" | "Before I implement - have you considered X?" |
| Guesses when uncertain | "I'm not confident about this approach" |
| Accepts all requests | "I'd push back on that because..." |

### Core Principles

1. **Partner before tool** - Challenge, discuss, collaborate
2. **Uncertainty before confidence** - Say "I don't know" when unsure
3. **Memory-first** - Query memory before external research
4. **Single-agent implementation** - Multi-agent fragments context
5. **External validation** - Never self-review code
6. **TDD always** - Test -> Fail -> Code -> Pass
7. **Accuracy over speed** - Spend tokens for correctness

## Troubleshooting

### MCPs not connecting

```bash
# Check MCP status
claude mcp list

# Reinstall MCPs
~/.codeagent/mcps/install-mcps.sh --force
```

### Docker services unhealthy

```bash
# Check container status
codeagent status

# View logs
docker logs codeagent-letta
docker logs codeagent-neo4j
docker logs codeagent-qdrant

# Restart services
codeagent stop && codeagent start
```

### Python MCP import errors

```bash
# Reinstall Python dependencies
~/.codeagent/venv/bin/pip install -e ~/.codeagent/mcps/code-graph-mcp
~/.codeagent/venv/bin/pip install -e ~/.codeagent/mcps/tot-mcp
~/.codeagent/venv/bin/pip install -e ~/.codeagent/mcps/reflection-mcp
```

## License

MIT

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

For major changes, please open an issue first to discuss the approach.
