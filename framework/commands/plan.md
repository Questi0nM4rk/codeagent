---
description: Research, design, create epics/tasks, and auto-detect parallel execution potential
---

# /plan - Unified Planning

Gathers context, designs solution, creates backlog items (epics/tasks), and determines if parallel execution is beneficial.

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

### XML Tasks Section (NEW)

After architecture decision, include XML task format from architect:

```markdown
## XML Tasks

<task type="auto|checkpoint:human-verify|checkpoint:decision">
  <name>[Task name]</name>
  <files>
    <exclusive>[Files to modify]</exclusive>
    <readonly>[Files to read]</readonly>
    <forbidden>[Files to avoid]</forbidden>
  </files>
  <action>[Specific instructions]</action>
  <verify>[Verification command/check]</verify>
  <done>
    - [ ] [Criterion 1]
    - [ ] [Criterion 2]
  </done>
</task>
```

Reference: `@~/.claude/framework/references/xml-task-format.md`

### Execution Strategy Section (NEW)

After parallelization analysis, include strategy from orchestrator:

```markdown
## Execution Strategy: [A|B|C]

**Reason:** [Based on checkpoint types in tasks]

| Strategy | When | Behavior |
|----------|------|----------|
| A | All auto | Single subagent, full plan |
| B | Has verify | Fresh subagent per segment |
| C | Has decision | Main context only |

### Checkpoint Analysis
| Task | Type | Impact |
|------|------|--------|
```

Reference: `@~/.claude/framework/references/execution-strategies.md`

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

## Context File Generation

After planning completes, generate context files in `.planning/` directory:

### Directory Structure

```
.planning/
├── STATE.md       # Session state and progress tracking
├── PLAN.md        # Executable task definitions (XML format)
└── ISSUES.md      # Deferred enhancements (created during /implement)
```

### .planning/STATE.md

Generated from template: `@~/.claude/framework/templates/planning/STATE.md.template`

Contents:
- Session ID (timestamp-based)
- Current position (phase, task, status)
- Decisions table (empty, filled during /implement)
- Blockers table
- A-MEM/Reflection memory links

### .planning/PLAN.md

Generated from template: `@~/.claude/framework/templates/planning/PLAN.md.template`

Contents:
- Task name and metadata
- Execution mode (SEQUENTIAL/PARALLEL)
- Execution strategy (A/B/C)
- XML tasks from architect
- Deviation rules reference
- Verification steps

### Output Addition

Add to plan output:

```markdown
## Context Files Created

- `.planning/STATE.md` - Session state tracking (empty decisions table)
- `.planning/PLAN.md` - Executable XML task definitions

Ready for `/implement` with strategy [A|B|C]
```

## Backlog Integration

After planning completes, generate backlog items in `.codeagent/backlog/`:

### Epic Creation (if scope is large)

**File:** `.codeagent/backlog/epics/EPIC-{N}.yaml`

```yaml
id: EPIC-{N}
type: epic
name: "[Task name from plan]"
description: |
  [From architect's architecture decision]
status: ready
priority: high
tasks: [TASK-{N}, TASK-{N+1}]
source:
  type: plan
  ref: "[session-id]"
context:
  files_to_reference: [from plan's affected files]
  patterns_to_follow: [from architect's patterns]
  constraints: [from plan's risks]
created: "[timestamp]"
```

### Task Creation

**File:** `.codeagent/backlog/tasks/TASK-{N}.yaml`

```yaml
id: TASK-{N}
type: task
name: "[Step name from plan]"
description: |
  [Step description]
epic: EPIC-{N}  # Link to parent epic
status: ready
depends_on: []  # Auto-populated from plan dependencies
blocks: []
implementation:
  files:
    exclusive: [from plan's exclusive files]
    readonly: [from plan's readonly files]
    forbidden: [from plan's forbidden files]
  action: |
    [From XML task action]
  verify: [from XML task verify]
  done: [from XML task done criteria]
execution:
  strategy: A  # From orchestrator's strategy decision
  checkpoint_type: auto  # auto | human-verify | decision
source:
  type: plan
  ref: "[session-id]"
created: "[timestamp]"
```

### Update BACKLOG.md

After creating items, regenerate `.codeagent/backlog/BACKLOG.md`:

```markdown
# [Project] Backlog

*Auto-generated. Do not edit manually.*

## Summary

| Type | Backlog | Ready | In Progress | Blocked | Done |
|------|---------|-------|-------------|---------|------|
| Epics | 0 | 1 | 0 | 0 | 0 |
| Tasks | 0 | 3 | 0 | 0 | 0 |

## Ready Items

### EPIC-001: [name]
- [ ] TASK-001: [name]
- [ ] TASK-002: [name]
- [ ] TASK-003: [name]
```

### ID Generation

```
1. Read .codeagent/config.yaml for id_prefix
2. Find highest existing number for type
3. Increment: {prefix}-{TYPE}-{N+1}

Example: If id_prefix="MP" and highest task is TASK-005
         Next task ID = MP-TASK-006
```

## Integration with /analyze

If `/analyze` was run first:
- Link epic to spike: `source.type: spike`, `source.ref: SPIKE-{N}`
- Import findings as context
- Reference spike output in epic description

## Notes

- Always run /scan before first /plan in a project
- /plan stores its output in memory for /implement to use
- Use `--deep` for complex investigative tasks
- If confidence < 7, the plan will recommend human review
- Architecture decisions are stored in A-MEM for future reference
- Context files are generated in `.planning/` directory
- Backlog items are created in `.codeagent/backlog/`
- Maximum 2-3 tasks per plan to prevent context degradation
