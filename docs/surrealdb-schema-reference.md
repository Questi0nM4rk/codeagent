# SurrealDB Schema Reference

Complete schema for the unified CodeAgent memory system. This is the authoritative reference for all agents working on the MCP server.

## Storage Backend

- **Engine**: SurrealDB with SurrealKV versioned storage
- **Start command**: `surreal start surrealkv+versioned://~/.codeagent/data/surrealdb`
- **Namespace**: `codeagent`
- **Database**: `memory`
- **Python SDK**: `surrealdb>=0.3.0` (AsyncSurreal)

## Analyzer

```surql
DEFINE ANALYZER memory_analyzer
    TOKENIZERS blank, class, camel, punct
    FILTERS snowball(english), lowercase;
```

- `blank`: Split on whitespace
- `class`: Split on unicode class changes (letter->digit->punct)
- `camel`: Split CamelCase words
- `punct`: Split on punctuation
- `snowball(english)`: Stemming (running->run, patterns->pattern)
- `lowercase`: Case-insensitive search

## Memory Table

Core table. All memory types live here with a type discriminator.

```surql
DEFINE TABLE memory SCHEMAFULL CHANGEFEED 90d;

-- Core fields
DEFINE FIELD type ON memory TYPE string
    ASSERT $value IN ["knowledge", "episode", "decision", "pattern", "code_chunk"];
DEFINE FIELD content ON memory TYPE string;
DEFINE FIELD title ON memory TYPE option<string>;
DEFINE FIELD metadata ON memory FLEXIBLE TYPE object;
DEFINE FIELD embedding ON memory TYPE array<float>;
DEFINE FIELD tags ON memory TYPE array<string>;
DEFINE FIELD project ON memory TYPE option<string>;
DEFINE FIELD confidence ON memory TYPE float DEFAULT 1.0;
DEFINE FIELD access_count ON memory TYPE int DEFAULT 0;
DEFINE FIELD last_accessed ON memory TYPE option<datetime>;
DEFINE FIELD source_task ON memory TYPE option<record<task>>;
DEFINE FIELD created_at ON memory TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON memory TYPE datetime DEFAULT time::now();

-- Indexes
DEFINE INDEX memory_vec ON memory FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE TYPE F32 EFC 200 M 16;
DEFINE INDEX memory_fts ON memory FIELDS content
    SEARCH ANALYZER memory_analyzer BM25 HIGHLIGHTS;
DEFINE INDEX memory_type ON memory FIELDS type;
DEFINE INDEX memory_project ON memory FIELDS project;
DEFINE INDEX memory_tags ON memory FIELDS tags;
```

### Type-Specific Metadata

The `metadata` field is `FLEXIBLE` - each type stores different structured data.

**knowledge**:
```json
{
    "keywords": ["repository", "pattern"],
    "context": "Used in data access layer",
    "source": "manual"
}
```

**episode**:
```json
{
    "task": "Implement auth middleware",
    "approach": "JWT with refresh tokens",
    "outcome": "success",
    "feedback": "All tests passing",
    "feedback_type": "test_result",
    "reflection": {
        "what_went_wrong": null,
        "root_cause": null,
        "what_to_try_next": null,
        "general_lesson": "JWT refresh pattern works well with middleware"
    },
    "model_used": "opus",
    "attempt_number": 1
}
```

**decision**:
```json
{
    "options_considered": ["JWT", "Session cookies", "OAuth2"],
    "chosen": "JWT",
    "rationale": "Stateless, works with microservices",
    "status": "accepted"
}
```

**pattern**:
```json
{
    "language": "python",
    "category": "testing",
    "frequency": 5,
    "last_applied": "2025-02-01T00:00:00Z"
}
```

**code_chunk**:
```json
{
    "file_path": "src/auth/middleware.py",
    "language": "python",
    "chunk_type": "function",
    "name": "verify_token",
    "start_line": 42,
    "end_line": 67,
    "file_hash": "abc123",
    "dependencies": ["jwt", "datetime"],
    "parent_name": "AuthMiddleware"
}
```

## Graph Relations

```surql
DEFINE TABLE relates_to SCHEMAFULL TYPE RELATION IN memory OUT memory;
DEFINE FIELD strength ON relates_to TYPE float
    ASSERT $value >= 0.0 AND $value <= 1.0;
DEFINE FIELD reason ON relates_to TYPE string;
DEFINE FIELD auto ON relates_to TYPE bool DEFAULT false;
DEFINE FIELD created_at ON relates_to TYPE datetime DEFAULT time::now();
```

### Auto-Linking Event

Automatically creates graph edges when a memory is stored:

```surql
DEFINE EVENT auto_link ON TABLE memory WHEN $event = "CREATE" THEN (
    LET $similar = (
        SELECT id, vector::similarity::cosine(embedding, $after.embedding) AS score
        FROM memory WHERE id != $after.id
        AND embedding <|5, COSINE|> $after.embedding
    );
    FOR $mem IN $similar {
        RELATE $after.id->relates_to->$mem.id SET
            strength = $mem.score,
            reason = "semantic_similarity",
            auto = true;
    };
);
```

### Traversal Examples

