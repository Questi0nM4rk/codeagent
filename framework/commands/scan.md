---
description: Build complete knowledge graph of your codebase
---

# /scan - Build Knowledge Base

Scans entire codebase and builds knowledge graph + memory store.

## Usage

```
/scan                  # Scan current directory
/scan src/             # Scan specific path
/scan --full           # Force full rescan (ignore cache)
```

## What This Does

1. **Discovery**: Find all source files matching your language stack
2. **AST Parsing**: Extract functions, classes, dependencies, call relationships
3. **Pattern Extraction**: Identify coding conventions and patterns
4. **Memory Storage**: Store in Letta for semantic retrieval
5. **Graph Storage**: Store in Neo4j for structural queries

## Process

### Step 1: File Discovery

Find all relevant source files:

```bash
# Languages we scan
.cs, .csproj, .sln     # .NET
.cpp, .c, .h, .hpp     # C/C++
.rs, Cargo.toml        # Rust
.lua, *.rockspec       # Lua
.sh, .zsh              # Shell

# Exclude patterns
*/bin/*, */obj/*       # Build outputs
*/node_modules/*       # Dependencies
*/target/*             # Rust target
*/.git/*               # Git internals
```

### Step 2: Structure Extraction

For each file, extract:
- Namespaces/modules
- Classes/structs/interfaces
- Functions/methods with signatures
- Import/dependency relationships
- Call relationships (what calls what)

### Step 3: Pattern Detection

Identify project conventions:
- Error handling patterns (exceptions vs Result<T>)
- Naming conventions
- Test organization
- Architecture patterns (layers, modules)
- Common idioms

### Step 4: Storage

Store extracted data:
- **Neo4j**: Structural relationships (calls, imports, inherits)
- **Letta**: Semantic patterns and conventions

## Output Format

```markdown
## Scan Complete

### Coverage
| Metric | Count |
|--------|-------|
| Files scanned | X |
| Functions indexed | X |
| Classes indexed | X |
| Dependencies mapped | X |

### By Language
| Language | Files | Functions | Classes |
|----------|-------|-----------|---------|
| C# | X | X | X |
| C++ | X | X | X |
| Rust | X | X | X |
| Lua | X | X | X |

### Patterns Detected
| Pattern | Occurrences | Files |
|---------|-------------|-------|
| [pattern name] | X | [file list] |

### Architecture Summary
[Brief description of detected architecture]

### Knowledge Gaps
- [Areas with sparse coverage]
- [Files that couldn't be parsed]

### Completeness: X%
```

## When to Run

- **First time**: Always run /scan before other commands
- **After major changes**: When you've added significant new code
- **Before complex tasks**: Ensure knowledge is current
- **After merges**: When pulling in others' code

## Notes

- First scan may take a few minutes for large codebases
- Subsequent scans are incremental (only changed files)
- Use `--full` to force complete rescan
- Knowledge persists across Claude Code sessions
