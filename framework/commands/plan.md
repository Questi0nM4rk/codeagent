---
description: Research, design, and auto-detect parallel execution potential
---

# /plan - Unified Planning

Gathers context, designs solution, and automatically determines if parallel execution is beneficial.

## Usage

```
/plan "Add JWT authentication"              # Standard planning
/plan "Add users and products"              # Auto-detects if parallelizable
/plan --sequential "Complex refactoring"    # Force sequential mode
/plan --deep "Investigate performance"      # Extra research phase
```

## Agent Pipeline

This command spawns three agents:

```
Main Claude (Orchestrator)
      │
      ├─► researcher agent (opus)
      │       skills: [domain skills based on file types]
      │       → Queries A-MEM, codebase, context7
      │       → Returns: context summary, confidence score
      │
      ├─► architect agent (opus)
      │       skills: [spec-driven, relevant domain skills]
      │       → Uses ultrathink for structured exploration
      │       → Returns: 3+ approaches with evaluation
      │
      └─► orchestrator agent (opus)
              → Analyzes file/dependency conflicts
              → Returns: PARALLEL or SEQUENTIAL decision
```

## Process

### Phase 1: Research (researcher agent)

```markdown
Research Priority:
1. Query A-MEM for similar past implementations
2. Analyze codebase for patterns and conventions (Grep/Glob/Read)
3. Only if needed: Context7 for docs, external research

Output: Context summary with confidence score
```

### Phase 2: Design (architect agent)

```markdown
Structured Exploration (ultrathink):
1. Decompose into sub-problems
2. Generate 3+ approaches per sub-problem
3. Evaluate each: feasibility, risk, complexity
4. Select best path with documented rationale

Output: Architecture decision with explored alternatives
```

### Phase 3: Parallelization Analysis (orchestrator agent)

**Automatically runs if task has multiple subtasks.**

```markdown
Conflict Detection:
For each pair of subtasks (A, B):
  files_A = files modified by A
  files_B = files modified by B
  deps_A = dependencies of files_A
  deps_B = dependencies of files_B

  If (files_A ∩ files_B) ≠ ∅ → CONFLICT
  If (files_A ∩ deps_B) ≠ ∅ → CONFLICT
  If (deps_A ∩ files_B) ≠ ∅ → CONFLICT
  Else → PARALLELIZABLE
```

## Output Format

### Sequential Mode

```markdown
## Plan: [Task Name]

### Execution Mode: SEQUENTIAL
Reason: [single task / conflicts in X files / user requested]

### Research Summary
[From researcher agent - context gathered, confidence score]

### Architecture Decision
[From architect agent - chosen approach, alternatives explored]

### Implementation Steps
1. [ ] Step 1 - [description] - [files]
2. [ ] Step 2 - [description] - [files]
3. [ ] Step 3 - [description] - [files]

### Test Strategy
- Unit tests: [what to test]
- Integration tests: [what to test]
- Edge cases: [list]

### Risks
| Risk | Mitigation |
|------|------------|
| [risk] | [how to handle] |

### Confidence: X/10

Ready for /implement
```

### Parallel Mode

```markdown
## Plan: [Task Name]

### Execution Mode: PARALLEL
Reason: X independent subtasks, no file conflicts
Estimated speedup: Y%

### Research Summary
[From researcher agent]

### Architecture Decision
[From architect agent]

### Parallelization Analysis
[From orchestrator agent - isolation boundaries]

#### Task A: [name]
Exclusive files: [list - can modify]
Read-only: [list - can read only]
Forbidden: [list - don't touch]

#### Task B: [name]
Exclusive files: [list]
Read-only: [list]
Forbidden: [list]

### Shared Code (LOCKED - no task may modify)
- [files that are read-only for all tasks]

### Confidence: X/10

Ready for /implement (will auto-parallelize)
```

## Mode Detection Rules

| Condition | Mode | Reason |
|-----------|------|--------|
| Single subtask | SEQUENTIAL | Nothing to parallelize |
| `--sequential` flag | SEQUENTIAL | User forced |
| Any file modified by 2+ subtasks | SEQUENTIAL | Conflict risk |
| Subtask A modifies B's dependency | SEQUENTIAL | Dependency conflict |
| Estimated speedup < 30% | SEQUENTIAL | Overhead not worth it |
| All subtasks fully isolated | PARALLEL | Safe to proceed |

## A-MEM Integration

The planning pipeline uses A-MEM memory throughout:

**Researcher agent queries A-MEM for:**
- Past similar designs (avoids reinventing)
- Project-specific constraints and conventions
- Previous architecture decisions

**Architect agent stores:**
- New design decisions (with alternatives considered)
- Tradeoff analysis and rationale
- Implementation notes for future reference

**Orchestrator agent queries/stores:**
- Past parallelization decisions
- Known file conflict patterns

A-MEM automatically links related memories and evolves existing context.

## Notes

- Always run /scan before first /plan in a project
- /plan stores its output in memory for /implement to use
- Use `--deep` for complex investigative tasks
- If confidence < 7, the plan will recommend human review
- Architecture decisions are stored in A-MEM for future reference
