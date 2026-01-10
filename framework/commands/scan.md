---
description: Build complete knowledge base of your codebase
---

# /scan - Build Knowledge Base

Scans entire codebase and builds memory store using multiple specialized agents.

## Usage

```
/scan                  # Scan current directory
/scan src/             # Scan specific path
/scan --full           # Force full rescan (ignore cache)
```

## Agent Pipeline

This command spawns three agents in sequence:

```
Main Claude (Orchestrator)
      │
      ├─► indexer agent
      │       → Analyzes file structure and patterns
      │       → Returns: files scanned, patterns found
      │
      ├─► memory-writer agent
      │       → Stores patterns and architecture in A-MEM
      │       → Returns: memories created
      │
      └─► validator agent
              → Verifies accuracy against actual code
              → Corrects errors if found
              → Returns: validation report
```

## What This Does

1. **Discovery**: Find all source files matching your language stack
2. **Pattern Extraction**: Identify coding conventions and patterns
3. **Memory Storage**: Store in A-MEM for semantic retrieval
4. **Validation**: Verify stored data matches actual code

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

### Coverage
| Metric | Count |
|--------|-------|
| Files scanned | X |
| Patterns found | X |

### By Language
| Language | Files |
|----------|-------|
| C# | X |
| TypeScript | X |
| ... | ... |

### Patterns Detected
| Pattern | Occurrences | Files |
|---------|-------------|-------|
| [pattern name] | X | [file list] |

### Architecture Summary
[Brief description of detected architecture]

### Validation Results
- Memories verified: X
- Accuracy: Y%
- Corrections made: Z

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
- Knowledge persists across Claude Code sessions via A-MEM
- Validator agent corrects errors automatically
