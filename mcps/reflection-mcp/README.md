# reflection-mcp

Self-reflection MCP server with persistent episodic memory.
Based on Reflexion research showing +21% improvement on HumanEval.

## Features

- **Persistent Storage**: Episodes saved to `~/.codeagent/data/reflection-episodes/`
- **Lesson Effectiveness Tracking**: Track if applying lessons leads to success
- **Cross-Session Learning**: Aggregate patterns across sessions
- **Learner Skill Integration**: Export lessons for project memory

## MCP Tools

| Tool | Description |
|------|-------------|
| `reflect_on_failure` | Generate structured reflection on failure |
| `store_episode` | Store learning episode in memory |
| `retrieve_episodes` | Find similar past episodes |
| `generate_improved_attempt` | Generate guidance for improvement |
| `get_reflection_history` | View reflection history |
| `get_common_lessons` | Get aggregated lessons by type |
| `clear_episodes` | Clear episodic memory |
| `get_episode_stats` | Get statistics about memory |
| `mark_lesson_effective` | Track lesson effectiveness |
| `export_lessons` | Export for learner skill |
| `link_episode_to_lesson` | Link episode to applied lesson |

## Feedback Types

| Type | Description |
|------|-------------|
| `test_failure` | Test assertion failed |
| `lint_error` | Linter rule violation |
| `build_error` | Compilation/build failure |
| `review_comment` | Code review feedback |
| `runtime_error` | Runtime exception |
| `security_issue` | Security vulnerability |
| `performance_issue` | Performance problem |
| `type_error` | Type mismatch |

## Installation

```bash
pip install -e .
```

## Usage

```bash
python -m reflection_mcp.server
```

## Environment Variables

```bash
CODEAGENT_HOME  # Storage location (default: ~/.codeagent)
```

## Storage

Episodes and lessons are persisted as JSON files in:
```
~/.codeagent/data/reflection-episodes/
├── episodes.json    # All episodes
└── lessons.json     # Aggregated patterns
```
