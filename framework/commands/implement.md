---
description: Execute plan using TDD (auto-detects parallel from plan)
---

# /implement - TDD Implementation

Implements the plan using Test-Driven Development. Automatically uses parallel execution if the plan detected isolated subtasks.

## Usage

```
/implement                  # Execute plan (uses mode from /plan)
/implement --sequential     # Force sequential even if plan allows parallel
/implement --step 2         # Start from step 2 (sequential mode)
/implement --continue       # Continue from last checkpoint
/implement --task=A         # Re-run specific parallel task
```

## Agent Pipeline

### Execution by Strategy

Reference: `@~/.claude/framework/references/execution-strategies.md`

#### Strategy A: Fully Autonomous

```
Main Claude (Orchestrator) ~5% context
      │
      └─► Single subagent (opus)
              skills: [tdd, domain skills]
              → Executes ALL tasks sequentially
              → Full 200k context for implementation
              → No interruptions
              → Reports only on completion or block
```

**When:** All tasks have `type="auto"`. No checkpoints needed.

#### Strategy B: Segmented Execution (Fresh Subagent Per Task)

```
Main Claude (Orchestrator) ~20% context
      │
      ├─► Subagent 1 (fresh context)
      │       → Executes tasks until checkpoint
      │       → Returns results to main
      │
      ├─► [Main validates checkpoint with user]
      │
      ├─► Subagent 2 (fresh context)
      │       → Executes next segment
      │       → Returns results to main
      │
      └─► [Continue until all complete]
```

**When:** Has `checkpoint:human-verify` tasks. No decision checkpoints.

**Benefits:**
- Full 200k context per segment
- No context degradation across tasks
- Isolated failures

#### Strategy C: Main Context Only

```
Main Claude (no subagents) 100% context
      │
      ├─► Execute Task 1 (auto)
      │
      ├─► Hit checkpoint:decision
      │       → Present options to user
      │       → User selects option
      │       → Record in STATE.md
      │
      └─► Continue with selected path
```

**When:** Has `checkpoint:decision` tasks. Decisions affect subsequent tasks.

### Parallel Mode

```
Main Claude (Orchestrator)
      │
      ├─► implementer agent (Task A) - Strategy A only
      │       skills: [tdd, relevant domain skills]
      │       exclusive files: [list]
      │       → TDD loop for Task A
      │
      ├─► implementer agent (Task B) - Strategy A only
      │       skills: [tdd, relevant domain skills]
      │       exclusive files: [list]
      │       → TDD loop for Task B
      │
      └─► (auto-triggers /integrate when all complete)
```

**Note:** Parallel tasks MUST be `type="auto"`. Tasks with checkpoints cannot be parallelized.

## TDD Loop (Every Step)

```
1. Write test for the behavior
2. Run test → MUST FAIL
3. Commit test
4. Write minimal implementation
5. Run test → MUST PASS (max 3 attempts)
6. Commit implementation
7. Run full test suite → check for regressions
8. Refactor if needed (tests must still pass)
9. Next step
```

## Deviation Handling

Reference: `@~/.claude/framework/references/deviation-rules.md`

During implementation, handle unexpected situations with these rules:

### The Five Rules

| Rule | Condition | Action | Document In |
|------|-----------|--------|-------------|
| **1** | Bug discovered | Auto-fix | STATE.md |
| **2** | Missing security/validation | Auto-add | STATE.md |
| **3** | Blocker with clear fix | Auto-fix | STATE.md |
| **4** | Architectural change needed | **STOP** | Ask user |
| **5** | Enhancement opportunity | Log only | ISSUES.md |

**Priority:** Rule 4 (stop) > Rules 1-3 (auto-fix) > Rule 5 (log)

### Auto-Fix Examples (Rules 1-3)

```markdown
## Deviations in STATE.md
| Time | Type | Issue | Action | Files |
|------|------|-------|--------|-------|
| 14:32 | bug | Null check missing | Added guard clause | UserService.cs |
| 14:45 | security | SQL injection risk | Parameterized query | SearchRepo.cs |
| 15:01 | blocker | Missing DI registration | Added to Program.cs | Program.cs |
```

### STOP Example (Rule 4)

```markdown
## Architectural Decision Required

**Task:** Add caching layer

**Issue:** Current design requires modifying shared IRepository interface

**Options:**
1. Modify interface (breaks 12 existing implementations)
2. Create decorator pattern (more code, no breaking changes)
3. Abandon caching for now

**My recommendation:** Option 2 because [rationale]

Please choose an option to proceed.
```

### Log Example (Rule 5)

