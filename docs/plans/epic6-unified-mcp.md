# Epic 6: Unified MCP Server

## Status: Planning

## Goal

Replace 4 separate MCP servers (amem, reflection, codebase, backlog) with a single unified `codeagent-mcp` server backed by SurrealDB. Reduce 36 tools to ~15 through a unified memory model with types.

## Design Documents

- `docs/ideas/unified-memory-system.md` - Brainstorming output and design rationale
- `docs/ideas/surrealdb-advanced-features.md` - SurrealDB capabilities research
- `docs/ideas/enterprise-memory-patterns.md` - Patterns from enterprise systems
- `docs/surrealdb-schema-reference.md` - Complete schema specification
- `docs/mcp-tool-reference.md` - Tool API specification
- `docs/current-mcp-architecture.md` - What we're replacing

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Database | SurrealDB (HNSW, not MTREE) | Native graph, vectors, changefeeds, events |
| Embeddings | 1536d OpenAI `text-embedding-3-small` | Unified quality across all types |
| Memory model | Unified table with type discriminator | knowledge, episode, decision, pattern, code_chunk |
| Tasks | Separate table, linked via record IDs | Lifecycle doesn't fit memory model |
| Search | Hybrid HNSW + BM25 with `search::rrf()` | SurrealDB native fusion |
| Graph | Native `RELATE` with auto-link event | Replaces manual zettelkasten code |
| Audit | `CHANGEFEED 90d` + versioned storage | Replaces manual provenance |
| Tool count | ~15 (down from 36) | Type system does what separate MCPs did |

## Implementation Order

### Phase 1: Infrastructure

- [ ] SurrealDB Docker Compose (replace Qdrant)
- [ ] Schema file (`schema.surql`) with all tables, indexes, events
- [ ] Update `SurrealDBClient` in `codeagent/src/codeagent/mcp/db/client.py`
- [ ] Schema initialization on first connect

### Phase 2: Embedding Service

- [ ] OpenAI `text-embedding-3-small` provider
- [ ] Local embedding cache (avoid re-embedding identical content)
- [ ] Pydantic models for Memory, SearchResult, Task

### Phase 3: Core Memory Tools

- [ ] `store` - Create memory of any type, auto-embed
- [ ] `search` - Hybrid search with dual-response pattern
- [ ] `read` - Read with graph neighborhood
- [ ] `update` - Update with re-embedding
- [ ] `delete` - Soft delete
- [ ] `link` - Manual graph edges
- [ ] `stats` - Memory statistics

### Phase 4: Task Tools

- [ ] `create_task` - With project prefix generation
- [ ] `get_next_task` - Single task, anti-scope-creep
- [ ] `complete_task` - With episode linking
- [ ] `list_tasks` - Filtered listing

### Phase 5: Reflection Tools

- [ ] `reflect` - Structured failure analysis -> episode memory
- [ ] `improved_attempt` - Past failure guidance
- [ ] `model_effectiveness` - Model recommendation

### Phase 6: Code Indexing

- [ ] `index_file` - Tree-sitter parse -> code_chunk memories
- [ ] Port tree-sitter language grammars
- [ ] Incremental indexing (hash-based skip)

### Phase 7: Integration

- [ ] FastMCP server registration (single `server.py`)
- [ ] MCP registry update (`mcps/mcp-registry.json`)
- [ ] Data migration script (libSQL -> SurrealDB, one-time)
- [ ] Update `install.sh` for SurrealDB
- [ ] Update skills to use new tool names

## File Structure

```
codeagent/src/codeagent/mcp/
├── server.py
├── db/
│   ├── client.py
│   ├── schema.surql
│   └── migrations/
├── embeddings/
│   ├── provider.py
│   └── cache.py
├── tools/
│   ├── __init__.py
│   ├── memory.py
│   ├── tasks.py
│   ├── reflect.py
│   └── index.py
├── models/
│   ├── memory.py
│   ├── task.py
│   └── common.py
└── services/
    ├── memory_service.py
    ├── task_service.py
    ├── search_service.py
    └── embedding_service.py
```

## Migration Strategy

Progressive (strangler fig). Old MCPs continue working until unified server is validated. Per-phase testing before moving to next phase.

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SurrealDB Python SDK instability (0.3.x) | Pin version, wrap all calls in our client |
| HNSW index issues at scale | Start with EFC=200, M=16 (conservative). Benchmark early |
| OpenAI embedding costs | Cache aggressively. ~$0.02/1M tokens is low |
| Data migration failures | Keep libSQL as read-only backup during transition |
| Tool name changes break skills | Update skills in Epic 7 (separate PR) |
