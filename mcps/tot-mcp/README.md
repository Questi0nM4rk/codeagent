# tot-mcp

Tree-of-Thought MCP server for systematic solution exploration.
Based on ToT research showing +70% improvement on complex reasoning tasks.

## Features

- **Persistent Storage**: Thought trees saved to `~/.codeagent/data/thought-trees/`
- **Thinking Level Integration**: Maps complexity to Claude's `think`/`think hard`/`ultrathink`
- **Advanced Pruning**: Alpha-beta style pruning, weighted criteria, diversity preservation
- **Multiple Strategies**: greedy, beam, sampling, diverse

## MCP Tools

| Tool | Description |
|------|-------------|
| `create_tree` | Initialize a new thought tree for a problem |
| `generate_thoughts` | Add candidate approaches to current node |
| `evaluate_thoughts` | Score thoughts against weighted criteria |
| `select_path` | Choose path(s) based on strategy |
| `expand_thought` | Add detail to a specific thought |
| `backtrack` | Mark path as failed, return to parent |
| `get_tree_state` | Get current state visualization |
| `get_best_path` | Get highest-scoring complete path |
| `list_trees` | List all persisted trees |
| `delete_tree` | Remove a thought tree |
| `set_criteria_weights` | Adjust criterion importance |

## Strategies

| Strategy | Description |
|----------|-------------|
| `greedy` | Always pick highest score |
| `beam` | Keep top-k candidates |
| `sampling` | Probabilistic selection |
| `diverse` | Maximize diversity among selections |

## Thinking Levels

The server auto-detects appropriate thinking level based on problem complexity:

| Level | Indicators |
|-------|------------|
| `ultrathink` | Architecture, design, system decisions |
| `think harder` | Refactoring, optimization, algorithms |
| `think hard` | Implementation, features, modules |
| `think` | Simple fixes, straightforward tasks |

## Installation

```bash
pip install -e .
```

## Usage

```bash
python -m tot_mcp.server
```

## Environment Variables

```bash
CODEAGENT_HOME  # Storage location (default: ~/.codeagent)
```

## Storage

Trees are persisted as JSON files in:
```
~/.codeagent/data/thought-trees/{tree_id}.json
```
