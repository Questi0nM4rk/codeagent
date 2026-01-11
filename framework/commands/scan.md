---
description: Build complete knowledge base of your codebase
---

# /scan - Build Knowledge Base

Scans entire codebase using Merkle tree change detection, Tree-sitter parsing, and Qdrant hybrid indexing.

**Reference:** `@~/.claude/framework/references/codebase-indexing.md`

## Usage

```
/scan                  # Incremental scan (only changed files)
/scan src/             # Scan specific path
/scan --full           # Force full rescan (ignore Merkle cache)
/scan --status         # Show index status without scanning
```

## Agent Pipeline

```
Main Claude (Orchestrator)
      │
      ├─► indexer agent
      │       → Computes Merkle tree for change detection
      │       → Parses changed files with Tree-sitter
      │       → Stores chunks in Qdrant (hybrid: BM25 + vector)
      │       → Returns: files indexed, chunks created
      │
      ├─► memory-writer agent
      │       → Stores patterns and architecture in A-MEM
      │       → Returns: memories created
      │
      └─► validator agent
              → Verifies index accuracy
              → Tests hybrid search quality
              → Returns: validation report
```

## What This Does

1. **Change Detection**: Merkle tree identifies only changed files
2. **Semantic Parsing**: Tree-sitter extracts functions, classes, methods
3. **Hybrid Indexing**: Qdrant stores both BM25 keywords and vectors
4. **Memory Storage**: Key patterns stored in A-MEM
5. **Validation**: Verify search results match actual code

## Supported Languages

```bash
# 9 languages supported
.cs, .csproj, .sln     # .NET (C#)
.cpp, .c, .h, .hpp     # C/C++
.rs, Cargo.toml        # Rust
.lua, *.rockspec       # Lua
.sh, .zsh              # Shell (Bash)
.py, pyproject.toml    # Python
.ts, .tsx              # TypeScript
.js, .jsx              # JavaScript
.go, go.mod            # Go
```

## Exclude Patterns

```bash
*/bin/*, */obj/*       # Build outputs
*/node_modules/*       # Dependencies
*/target/*             # Rust target
*/.git/*               # Git internals
*/__pycache__/*        # Python cache
*/dist/*, */build/*    # Build outputs
*.min.js, *.bundle.js  # Bundled JS
*/vendor/*             # Go vendor
```

## Output Format

```markdown
## Scan Complete

### Mode
[Full / Incremental]

### Index Statistics
| Metric | Count |
|--------|-------|
| Files scanned | X |
| Files changed | Y |
| Chunks created | Z |
| Chunks deleted | W |

### By Language
| Language | Files | Chunks |
|----------|-------|--------|
| C# | X | Y |
| TypeScript | X | Y |

### Performance
| Stage | Time |
|-------|------|
| Merkle tree | Xs |
| Tree-sitter | Xs |
| Qdrant upload | Xs |
| Total | Xs |

### Index Health
- Qdrant: [Healthy / Degraded]
- Chunks searchable: X
- BM25 index: [Ready / Building]
- Vector index: [Ready / Building]

### Changes Detected
| File | Action |
|------|--------|
| src/Auth/AuthService.cs | Updated |
| src/Models/User.cs | New |
| src/Old/Legacy.cs | Deleted |

### Patterns Stored in A-MEM
| Pattern | Type | Memory ID |
|---------|------|-----------|
| Repository pattern | architectural | mem_001 |
| JWT auth flow | code | mem_002 |

### Validation Results
- Search accuracy: X%
- Sample queries tested: Y
- Issues found: Z

### Index Location
- Manifest: .codeagent/index/manifest.json
- Qdrant collection: codebase_chunks
```

## When to Run

- **First time**: Always run `/scan` before other commands in a new project
- **After major changes**: When you've added significant new code
- **Before complex tasks**: Ensure knowledge is current
- **After merges**: When pulling in others' code
- **Automatic**: File hook triggers incremental index on file writes

## Incremental Indexing

### Merkle Tree Change Detection

```
1. Compute hash for each file: SHA256(content)
2. Compute hash for each directory: SHA256(sorted child hashes)
3. Compare against stored manifest.json
4. Only re-index files where hash differs
```

**Benefits:**
- 1000 files with 5 changes = only 5 files re-parsed
- Typical incremental scan: <2 seconds
- Full rescan: proportional to file count

### File Write Hook

When a file is written during implementation:
```
1. Hook triggers: index-file.sh
2. Computes file hash
3. If changed: re-parse and update Qdrant
4. Updates manifest.json entry
```

## Hybrid Search

After indexing, researchers can query:

```python
# BM25 (keyword) + Vector (semantic) combined
mcp__codebase__search(
    query="JWT token validation",
    k=10,
    language="csharp"
)
```

**Reciprocal Rank Fusion (RRF):**
- Combines BM25 and vector rankings
- Exact keyword matches rank high
- Semantically similar code also found

## Notes

- First scan may take 30-60 seconds for large codebases
- Subsequent scans use Merkle tree (only changed files)
- Use `--full` to force complete rescan
- Use `--status` to check index health without scanning
- Knowledge persists via A-MEM and Qdrant
- Validator agent tests search quality automatically
- Index stored in `.codeagent/index/` (add to .gitignore)
