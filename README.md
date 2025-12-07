# CodeAgent

Research-backed autonomous coding framework for Claude Code. Transforms Claude Code into an accuracy-optimized system with memory, planning, and TDD enforcement.

## Features

- **Memory-First Research** - Query past implementations before external search
- **Tree-of-Thought Planning** - Explore 3+ approaches before committing
- **TDD Enforcement** - Strict test-first development workflow
- **External Validation** - Never self-review, always use tools
- **Pattern Learning** - Extract and store learnings for future tasks
- **Parallel Execution Analysis** - Automatic detection of parallelizable work

## Quick Install

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/codeagent.git
cd codeagent
./install.sh

# Or one-liner (after publishing)
# curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/codeagent/main/install.sh | bash
```

## Requirements

- **Docker** with Docker Compose v2
- **Node.js** (for MCP servers)
- **Python 3** (for custom MCPs)
- **Claude Code CLI** (optional, for MCP configuration)

## Usage

### Start Infrastructure

```bash
codeagent start    # Start Neo4j, Qdrant, Letta
codeagent status   # Check health
codeagent stop     # Stop services
```

### Initialize a Project

```bash
cd /your/project
codeagent init     # Sets up skills, commands, settings
```

### Slash Commands

| Command | Description |
|---------|-------------|
| `/scan` | Build knowledge graph of your codebase |
| `/plan "task"` | Research + design with Tree-of-Thought |
| `/implement` | TDD execution with quality gates |
| `/integrate` | Merge parallel work streams |
| `/review` | External tool validation |

## Skills

CodeAgent provides 6 specialized skills that activate based on context:

| Skill | Purpose | Activates When |
|-------|---------|----------------|
| `researcher` | Memory-first context gathering | Exploring codebase, gathering info |
| `architect` | Tree-of-Thought solution design | Planning features, making decisions |
| `orchestrator` | Parallel execution analysis | Multiple subtasks detected |
| `implementer` | Strict TDD workflow | Writing code, implementing features |
| `reviewer` | External tool validation | Reviewing code, validating changes |
| `learner` | Pattern extraction | After successful implementations |

## Infrastructure

| Service | Port | Purpose |
|---------|------|---------|
| Neo4j | 7474, 7687 | Code structure graph |
| Qdrant | 6333 | Vector embeddings |
| Letta | 8283 | Memory system (74% LOCOMO accuracy) |

**Cost**: ~$4/month for OpenAI embeddings (`text-embedding-3-small`)

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY      # Required - for memory embeddings
GITHUB_TOKEN        # Optional - for GitHub MCP
TAVILY_API_KEY      # Optional - for web research
```

### Project Structure After `codeagent init`

```
your-project/
├── CLAUDE.md                 # Project config (customize!)
├── .claude/
│   ├── settings.json         # Permissions, hooks, MCPs
│   ├── skills/               # Skill definitions
│   │   ├── researcher/
│   │   ├── architect/
│   │   ├── orchestrator/
│   │   ├── implementer/
│   │   ├── reviewer/
│   │   └── learner/
│   └── commands/             # Slash commands
│       ├── scan.md
│       ├── plan.md
│       ├── implement.md
│       ├── integrate.md
│       └── review.md
└── docs/
    └── decisions/            # Architecture decision records
```

## MCP Servers

CodeAgent configures these MCP servers:

**Core:**
- `filesystem` - File system access
- `git` - Git operations
- `memory` - Basic memory
- `sequential-thinking` - Complex reasoning

**Research:**
- `context7` - Library documentation
- `fetch` - URL fetching

**Validation:**
- `semgrep` - Security scanning

**Optional (require API keys):**
- `github` - GitHub integration
- `tavily` - Web research
- `letta` - Advanced memory (requires `codeagent start`)

## Workflow Example

```bash
# 1. Start infrastructure
codeagent start

# 2. Initialize project
cd /your/project
codeagent init

# 3. In Claude Code:
/scan                        # Build knowledge graph (first time)
/plan "Add user authentication"  # Research + design
/implement                   # TDD implementation
/review                      # Validate with external tools
```

## Uninstall

```bash
./uninstall.sh
```

This removes CodeAgent but preserves:
- Your `~/.claude/` directory
- Your project `.claude/` directories
- Docker volume data (optional to remove)

## Philosophy

1. **Memory-first** - Query memory before external research
2. **Single-agent implementation** - Multi-agent fragments context
3. **External validation** - Never self-review code
4. **TDD always** - Test → Fail → Code → Pass
5. **Accuracy over speed** - Spend tokens for correctness

## License

MIT

## Contributing

Contributions welcome! Please read the design docs in `Docs/` before submitting PRs.
