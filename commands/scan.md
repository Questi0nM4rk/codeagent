---
name: scan
description: Build complete knowledge base of your codebase
---

# /scan - Build Knowledge Base

Scans entire codebase using Merkle tree change detection, Tree-sitter parsing, and hybrid indexing.

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
      |
      +-- indexer agent
      |       --> Computes Merkle tree for change detection
      |       --> Parses changed files with Tree-sitter
      |       --> Stores chunks in index (hybrid: BM25 + vector)
      |       --> Returns: files indexed, chunks created
      |
      +-- memory-writer agent
      |       --> Stores patterns and architecture in A-MEM
      |       --> Returns: memories created
      |
      +-- validator agent
              --> Verifies index accuracy
              --> Tests search quality
              --> Returns: validation report
```

## What This Does

1. **Change Detection**: Merkle tree identifies only changed files
2. **Semantic Parsing**: Tree-sitter extracts functions, classes, methods
3. **Hybrid Indexing**: Stores both BM25 keywords and vectors
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

## Expected Output

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
| Index upload | Xs |
| Total | Xs |

### Index Health
- Index: [Healthy / Degraded]
- Chunks searchable: X
- BM25 index: [Ready / Building]
- Vector index: [Ready / Building]

### Patterns Stored in A-MEM
| Pattern | Type | Memory ID |
|---------|------|-----------|
| Repository pattern | architectural | mem_001 |
| JWT auth flow | code | mem_002 |

### Validation Results
- Search accuracy: X%
- Sample queries tested: Y
- Issues found: Z
```

## When to Run

- **First time**: Always run `/scan` before other commands
- **After major changes**: When you've added significant new code
- **Before complex tasks**: Ensure knowledge is current
- **After merges**: When pulling in others' code
- **Automatic**: File hook triggers incremental index on writes

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| path | No | Specific path to scan (defaults to project root) |
| --full | No | Force full rescan ignoring cache |
| --status | No | Show status without scanning |

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Index | `.codeagent/index/` | Searchable code chunks |
| Manifest | `.codeagent/index/manifest.json` | Merkle tree for change detection |
| A-MEM | Memory system | Patterns and architecture knowledge |

## Example

```bash
# First time in a project
/scan

# After pulling new code
/scan --full

# Check if index is healthy
/scan --status
```

## Notes

- First scan may take 30-60 seconds for large codebases
- Subsequent scans use Merkle tree (only changed files)
- Knowledge persists via A-MEM
- Index stored in `.codeagent/index/` (add to .gitignore)
