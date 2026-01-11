# Codebase Indexing Reference

Specification for incremental RAG indexing with Merkle tree change detection, Tree-sitter parsing, and Qdrant hybrid search.

## Architecture Overview

```
Files → Merkle Tree (change detection) → Tree-sitter (parse) → Chunks
                                                                  ↓
                                                              Qdrant
                                                    (BM25 + Vector in one DB)
                                                                  ↓
                                                          Hybrid Search (RRF)
```

## Components

### 1. Merkle Tree (Change Detection)

**Purpose:** Detect which files changed since last indexing, enabling incremental updates.

**Algorithm:**
```
For each file:
  file_hash = SHA256(content)

For each directory:
  dir_hash = SHA256(sorted([child_hashes]))

Root hash = hash of top-level directory
```

**Manifest File:** `.codeagent/index/manifest.json`

```json
{
  "version": "1.0",
  "root_hash": "abc123...",
  "updated": "2026-01-10T16:30:00Z",
  "stats": {
    "files": 156,
    "chunks": 892,
    "languages": ["csharp", "typescript"]
  },
  "tree": {
    "src/": {
      "hash": "def456...",
      "Controllers/": {
        "hash": "ghi789...",
        "AuthController.cs": {
          "hash": "jkl012...",
          "mtime": "2026-01-10T14:20:00Z",
          "chunk_ids": ["chunk_001", "chunk_002"]
        }
      }
    }
  }
}
```

**Change Detection Flow:**
```
1. Read existing manifest.json
2. Walk directory tree, computing new hashes
3. Compare hashes to find changed paths:
   - If directory hash differs: recurse into children
   - If file hash differs: mark for re-indexing
   - If file hash same: skip (already indexed)
4. Re-index only changed files
5. Update manifest with new hashes
```

**Benefits:**
- O(changed files) indexing vs O(all files)
- No need to re-parse unchanged code
- Efficient even for large codebases

### 2. Tree-sitter (Code Parsing)

**Purpose:** Language-aware code parsing for semantic chunking.

**Supported Languages:**

| Language | Grammar | Chunk Types |
|----------|---------|-------------|
| C# | tree-sitter-c-sharp | class, method, property |
| TypeScript | tree-sitter-typescript | class, function, interface |
| Python | tree-sitter-python | class, function, async_function |
| Rust | tree-sitter-rust | struct, impl, fn |
| Go | tree-sitter-go | type, func, method |
| C/C++ | tree-sitter-c, cpp | struct, function |
| Lua | tree-sitter-lua | function, local_function |

**Chunk Strategy:**

```
Priority:
1. Function/Method level (preferred)
2. Class/Type level (if function too small)
3. Block level (for very large functions)

Max chunk size: ~2000 tokens
Min chunk size: ~100 tokens
Overlap: None (semantic boundaries are clean)
```

**Chunk Format:**

```json
{
  "id": "chunk_001",
  "file": "src/Controllers/AuthController.cs",
  "language": "csharp",
  "type": "method",
  "name": "Login",
  "signature": "public async Task<IActionResult> Login(LoginRequest request)",
  "start_line": 45,
  "end_line": 78,
  "start_byte": 1234,
  "end_byte": 2345,
  "content": "public async Task<IActionResult> Login...",
  "dependencies": ["IAuthService", "LoginRequest", "IActionResult"],
  "docstring": "Authenticates user and returns JWT token",
  "parent": "AuthController"
}
```

**Dependency Extraction:**

```
For each chunk, extract:
- Imports/using statements
- Type annotations (parameters, returns)
- Direct references to other types
- Base classes/interfaces
```

### 3. Qdrant (Hybrid Search)

**Purpose:** Combined BM25 keyword and semantic vector search in single database.

**Collection Configuration:**

```python
collection_name = "codebase_chunks"

vectors_config = {
    "content": {
        "size": 1024,  # text-embedding-3-small
        "distance": "Cosine"
    }
}

sparse_vectors_config = {
    "bm25": {
        "index": {
            "on_disk": false  # Fast keyword matching
        }
    }
}
```

**Indexing:**

```python
# For each chunk:
point = {
    "id": chunk_id,
    "vector": {
        "content": embed(chunk.content)  # Dense vector
    },
    "sparse_vector": {
        "bm25": tokenize_bm25(chunk.content)  # Sparse for keywords
    },
    "payload": {
        "file": chunk.file,
        "language": chunk.language,
        "type": chunk.type,
        "name": chunk.name,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "dependencies": chunk.dependencies,
        "project": project_name
    }
}
```

**Hybrid Search:**

```python
def hybrid_search(query: str, k: int = 10, project: str = None):
    # Encode query
    dense_vector = embed(query)
    sparse_vector = tokenize_bm25(query)

    # Build filter
    filter = {"project": project} if project else None

    # Prefetch from both indexes
    results = client.query_points(
        collection_name="codebase_chunks",
        prefetch=[
            Prefetch(
                query=dense_vector,
                using="content",
                limit=k * 2
            ),
            Prefetch(
                query=sparse_vector,
                using="bm25",
                limit=k * 2
            )
        ],
        query=RRFFusion(),  # Reciprocal Rank Fusion
        filter=filter,
        limit=k
    )

    return results
```

