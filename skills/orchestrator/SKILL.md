---
name: orchestrator
description: Parallel execution analysis. Determines if tasks can run concurrently by detecting file and dependency conflicts.
activation:
  triggers:
    - "parallel"
    - "concurrent"
    - "isolation"
    - "can these run together"
    - "dependency analysis"
  file_patterns: []
thinking: think harder
tools:
  - Read
  - Glob
  - Grep
  - mcp__amem__search_memory
  - mcp__amem__store_memory
---

# Orchestrator Skill

Parallelization analysis and execution strategy selection.

## The Iron Law

```
CONSERVATIVE BY DEFAULT - IF UNCERTAIN, SEQUENTIAL
The cost of a merge conflict far exceeds the benefit of parallel execution.
```

## Core Principle

> "Only parallelize what is truly isolated. Shared state is a merge conflict waiting to happen."

## When to Activate

**Always:**

- Plan contains multiple tasks
- Architect output has several steps
- Need to determine execution strategy
- Analyzing file boundaries

**Skip when:**

- Single task only
- User explicitly requests sequential

## Step 0: Check Past Decisions (ALWAYS)

```yaml
mcp__amem__search_memory:
  query: "parallelization conflict decision"
  k: 10
```

If past decisions found:

- Note patterns that caused merge conflicts
- Avoid known problematic parallel combinations
- Build on successful parallelization patterns

## Isolation Analysis

For each pair of tasks (A, B), analyze:

```
files_A = files modified by task A
files_B = files modified by task B
imports_A = imports used by files_A
imports_B = imports used by files_B
```

### Conflict Detection

Use file tools to discover:

```yaml
# Find files that would be modified
Glob: pattern="[task patterns]"

# Check imports/dependencies
Grep: pattern="import|using|require" path="[file]"

# Read file headers
Read: file_path="[file]"
```

### CONFLICT EXISTS IF

- `files_A intersection files_B` is not empty (same files modified)
- Both tasks import/modify the same shared module
- Shared mutable state (database tables, caches, config files)

## Decision Matrix

| Condition | Decision | Confidence |
|-----------|----------|------------|
| Any file conflict | SEQUENTIAL | High |
| Same module imported and modified | SEQUENTIAL | High |
| Shared database tables | SEQUENTIAL | High |
| Shared config files | SEQUENTIAL | Medium |
| Read-only shared deps | PARALLEL OK | Medium |
| Completely isolated | PARALLEL OK | High |
| Uncertain | SEQUENTIAL | Low |

## Execution Strategy Selection

After parallelization analysis, select strategy based on checkpoint types:

| Strategy | When | Main Context |
|----------|------|--------------|
| **A** | All tasks `type="auto"` | ~5% |
| **B** | Has `checkpoint:human-verify` | ~20% |
| **C** | Has `checkpoint:decision` | 100% |

### Selection Algorithm

```python
def select_strategy(tasks):
    has_decision = any(t.type == "checkpoint:decision" for t in tasks)
    has_verify = any(t.type == "checkpoint:human-verify" for t in tasks)

    if has_decision:
        return "C"  # Decisions require main context
    elif has_verify:
        return "B"  # Segment at verify checkpoints
    else:
        return "A"  # Fully autonomous
```

### Integration with Parallel Mode

```
Parallelization Analysis
         |
         +-- SEQUENTIAL --> Select Strategy A, B, or C
         |
         +-- PARALLEL --> Each parallel task must be Strategy A
                          (parallel tasks cannot have checkpoints)
```

**Rule:** Parallel tasks MUST have `type="auto"`. Tasks with checkpoints cannot be parallelized.

## Output Format

```markdown
## Parallelization Analysis

### Tasks Analyzed
1. Task A: [description]
   - Files: [list]
   - Imports: [shared modules]

2. Task B: [description]
   - Files: [list]
   - Imports: [shared modules]

### Conflict Analysis

#### File Conflicts
| Task A File | Task B File | Conflict Type |
|-------------|-------------|---------------|
| [none or list] |

#### Shared Modules
| Module | Used By | Modified By |
|--------|---------|-------------|
| [none or list] |

#### Shared State
- Database tables: [list or none]
- Config files: [list or none]
- Caches: [list or none]

### Decision

**Mode: PARALLEL | SEQUENTIAL**
**Confidence: High | Medium | Low**

### Execution Strategy: [A|B|C]

**Reason:** [explanation based on checkpoint types]

### Rationale
[Why this decision]

### If PARALLEL
- Task A boundaries: [files it can touch]
- Task B boundaries: [files it can touch]
- Integration requirements: [what to check after]

### If SEQUENTIAL
- Order: A --> B (or B --> A)
- Reason: [why this order]

### Warnings
- [Any concerns even if parallel is possible]
```

## Store Decision (ALWAYS)

```yaml
mcp__amem__store_memory:
  content: |
    ## Parallelization: [task description]
    Type: process
    Context: [when this applies]

    ### Decision
    [PARALLEL or SEQUENTIAL]

    ### Rationale
    [Why this decision was made]

    ### Conflicts Found
    [List any file/module conflicts]
  tags: ["project:[name]", "parallelization", "decision"]
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "They probably don't conflict" | Probably is not good enough. Verify. |
| "Parallel is faster" | Merge conflicts cost more than sequential. |
| "Only one file overlaps" | One file is enough to conflict. |
| "We can fix conflicts later" | Prevention is easier than resolution. |

## Red Flags - STOP

- Assuming isolation without checking
- Ignoring shared state
- Not checking imports/dependencies
- Forcing parallel when uncertain
- Estimated speedup < 30%
- Parallelizing database migrations
- Parallelizing shared service modifications

If you see these, default to SEQUENTIAL.

## Verification Checklist

- [ ] Queried A-MEM for past conflicts
- [ ] Analyzed all file modifications
- [ ] Checked import statements
- [ ] Identified shared state
- [ ] Calculated estimated speedup
- [ ] Selected execution strategy
- [ ] Stored decision in A-MEM

## Related Skills

- `architect` - Provides task breakdown
- `implementer` - Executes with file boundaries
- `reviewer` - Validates after integration

## Handoff

After analysis completes:

1. Store decision in A-MEM
2. Pass file boundaries to implementer agents
3. If PARALLEL: set up worktrees via `/implement`
4. Include in `/plan` output
