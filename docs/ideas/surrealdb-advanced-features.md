# SurrealDB Advanced Features for CodeAgent

Research findings from Epic 6 design session. Features beyond basic tables that impact our architecture.

## Game-Changers (Using in v1)

### 1. Hybrid Search Fusion

Built-in functions that fuse HNSW vector results with BM25 full-text results.

```surql
LET $semantic = (
    SELECT id, content, type,
        vector::similarity::cosine(embedding, $vec) AS vs
    FROM memory WHERE embedding <|20, COSINE|> $vec
);

LET $keyword = (
    SELECT id, content, type,
        search::score(1) AS ts
    FROM memory WHERE content @1@ $query
);

-- Reciprocal Rank Fusion
RETURN search::rrf([$semantic, $keyword], 10, 60);

-- Or Linear Fusion with weights
RETURN search::linear([$semantic, $keyword], [0.7, 0.3], 10, 'minmax');
```

Replaces hundreds of lines of manual hybrid search code.

### 2. HNSW Vector Index (replaces deprecated MTREE)

MTREE was removed due to scalability issues (failed at >30k vectors). HNSW is the replacement.

```surql
DEFINE INDEX memory_vec ON memory FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE TYPE F32 EFC 200 M 16;
```

Parameters:
- `EFC` (200): Construction accuracy/speed tradeoff. Default 150
- `M` (16): Max connections per node. Default 12
- `M0` (32): Max connections in lowest layer. Default 24
- Cache: 256 MiB LRU (configurable via `SURREAL_HNSW_CACHE_SIZE`)

Distance functions: COSINE, EUCLIDEAN, MANHATTAN, MINKOWSKI
Types: F64, F32, I64, I32, I16

### 3. Custom Analyzers (Snowball Stemming)

```surql
DEFINE ANALYZER memory_analyzer
    TOKENIZERS blank, class, camel, punct
    FILTERS snowball(english), lowercase;

DEFINE INDEX memory_fts ON memory FIELDS content
    SEARCH ANALYZER memory_analyzer BM25 HIGHLIGHTS;
```

Tokenizers: `blank`, `punct`, `camel`, `class` (unicode class changes)
Filters: `lowercase`, `uppercase`, `ascii`, `ngram(min,max)`, `edgengram(min,max)`, `snowball(lang)` (17 languages)

### 4. Changefeeds (Built-in Audit Trail)

```surql
DEFINE TABLE memory SCHEMAFULL CHANGEFEED 90d;

-- Replay all changes since a timestamp
SHOW CHANGES FOR TABLE memory SINCE d'2025-02-01' INCLUDE ORIGINAL;
```

90-day changelog. Replaces manual provenance tables. `INCLUDE ORIGINAL` gives before-state.

### 5. Events (Database Triggers)

```surql
DEFINE EVENT auto_link ON TABLE memory WHEN $event = "CREATE" THEN (
    LET $similar = (
        SELECT id, vector::similarity::cosine(embedding, $after.embedding) AS score
        FROM memory WHERE id != $after.id
        AND embedding <|5, COSINE|> $after.embedding
    );
    FOR $mem IN $similar {
        RELATE $after.id->relates_to->$mem.id SET
            strength = $mem.score, reason = "semantic_similarity", auto = true;
    };
);
```

Variables: `$event` (CREATE/UPDATE/DELETE), `$before`, `$after`, `$value`
Can call `http::post()` for webhooks.

### 6. Graph Relations with Recursive Traversal

```surql
-- Define typed relations
DEFINE TABLE relates_to SCHEMAFULL TYPE RELATION IN memory OUT memory;

-- Create edges
RELATE memory:abc->relates_to->memory:xyz SET strength = 0.85;

-- Traverse
SELECT *, ->relates_to->memory AS related FROM memory:abc;
SELECT *, <->relates_to<->memory AS all_connected FROM memory:abc;

-- Recursive (multi-hop)
SELECT *, {..3}->relates_to->memory AS three_hops FROM memory:abc;
SELECT *, {..+shortest=memory:target}->relates_to->memory AS path FROM memory:abc;
```

Operators: `->` (out), `<-` (in), `<->` (both), `->?` (all outgoing)
Pathfinding: `+paths`, `+unique`, `+shortest=<target>`

### 7. Views (Virtual Tables)

```surql
DEFINE TABLE recent_failures AS
    SELECT * FROM memory
    WHERE type = "episode" AND metadata.outcome = "failure"
    ORDER BY created_at DESC LIMIT 50;

DEFINE TABLE active_knowledge AS
    SELECT * FROM memory
    WHERE type = "knowledge" AND confidence > 0.5
    ORDER BY access_count DESC LIMIT 100;
```

Pre-computed for hot paths. Always fresh.

### 8. SurrealKV Versioned Storage

```surql
-- Start with versioning enabled
-- surreal start surrealkv+versioned://mydb

-- Query historical state
SELECT * FROM memory:abc VERSION d'2025-01-15T00:00:00Z';
```

Built-in immutable history. No separate version table needed.

## Future Potential (v2+)

### SurrealML (In-Database ML)

```surql
-- Import ONNX model
-- POST /ml/import with .surml file

-- Run inference in queries
SELECT ml::embedding_model<1>({ text: content }) AS embedding FROM memory;
```

Could embed the embedding model directly in SurrealDB. Eliminates OpenAI API dependency for embeddings. Requires ONNX export of the model.

### Live Queries (Real-Time Subscriptions)

```surql
LIVE SELECT * FROM memory WHERE type = "episode" AND metadata.outcome = "failure";
```

Real-time streaming of new failures. Could power a monitoring dashboard.

### Record References (Bidirectional)

```surql
DEFINE FIELD memories ON project TYPE option<array<record<memory>>> REFERENCE;
DEFINE FIELD project_ref ON memory COMPUTED <~project;

-- Auto-populated: query from either direction
SELECT *, project_ref FROM memory:abc;
```

`<~table` syntax auto-resolves incoming references.

### Geometry Types

Full GeoJSON support. Could add location context to memories if relevant (e.g., "learned this at office" vs "learned this at home").

### Embedded Storage Backends

- `memory://` for testing (no persistence)
- `surrealkv://` for single-node (our use case)
- `tikv://` for distributed scaling (enterprise future)

## What SurrealDB Lacks

- Custom retention policies / TTL (must implement manually via events or cron)
- Columnar storage (not OLAP-optimized)
- RDF/SPARQL (not a semantic web triple store)
- Dedicated vertex table types (use TYPE constraints instead)

## What This Eliminates From Our Codebase

| Before (manual code) | After (SurrealDB native) |
|----------------------|--------------------------|
| Custom hybrid search (~200 lines) | `search::rrf()` |
| Provenance/audit table + inserts | `CHANGEFEED 90d` |
| Manual stemming/tokenization | `DEFINE ANALYZER ... snowball(english)` |
| Custom auto-linking logic | `DEFINE EVENT auto_link` |
| "Recent failures" query logic | `DEFINE TABLE recent_failures AS ...` |
| Manual `updated_at` tracking | `DEFINE EVENT touch_updated` |
| BM25 highlight extraction | `HIGHLIGHTS` in search index |
| Graph traversal code | Native `->relates_to->` syntax |
| Version history tracking | `VERSION d'...'` queries |
