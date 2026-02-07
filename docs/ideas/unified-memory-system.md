# Unified Memory System

Brainstorming output from Epic 6 design session.

## Problem

4 separate MCP servers (~4,630 lines) with 36 tools, mixed embedding dimensions (384d + 1536d), sharing one libSQL file. Excessive context window cost, redundant patterns, no cross-domain queries.

## Key Insight

Semantic memory (A-MEM) and episodic memory (reflection) are not fundamentally different systems. They are **different types of the same thing**: a memory with an embedding, metadata, and graph connections.

## Memory Types

| Type | Replaces | Metadata |
|------|----------|----------|
| `knowledge` | amem `store_memory` | keywords, context, project |
| `episode` | reflection `store_episode` | task, approach, outcome, feedback, reflection, model_used |
| `decision` | (new - ADRs as memory) | options_considered, chosen, rationale, status |
| `pattern` | (new - extracted by learner) | language, category, frequency, last_applied |
| `code_chunk` | codebase `index_file` | file_path, language, chunk_type, name, lines, hash, deps |

## Unified Tool Surface (~15 tools)

Instead of 36 tools across 4 domains:

| Tool | Replaces | Description |
|------|----------|-------------|
| `store` | store_memory, store_episode, index_file | Store any memory type (auto-embeds, auto-links) |
| `search` | search_memory, retrieve_episodes, search | Hybrid search (HNSW + BM25 + RRF). Dual-response |
| `read` | read_memory | Read specific memory with graph neighborhood |
| `update` | update_memory, mark_lesson_effective | Update any memory |
| `delete` | delete_memory, clear_episodes, delete_file | Soft delete with changefeed audit |
| `link` | link_episode_to_lesson | Manual link between any memories |
| `stats` | get_memory_stats, get_episode_stats, status | Stats by type, project, tags |
| `reflect` | reflect_on_failure | Structured failure analysis -> store as episode |
| `improved_attempt` | generate_improved_attempt | Query past failures + generate guidance |
| `model_effectiveness` | get_model_effectiveness | Which model works for this task pattern? |
| `create_task` | create_task, create_epic | Create task/epic with file scopes |
| `get_next_task` | get_next_task | Single pending task (anti-scope-creep) |
| `complete_task` | complete_task | Mark done, link resolution episode |
| `list_tasks` | list_tasks, get_backlog_summary | Filter by status/project/priority |
| `index_file` | index_file | Tree-sitter parse -> store as code_chunk memories |

## Architecture

```
codeagent/src/codeagent/mcp/
├── server.py                  # FastMCP server, tool registration
├── db/
│   ├── client.py              # SurrealDB async client (exists)
│   ├── schema.surql           # Unified schema
│   └── migrations/            # Schema versioning
├── embeddings/
│   ├── provider.py            # OpenAI text-embedding-3-small (1536d)
│   └── cache.py               # Local embedding cache
├── tools/
│   ├── __init__.py            # Tool registration
│   ├── memory.py              # store, search, read, update, delete, link, stats
│   ├── tasks.py               # create_task, get_next, complete, list
│   ├── reflect.py             # reflect, improved_attempt, model_effectiveness
│   └── index.py               # index_file (tree-sitter -> memory)
├── models/
│   ├── memory.py              # Memory, MemoryType, SearchResult
│   ├── task.py                # Task, Project, Epic
│   └── common.py              # Shared types
└── services/
    ├── memory_service.py      # Business logic (auto-link, evolve, score)
    ├── task_service.py        # Task lifecycle
    ├── search_service.py      # Hybrid search + dual-response
    └── embedding_service.py   # Embedding generation + caching
```

## Design Decisions

1. **SurrealDB over libSQL**: Native graph, HNSW vectors, changefeeds, events all reduce application code
2. **1536d OpenAI unified**: Consistent quality across all memory types. Cost acceptable for the quality gain
3. **Tasks stay separate**: Lifecycle (pending->in_progress->done), dependencies, and execution strategies don't fit the memory model. Linked via record IDs
4. **Dual-response pattern**: Search returns index (summaries) + details (top N full). 10x token savings (from claude-mem research)
5. **Progressive disclosure**: search -> read -> graph traversal (3 layers of detail)

## Patterns Adopted

| Pattern | Source | Description |
|---------|--------|-------------|
| Dual-response | claude-memory-mcp | Index + details in one call |
| Progressive disclosure | claude-mem | 3 layers of increasing detail |
| Access-based scoring | claude-memory-mcp | `access_count` boosts relevance |
| Soft delete + changefeed | SurrealDB native | Built-in audit trail via `CHANGEFEED` |
| Auto-linking via events | SurrealDB native | `DEFINE EVENT` creates graph edges |
| Snowball stemming | SurrealDB analyzers | Better full-text search quality |
| Hybrid search fusion | SurrealDB `search::rrf()` | Vector + keyword in one query |

## Open Questions

- Should `decision` type memories be auto-created from `/plan` output?
- How to handle embedding cache invalidation on content update?
- Should `pattern` memories have a decay mechanism (reduce confidence over time)?
- Multi-project memory isolation vs cross-project knowledge sharing?