**Reciprocal Rank Fusion (RRF):**

```
RRF Score = sum(1 / (k + rank_i)) for each retrieval method

Where:
- k = 60 (constant to reduce impact of high-rank differences)
- rank_i = position in each result list

Benefits:
- Combines semantic and keyword matches
- Exact matches score high (BM25)
- Conceptually similar code also found (vectors)
```

## Index Triggers

| Trigger | Scope | Description |
|---------|-------|-------------|
| `/scan` | Full | Scan entire codebase (incremental via Merkle) |
| `/scan --full` | Full | Force complete re-index |
| File write (hook) | Single | Re-index modified file |
| `/implement` complete | Modified | Re-index files touched during implementation |
| `codeagent index` | Full | CLI trigger for indexing |

## Index Update Flow

### Full Scan (`/scan`)

```
1. Load manifest.json (or create if missing)
2. Walk source tree, compute Merkle hashes
3. Compare against stored hashes
4. For each changed file:
   a. Parse with Tree-sitter
   b. Extract chunks
   c. Delete old chunks from Qdrant
   d. Insert new chunks
5. Update manifest.json
6. Store summary in A-MEM
```

### Incremental Update (file hook)

```
1. Compute file hash
2. If hash unchanged: skip
3. Parse file with Tree-sitter
4. Extract chunks
5. Delete old chunks for this file from Qdrant
6. Insert new chunks
7. Update file entry in manifest.json
8. Update parent directory hashes
```

## Query Integration

### Researcher Agent Query Flow

```python
# 1. Query codebase index
chunks = hybrid_search(
    query="JWT token validation",
    k=10,
    project="MyProject"
)

# 2. Format for context
context = []
for chunk in chunks:
    context.append({
        "file": chunk.file,
        "name": chunk.name,
        "lines": f"{chunk.start_line}-{chunk.end_line}",
        "content": chunk.content[:500],  # Truncate for context
        "relevance": chunk.score
    })

# 3. Include in research output
```

### Result Format

```markdown
### From Codebase Index

| File | Type | Name | Relevance |
|------|------|------|-----------|
| src/Auth/AuthService.cs | method | ValidateToken | 0.92 |
| src/Middleware/AuthMiddleware.cs | method | Invoke | 0.87 |
| src/Models/JwtToken.cs | class | JwtToken | 0.81 |
```

## Storage Locations

| Data | Location | Format |
|------|----------|--------|
| Merkle manifest | `.codeagent/index/manifest.json` | JSON |
| Chunk metadata | `.codeagent/index/chunks/` | JSON (backup) |
| Vectors + payloads | Qdrant (localhost:6333) | Native |

## Performance Considerations

### Memory Usage

```
Merkle manifest: ~1KB per 100 files
Tree-sitter: ~10MB parser + AST (per language)
Qdrant: ~1KB per chunk (vectors + payload)
```

### Time Estimates

```
Initial full index (1000 files):
  - Merkle tree: ~5s
  - Tree-sitter parsing: ~30s
  - Qdrant upload: ~10s
  - Total: ~45s

Incremental update (1 file):
  - Hash check: <1ms
  - Parse + upload: ~100ms
```

## Error Handling

### Parse Failures

```
If Tree-sitter fails to parse a file:
1. Log warning with file path
2. Create single "raw" chunk with full file content
3. Continue with other files
4. Report in scan summary
```

### Qdrant Connection

```
If Qdrant unavailable:
1. Check if codeagent start was run
2. Store chunks to local JSON fallback
3. Sync to Qdrant when available
4. Report degraded mode to user
```

## API Reference

### MCP Tools (codebase-rag server)

```python
# Search indexed codebase
mcp__codebase__search(
    query: str,         # Natural language or code pattern
    k: int = 10,        # Max results
    language: str = None,  # Filter by language
    file_pattern: str = None,  # Glob filter
    type: str = None    # function, class, method, etc.
) -> List[Chunk]

# Get index status
mcp__codebase__status() -> {
    "indexed": bool,
    "files": int,
    "chunks": int,
    "last_updated": str,
    "qdrant_healthy": bool
}

# Force re-index specific file
mcp__codebase__index_file(path: str) -> {
    "chunks_created": int,
    "chunks_deleted": int
}
```

## Configuration

### Project Config (`.codeagent/config.yaml`)

```yaml
indexing:
  enabled: true
  incremental: true

  include:
    - "src/**/*.cs"
    - "tests/**/*.cs"

  exclude:
    - "**/bin/**"
    - "**/obj/**"
    - "**/node_modules/**"

  chunk_size:
    max_tokens: 2000
    min_tokens: 100

  qdrant:
    collection: "codebase_chunks"
    host: "localhost"
    port: 6333
```

## Limitations

1. **Large files**: Files > 1MB are chunked at fixed intervals (not semantic)
2. **Binary files**: Skipped entirely
3. **Generated code**: May include generated files unless excluded
4. **Dynamic code**: Runtime-generated code not captured
5. **Cross-file relationships**: Dependencies extracted but not fully traced
