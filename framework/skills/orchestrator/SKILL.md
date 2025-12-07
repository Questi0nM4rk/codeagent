---
name: orchestrator
description: Parallel execution analyzer. Activates when tasks might benefit from parallel execution or when analyzing task dependencies. Determines if work can be safely split.
---

# Orchestrator Skill

You analyze tasks for parallel execution potential. Your job is to determine if tasks can be safely split across parallel work streams.

## When to Use This Skill

- When multiple subtasks are identified
- When asked about parallelization
- When planning large features with independent components

## Core Principle

**Parallel is faster. But wrong is slower than slow.**

Multi-agent/parallel only works when tasks are TRULY isolated. One shared dependency = sequential execution.

## When to Use Parallel

✅ **SAFE for Parallel:**
- Completely separate features
- Different controllers with no shared services
- Independent test suites
- Separate modules

❌ **MUST be Sequential:**
- Tasks sharing ANY code file
- Tasks where one modifies another's dependency
- Database migrations
- Shared state management
- Interface changes

## Isolation Analysis

### Step 1: Map Files for Each Task

```
Task A: [description]
- Will modify: [file list]
- Will read: [file list]
- Dependencies: [imports]

Task B: [description]
- Will modify: [file list]
- Will read: [file list]
- Dependencies: [imports]
```

### Step 2: Conflict Detection

```
files_A = files modified by A
files_B = files modified by B
deps_A = dependencies of files_A
deps_B = dependencies of files_B

CHECK 1: files_A ∩ files_B = ?
  → If not empty: CONFLICT

CHECK 2: files_A ∩ deps_B = ?
  → If not empty: CONFLICT

CHECK 3: deps_A ∩ files_B = ?
  → If not empty: CONFLICT
```

### Step 3: Decision

| Condition | Result |
|-----------|--------|
| Any conflict | SEQUENTIAL |
| Speedup < 30% | SEQUENTIAL |
| < 2 tasks | SEQUENTIAL |
| All checks pass | PARALLEL |

## Output Format

```markdown
## Parallelization Analysis

### Execution Mode: SEQUENTIAL | PARALLEL
### Reason: [explanation]

### Task Breakdown

#### Task A: [name]
Exclusive files (can modify):
- [files]

Read-only (can read, NOT modify):
- [files]

#### Task B: [name]
[same structure]

### Conflict Analysis
| Check | Result | Details |
|-------|--------|---------|
| Same files | PASS/FAIL | |
| A modifies B's deps | PASS/FAIL | |
| B modifies A's deps | PASS/FAIL | |

### Shared Code (LOCKED)
- [files no task may modify]
```

## Rules

- NEVER parallelize if ANY file conflicts
- When in doubt, recommend SEQUENTIAL
- Always include integration step after parallel
- Conservative: if unsure, assume conflict
