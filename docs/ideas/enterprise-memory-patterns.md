# Enterprise Memory System Patterns

Research from open-source Claude memory systems. Patterns to adopt for CodeAgent.

## Systems Analyzed

| System | Architecture | Storage | Search | Complexity |
|--------|-------------|---------|--------|------------|
| **claude-mem** (thedotmack) | Plugin + Worker + Chroma | SQLite + ChromaDB | FTS5 + Vector | High |
| **claude-memory-mcp** (WhenMoon-afk) | Pure MCP | SQLite | FTS5 only | Medium |
| **mcp-knowledge-graph** (shaneholloman) | MCP + JSONL | JSONL files | String match | Low |

## Patterns to Adopt

### 1. Dual-Response Pattern (from claude-memory-mcp)

Single search call returns two levels of detail:

```python
{
    "index": [                    # All matches as summaries (~50 tokens each)
        {"id": "mem_001", "title": "...", "type": "knowledge", "score": 0.92},
        {"id": "mem_002", "title": "...", "type": "episode", "score": 0.87},
    ],
    "details": [                  # Top N with full content (fits token budget)
        {"id": "mem_001", "content": "full content...", "metadata": {...}},
    ],
    "total_count": 42,
    "tokens_used": 850,
}
```

**Why**: No roundtrips. Automatic token management. Agent sees summaries first, can request more if needed.

### 2. Progressive Disclosure (from claude-mem)

Three layers of increasing detail:

1. **Search** -> Index of summaries (~50-100 tokens per result)
2. **Read** -> Full content of specific memory (~500-1000 tokens)
3. **Graph** -> Neighborhood of related memories (expand from a node)

**Why**: 10x token reduction vs returning everything. Agent controls what to expand.

### 3. Token Budgeting (from both SQLite systems)

Search accepts `max_tokens` parameter:

```python
search(query="auth patterns", max_tokens=2000)
# Returns: index (all matches) + details (as many as fit in 2000 tokens)
```

**Why**: Prevents context window overflow. Agent specifies budget based on task complexity.

### 4. Access-Based Scoring (from claude-memory-mcp)

Track how often memories are accessed:

```python
score = (
    recency_weight * recency_score +
    importance_weight * importance +
    frequency_weight * (access_count / max_access) +
    keyword_weight * fts_rank
)
```

Frequently accessed memories rank higher. Implicit importance signal.

### 5. Soft Deletes + Provenance (from claude-memory-mcp)

Never hard-delete. Mark as deleted + record why:

```sql
-- Soft delete
UPDATE memory SET is_deleted = true, deleted_reason = "outdated"

-- Audit trail (we use CHANGEFEED instead)
SHOW CHANGES FOR TABLE memory SINCE d'2025-01-01'
```

**Why**: Memory recovery. Audit compliance. Debug why knowledge changed.

### 6. Hierarchical Memory Structure (from claude-mem)

Structured data over blob text:

```python
{
    "title": "Repository pattern in JaCore",        # Quick scan
    "subtitle": "Data access layer architecture",    # Context
    "content": "Full detailed explanation...",        # Deep read
    "facts": ["Uses UoW pattern", "EF Core backed"], # Discrete items
    "concepts": ["repository", "unit-of-work"],      # Key ideas
    "files_touched": ["src/JaCore.Data/Repos/..."]   # Code links
}
```

**Why**: Different consumption levels. Agent can scan titles without reading full content.

### 7. Hook-Driven Capture (from claude-mem)

Automatically capture Claude's actions via lifecycle hooks:

- `PostToolUse`: Log what tools were called
- `SessionEnd`: Generate session summary
- No manual memory calls needed for basic observation

**Why**: Passive learning. Build knowledge base without explicit "store" calls.

## Patterns We Chose Not to Adopt

| Pattern | System | Why Not |
|---------|--------|---------|
| Separate Chroma service | claude-mem | Deployment complexity. SurrealDB has native HNSW |
| JSONL storage | mcp-knowledge-graph | Not scalable. No query optimization |
| No embeddings | claude-memory-mcp v3 | We need semantic search quality. OpenAI 1536d is worth the cost |
| Session-centric grouping | claude-mem | We group by memory type + project instead |
| TTL/expiration | claude-memory-mcp | Not needed for knowledge systems. Knowledge doesn't expire |

## Tool Surface Comparison

| System | Tool Count | Approach |
|--------|-----------|----------|
| claude-mem | 4 | Minimal: search, timeline, get_observations, docs |
| claude-memory-mcp | 3 | Minimal: store, recall, forget |
| mcp-knowledge-graph | 10 | CRUD for entities, relations, observations |
| **CodeAgent (planned)** | **~15** | Typed memory CRUD + tasks + reflection |

claude-mem's 4-tool approach is elegant but too few for our needs (we have tasks + reflection). claude-memory-mcp's 3 tools are good for pure memory but miss our graph and task features. Our 15 tools is the right balance for a unified system.
