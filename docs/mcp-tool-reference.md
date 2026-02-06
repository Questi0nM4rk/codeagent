# MCP Tool Reference

Unified CodeAgent MCP server tool specifications. For agents implementing or consuming tools.

## Overview

15 tools organized into 4 domains. Single MCP server (`codeagent-mcp`).

| Domain | Tools | Description |
|--------|-------|-------------|
| Memory | 7 | CRUD + search + link + stats for typed memories |
| Tasks | 4 | Task lifecycle management |
| Reflection | 3 | Failure analysis and model selection |
| Indexing | 1 | Code file indexing via tree-sitter |

## Memory Tools

### `store`

Store a memory of any type. Auto-generates embedding, auto-links to similar memories via SurrealDB event.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | `knowledge`, `episode`, `decision`, `pattern`, `code_chunk` |
| `content` | string | yes | The memory content |
| `title` | string | no | Short title for index display |
| `metadata` | object | no | Type-specific structured data (see schema) |
| `tags` | string[] | no | Filtering tags (e.g., `["project:jacore", "auth"]`) |
| `project` | string | no | Project scope |
| `confidence` | float | no | Initial confidence (0.0-1.0, default 1.0) |
| `source_task` | string | no | Task record ID that created this memory |

**Returns**: Created memory with ID and auto-generated links.

**Side effects**: SurrealDB `auto_link` event finds top 5 similar memories and creates `relates_to` edges.

### `search`

Hybrid search across all memory types. Returns dual-response (index + details).

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | yes | Search query (used for both vector and keyword) |
| `type` | string | no | Filter by memory type |
| `project` | string | no | Filter by project |
| `tags` | string[] | no | Filter by tags (AND logic) |
| `max_results` | int | no | Max results (default 10) |
| `max_tokens` | int | no | Token budget for details (default 2000) |
| `include_graph` | bool | no | Include 1-hop related memories (default false) |

**Returns**:
```json
{
    "index": [
        {"id": "memory:abc", "title": "...", "type": "knowledge", "score": 0.92, "snippet": "..."}
    ],
    "details": [
        {"id": "memory:abc", "content": "full content...", "metadata": {...}, "related": [...]}
    ],
    "total_count": 42
}
```

**Search strategy**: Reciprocal Rank Fusion of HNSW cosine similarity + BM25 full-text with snowball stemming.

### `read`

Read a specific memory by ID with its graph neighborhood.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Memory record ID |
| `depth` | int | no | Graph traversal depth (default 1, max 3) |

**Returns**: Full memory with `related_memories` from graph traversal.

**Side effect**: Increments `access_count`, updates `last_accessed`.

### `update`

Update memory content or metadata. Re-embeds if content changes.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Memory record ID |
| `content` | string | no | New content (triggers re-embedding) |
| `title` | string | no | New title |
| `metadata` | object | no | Merge into existing metadata |
| `tags` | string[] | no | Replace tags |
| `confidence` | float | no | New confidence score |

**Returns**: Updated memory.

### `delete`

Soft delete a memory. Preserved in changefeed for audit.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Memory record ID |

**Returns**: Confirmation. Memory remains in 90-day changefeed.

### `link`

Manually create a graph edge between two memories.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `from_id` | string | yes | Source memory ID |
| `to_id` | string | yes | Target memory ID |
| `reason` | string | no | Why these are linked |
| `strength` | float | no | Link strength (0.0-1.0, default 0.8) |

**Returns**: Created edge.

### `stats`

Memory statistics by type, project, and tags.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | no | Filter by project |
| `type` | string | no | Filter by memory type |

**Returns**:
```json
{
    "total": 142,
    "by_type": {"knowledge": 80, "episode": 45, "code_chunk": 12, "pattern": 5},
    "by_project": {"jacore": 50, "codeagent": 92},
    "avg_confidence": 0.87,
    "total_links": 234
}
```

## Task Tools

### `create_task`

Create a task or epic.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | yes | Project prefix (e.g., "CA") |
| `name` | string | yes | Task name |
| `type` | string | no | `task` or `epic` (default `task`) |
| `description` | string | no | Detailed description |
| `priority` | int | no | 1 (highest) to 5 (lowest), default 3 |
| `files_exclusive` | string[] | no | Files only this task modifies |
| `files_readonly` | string[] | no | Files this task reads |
| `depends_on` | string[] | no | Task IDs this depends on |
| `parent` | string | no | Parent epic task ID |
| `suggested_model` | string | no | `haiku`, `sonnet`, or `opus` |

**Returns**: Created task with generated task_id (e.g., "CA-TASK-001").

### `get_next_task`

Get a single pending task. Anti-scope-creep: returns ONE task only.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | no | Filter by project |

**Returns**: Highest priority pending task with no unresolved dependencies.

### `complete_task`

Mark a task as done.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | string | yes | Task ID (e.g., "CA-TASK-001") |
| `resolved_by` | string | no | Memory ID of the episode that resolved this |
| `summary` | string | no | Completion summary |

**Returns**: Updated task.

### `list_tasks`

List and filter tasks.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `project` | string | no | Filter by project |
| `status` | string | no | Filter by status |
| `type` | string | no | `task` or `epic` |

**Returns**: Array of tasks matching filters.

## Reflection Tools

### `reflect`

Structured failure analysis. Creates an `episode` type memory.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `output` | string | yes | Code/output that failed |
| `feedback` | string | yes | Error message or feedback |
| `feedback_type` | string | no | `test_failure`, `lint_error`, `build_error`, etc. |
| `task` | string | no | Task description |
| `approach` | string | no | What was tried |
| `model_used` | string | no | `haiku`, `sonnet`, or `opus` |
| `code_context` | string | no | Relevant code snippet |
| `file_path` | string | no | File being modified |

**Returns**: Structured reflection with `what_went_wrong`, `root_cause`, `what_to_try_next`, `general_lesson`. Stored as episode memory.

### `improved_attempt`

Query past failures and generate guidance for a new attempt.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `task` | string | yes | Current task description |
| `original_output` | string | yes | Code that failed |
| `error_pattern` | string | no | Error message to match |

**Returns**: Guidance based on similar past episodes. Includes what worked, what didn't, and recommended approach.

### `model_effectiveness`

Recommend which model to use based on historical success rates.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `task_pattern` | string | yes | Keywords from task description |
| `feedback_type` | string | no | Filter by feedback type |

**Returns**: Recommended model with confidence and reasoning.

## Indexing Tools

### `index_file`

Parse a source file with tree-sitter and store chunks as `code_chunk` memories.

**Parameters**:

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `file_path` | string | yes | Path to source file |
| `project` | string | no | Project scope |

**Returns**: Number of chunks created/updated. Uses file hash for incremental indexing (skips unchanged files).

**Supported languages**: Python, JavaScript, TypeScript, C, C++, Rust, Go, C#, Lua, Bash

## Error Convention

All tools return errors in a consistent format:

```json
{
    "error": "Description of what went wrong",
    "code": "NOT_FOUND"
}
```

Error codes: `NOT_FOUND`, `VALIDATION_ERROR`, `DB_ERROR`, `EMBEDDING_ERROR`