```surql
-- Direct neighbors
SELECT *, ->relates_to->memory AS related FROM memory:abc;

-- Bidirectional
SELECT *, <->relates_to<->memory AS all_connected FROM memory:abc;

-- Multi-hop (up to 3)
SELECT *, {..3}->relates_to->memory AS neighborhood FROM memory:abc;

-- Shortest path between two memories
SELECT *, {..+shortest=memory:target}->relates_to->memory AS path FROM memory:abc;
```

## Task Tables

```surql
DEFINE TABLE project SCHEMAFULL;
DEFINE FIELD name ON project TYPE string;
DEFINE FIELD prefix ON project TYPE string;
DEFINE FIELD description ON project TYPE option<string>;
DEFINE FIELD created_at ON project TYPE datetime DEFAULT time::now();
DEFINE INDEX project_prefix ON project FIELDS prefix UNIQUE;

DEFINE TABLE task SCHEMAFULL CHANGEFEED 90d;
DEFINE FIELD project ON task TYPE record<project>;
DEFINE FIELD task_id ON task TYPE string;
DEFINE FIELD type ON task TYPE string ASSERT $value IN ["task", "epic"];
DEFINE FIELD name ON task TYPE string;
DEFINE FIELD status ON task TYPE string
    ASSERT $value IN ["pending", "in_progress", "blocked", "done"];
DEFINE FIELD priority ON task TYPE int DEFAULT 3;
DEFINE FIELD description ON task TYPE option<string>;
DEFINE FIELD action ON task TYPE option<string>;
DEFINE FIELD files_exclusive ON task TYPE option<array<string>>;
DEFINE FIELD files_readonly ON task TYPE option<array<string>>;
DEFINE FIELD depends_on ON task TYPE option<array<record<task>>>;
DEFINE FIELD parent ON task TYPE option<record<task>>;
DEFINE FIELD execution_strategy ON task TYPE option<string>;
DEFINE FIELD suggested_model ON task TYPE option<string>;
DEFINE FIELD resolved_by ON task TYPE option<record<memory>>;
DEFINE FIELD created_at ON task TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON task TYPE datetime DEFAULT time::now();
DEFINE INDEX task_id_idx ON task FIELDS task_id UNIQUE;
DEFINE INDEX task_status ON task FIELDS status;
DEFINE INDEX task_project ON task FIELDS project;
```

## Views

Pre-computed virtual tables for hot query paths.

```surql
DEFINE TABLE recent_failures AS
    SELECT * FROM memory
    WHERE type = "episode" AND metadata.outcome = "failure"
    ORDER BY created_at DESC LIMIT 50;

DEFINE TABLE active_knowledge AS
    SELECT * FROM memory
    WHERE type = "knowledge" AND confidence > 0.5
    ORDER BY access_count DESC LIMIT 100;

DEFINE TABLE pending_tasks AS
    SELECT * FROM task
    WHERE status = "pending"
    ORDER BY priority ASC, created_at ASC;
```

## Key Queries

### Hybrid Search (Vector + Full-Text with RRF)

```surql
LET $vec = <array<float>> $embedding;
LET $q = <string> $query;

LET $semantic = (
    SELECT id, content, type, title, tags, project, confidence,
        vector::similarity::cosine(embedding, $vec) AS vs
    FROM memory
    WHERE embedding <|20, COSINE|> $vec
);

LET $keyword = (
    SELECT id, content, type, title, tags, project, confidence,
        search::score(1) AS ts
    FROM memory
    WHERE content @1@ $q
);

RETURN search::rrf([$semantic, $keyword], 10, 60);
```

### Filtered Search (by type and project)

```surql
SELECT id, content, title, metadata,
    vector::similarity::cosine(embedding, $vec) AS score
FROM memory
WHERE type = $type
AND ($project IS NONE OR project = $project)
AND embedding <|10, COSINE|> $vec
ORDER BY score DESC;
```

### Model Effectiveness

```surql
SELECT
    metadata.model_used AS model,
    count() AS total,
    count(metadata.outcome = "success") AS successes,
    math::mean(confidence) AS avg_confidence
FROM memory
WHERE type = "episode"
AND content ~ $task_pattern
GROUP BY metadata.model_used;
```

### Version History

```surql
-- Current state
SELECT * FROM memory:abc;

-- State at a specific time
SELECT * FROM memory:abc VERSION d'2025-01-15T00:00:00Z';

-- All changes in last 7 days
SHOW CHANGES FOR TABLE memory SINCE time::now() - 7d;
```

## Embedding Configuration

- **Model**: OpenAI `text-embedding-3-small`
- **Dimensions**: 1536
- **Index**: HNSW with COSINE distance
- **Caching**: Local cache to avoid re-embedding identical content
- **Cost**: ~$0.02 per 1M tokens

## Connection

```python
import os
from surrealdb import AsyncSurreal

async with AsyncSurreal("ws://localhost:8000/rpc") as db:
    await db.signin({
        "username": os.getenv("SURREAL_USER", "root"),
        "password": os.getenv("SURREAL_PASS", "codeagent"),
    })
    await db.use("codeagent", "memory")
    # Ready to query
```

## Docker Compose

```yaml
services:
  surrealdb:
    image: surrealdb/surrealdb:v2.2
    container_name: codeagent-surrealdb
    command: start --user root --pass root surrealkv+versioned:///data/codeagent.db
    ports:
      - "8000:8000"
    volumes:
      - surrealdb_data:/data
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'

volumes:
  surrealdb_data:
```
