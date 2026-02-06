# Current MCP Architecture (Pre-Unification)

Reference for agents understanding the existing system before Epic 6 migration.

## Status

This document describes the **current state** (4 separate MCPs on libSQL). This is being replaced by the unified system described in `surrealdb-schema-reference.md` and `mcp-tool-reference.md`.

## Overview

4 independent MCP servers sharing one libSQL database at `~/.codeagent/codeagent.db`.

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   amem-mcp   │ │reflection-mcp│ │ codebase-mcp │ │ backlog-mcp  │
│  (semantic)  │ │  (episodic)  │ │  (indexing)  │ │   (tasks)    │
│  9 tools     │ │  12 tools    │ │   5 tools    │ │  10 tools    │
│  384d embed  │ │  384d embed  │ │ 1536d embed  │ │  no embed    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                                │
                   ~/.codeagent/codeagent.db (libSQL)
```

## Server Details

### amem-mcp (Semantic Memory)

- **Repo**: `Questi0nM4rk/amem-mcp`
- **Code**: ~1,354 lines (`server.py`)
- **Module**: `amem_mcp.server`
- **Embedding**: `all-MiniLM-L6-v2` (384d, local, free)
- **Dependencies**: mcp, libsql-experimental, sentence-transformers (optional), spacy (optional)

**Tools**: store_memory, search_memory, read_memory, list_memories, update_memory, delete_memory, adjust_confidence, get_memory_stats, clear_all_memories

**Schema**:
```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY, memory_id TEXT UNIQUE,
    content TEXT, keywords TEXT, context TEXT, tags TEXT, links TEXT,
    project TEXT, confidence REAL, source_task_id TEXT,
    embedding BLOB, created_at TEXT, updated_at TEXT
)
CREATE TABLE memory_counter (id INTEGER PRIMARY KEY, counter INTEGER)
```

**Key features**: Zettelkasten auto-linking, keyword extraction (spaCy or simple), memory evolution (updating context on new links).

### reflection-mcp (Episodic Memory)

- **Repo**: `Questi0nM4rk/reflection-mcp`
- **Code**: ~1,431 lines (`server.py`)
- **Module**: `reflection_mcp.server`
- **Embedding**: `all-MiniLM-L6-v2` (384d, local, free)
- **Dependencies**: mcp, libsql-experimental, sentence-transformers (optional)

**Tools**: reflect_on_failure, store_episode, retrieve_episodes, generate_improved_attempt, mark_lesson_effective, get_model_effectiveness, get_reflection_history, get_common_lessons, get_episode_stats, export_lessons, link_episode_to_lesson, clear_episodes

**Schema**:
```sql
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY, episode_id TEXT UNIQUE,
    task TEXT, approach TEXT, outcome TEXT, feedback TEXT, feedback_type TEXT,
    reflection TEXT, code_context TEXT, file_path TEXT,
    attempt_number INTEGER, model_used TEXT, backlog_task_id TEXT,
    lesson_applied_from TEXT, led_to_success INTEGER, effectiveness_score REAL,
    embedding BLOB, created_at TEXT
)
CREATE TABLE lesson_effectiveness (episode_id TEXT, led_to_success INTEGER, effectiveness_score REAL)
CREATE TABLE episode_links (episode_id TEXT, lesson_episode_id TEXT)
CREATE TABLE task_attempts (task_key TEXT, attempt_count INTEGER)
```

**Key features**: Reflexion pattern (NeurIPS 2023), attempt tracking, lesson effectiveness scoring, model selection recommendations.

### codebase-mcp (Code Indexing)

- **Repo**: `Questi0nM4rk/codebase-mcp`
- **Code**: ~912 lines (`server.py`)
- **Module**: `codebase_rag.server`
- **Embedding**: OpenAI `text-embedding-3-small` (1536d, API, paid)
- **Dependencies**: mcp, libsql-experimental, tree-sitter, openai, pydantic

**Tools**: search, index_file, delete_file, clear_project, status

**Schema**:
```sql
CREATE TABLE code_chunks (
    id INTEGER PRIMARY KEY, chunk_id TEXT UNIQUE,
    file_path TEXT, chunk_index INTEGER, language TEXT,
    chunk_type TEXT, name TEXT, content TEXT,
    start_line INTEGER, end_line INTEGER, file_hash TEXT,
    project TEXT, dependencies TEXT, parent_name TEXT,
    embedding BLOB, created_at TEXT, updated_at TEXT
)
```

**Key features**: Tree-sitter parsing (9 languages), incremental indexing (hash-based), hybrid search (vector + keyword).

### backlog-mcp (Task Management)

- **Repo**: `Questi0nM4rk/backlog-mcp`
- **Code**: ~979 lines (`server.py`)
- **Module**: `backlog_mcp.server`
- **Embedding**: None
- **Dependencies**: mcp, libsql-experimental

**Tools**: create_project, list_projects, create_task, list_tasks, get_next_task, complete_task, update_task, delete_task, get_backlog_summary, create_epic

**Schema**:
```sql
CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT, prefix TEXT UNIQUE, description TEXT, created_at TEXT)
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY, project_id INTEGER, task_id TEXT UNIQUE,
    type TEXT, name TEXT, status TEXT, priority INTEGER,
    description TEXT, action TEXT,
    files_exclusive TEXT, files_readonly TEXT, files_forbidden TEXT,
    verify TEXT, done_criteria TEXT, depends_on TEXT, parent_id INTEGER,
    execution_strategy TEXT, checkpoint_type TEXT, suggested_model TEXT,
    resolved_by_episode TEXT, blocker_reason TEXT, blocker_needs TEXT,
    summary TEXT, commits TEXT
)
```

**Key features**: Task ID generation with project prefixes, single-task loading (anti-scope-creep), epic/subtask hierarchy, file scope tracking.

## Cross-MCP Data Flow

```
Task → Memory:     memories.source_task_id → tasks.task_id
Task → Episode:    episodes.backlog_task_id → tasks.task_id
Task ← Episode:    tasks.resolved_by_episode → episodes.episode_id
Episode → Model:   get_model_effectiveness() reads episodes.model_used + outcome
Memory → Memory:   memories.links (JSON array of memory_ids, bidirectional)
Code → Project:    code_chunks.project → projects.prefix
```

## Skills → MCP Mapping

| Skill | MCPs Used |
|-------|-----------|
| researcher | amem, codebase |
| architect | amem |
| orchestrator | backlog |
| implementer | backlog, reflection |
| reviewer | reflection |
| learner | amem, reflection |

## Known Issues

1. **Embedding mismatch**: 384d (amem/reflection) vs 1536d (codebase). Cannot cross-search
2. **36 tools**: Excessive context window cost. Many tools are thin CRUD wrappers
3. **No cross-domain search**: Cannot search memories + episodes in one query
4. **Manual linking only**: No auto-linking between episodes and knowledge
5. **Duplicate patterns**: Each MCP reimplements connection, embedding, search logic
6. **libSQL limitations**: No native graph traversal, no built-in hybrid search fusion