Add to `.planning/ISSUES.md`:
```markdown
## Enhancements (Not in Scope)
| ID | Enhancement | Discovered During | Priority |
|----|-------------|-------------------|----------|
| ENH-001 | UserService could use caching | Add user auth | Medium |
```

## Failure Handling

The implementer agent uses reflection MCP on failures:

```
mcp__reflection__reflect_on_failure
    → Analyze what went wrong
    → Check similar past failures
    → Generate improved attempt

After 3 failures:
    → Create checkpoint branch
    → Output BLOCKED status
    → Store episode in reflection memory
```

## Output Format

### Sequential Complete

```markdown
## Implementation Complete

### Mode: SEQUENTIAL

### Steps Completed
- [x] Step 1: [description]
- [x] Step 2: [description]
- [x] Step 3: [description]

### Files Modified
| File | Action | Lines Changed |
|------|--------|---------------|
| path/file.cs | Modified | +45, -12 |
| path/new.cs | Created | +120 |

### Tests Added
| Test File | Tests | Status |
|-----------|-------|--------|
| path/Tests.cs | 5 | All passing |

### Commits
- `test(auth): add tests for JWT validation`
- `feat(auth): implement JWT validation`
- `test(auth): add tests for token refresh`
- `feat(auth): implement token refresh`

### Test Results
- Total: 52
- Passed: 52
- Coverage: 84%

Ready for /review
```

### Parallel Complete

```markdown
## Implementation Complete

### Mode: PARALLEL
Duration: 5m 23s (vs ~12m sequential)

### Task Results

#### Task A: User Management
- Status: Complete
- Files modified: 4
- Tests added: 12
- Boundary violations: None
- Commits: 4

#### Task B: Product Catalog
- Status: Complete
- Files modified: 5
- Tests added: 15
- Boundary violations: None
- Commits: 5

### Integration (auto-triggered)
- Merge conflicts: None
- Full test suite: 67/67 passing
- Interface consistency: Verified

Ready for /review
```

### Blocked

```markdown
## BLOCKED: Test Failure

### Step: [which step]
### Test: [test name]

### Attempts
1. [approach] → [error]
2. [approach] → [error]
3. [approach] → [error]

### Reflection Analysis
[From mcp__reflection__reflect_on_failure]

### Similar Past Issues
[From mcp__reflection__retrieve_episodes]

### Checkpoint Created
Branch: checkpoint/[task]-[timestamp]

### Options
1. /implement --continue (after manual fix)
2. /plan "alternative approach" (try different design)
3. Ask for human help

### Needs
[Specific information or help needed]
```

## A-MEM Integration

The implementer agent uses A-MEM memory:

**Before implementing:**
- Queries A-MEM for architecture decisions from /plan
- Searches for similar implementation patterns
- Checks for project-specific conventions

**After successful implementation:**
- Stores novel patterns for future reference
- A-MEM automatically links to architect's design decisions

This ensures implementations follow established patterns and new patterns are captured for future use.
A-MEM's automatic linking helps connect related implementations across sessions.

## Completion

After all tasks complete:

### 1. Update STATE.md

```markdown
## Current Position
- Status: complete
- Last Activity: [timestamp] - All tasks completed

## Deviations During Implementation
[Populated from deviation handling]
```

### 2. Generate SUMMARY.md

Template: `@~/.claude/framework/templates/planning/SUMMARY.md.template`

Contents:
- What was done (summary description)
- Files changed (table with actions and line counts)
- Tests added (coverage info)
- Commits made (list with hashes)
- Deviations from plan (table)
- Lessons learned
- Memory links (A-MEM and reflection IDs)

### 3. Store in Memory

**A-MEM (patterns for future use):**
```
mcp__amem__store_memory:
  content="## Implementation: [task name]
Type: implementation
Context: [when this applies]

### Approach
[What was implemented]

### Patterns Used
[Key patterns and conventions]

### Deviations
[Any auto-fixes applied]"
  tags=["project:[name]", "implementation"]
```

**Reflection (episodes for learning):**
```
mcp__reflection__store_episode:
  task="[task description]"
  approach="[strategy used]"
  outcome="success"
  feedback="[results]"
  feedback_type="implementation_complete"
  reflection={
    "strategy_used": "[A|B|C]",
    "deviations": "[count and types]",
    "lessons": "[what to remember]"
  }
```

### 4. Clean Up

- Archive `.planning/PLAN.md` to `.planning/history/[timestamp]-PLAN.md`
- Keep STATE.md for session continuity
- ISSUES.md persists for future reference

## Notes

- Always run /plan before /implement
- /implement reads the plan from memory - don't modify manually
- Commits are automatic but push is NEVER automatic
- Use --continue to resume after fixing issues
- Parallel mode requires all tasks to complete before /integrate
- Learner agent triggers automatically after successful implementation
