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

## What This Does

1. Loads the plan from previous /plan command
2. Checks execution mode (SEQUENTIAL or PARALLEL)
3. Executes TDD loop for each step/task
4. Commits on success, checkpoints on failure
5. Triggers /integrate automatically after parallel completion

## TDD Loop (Every Step)

```
┌─────────────────────────────────────────────────────┐
│  1. Write test for the behavior                     │
│  2. Run test → MUST FAIL                            │
│  3. Commit test                                     │
│  4. Write minimal implementation                    │
│  5. Run test → MUST PASS (max 3 attempts)          │
│  6. Commit implementation                           │
│  7. Run full test suite → check for regressions    │
│  8. Refactor if needed (tests must still pass)     │
│  9. Next step                                       │
└─────────────────────────────────────────────────────┘
```

## Sequential Mode

Single @implementer agent executes all steps in order:

```markdown
Step 1: [description]
├── Write test
├── Run test (fail) ✓
├── Commit: test(scope): add test for [behavior]
├── Write code
├── Run test (pass) ✓
├── Commit: feat(scope): implement [behavior]
└── Full suite: 47/47 passing ✓

Step 2: [description]
├── ...
```

## Parallel Mode

Spawns separate agents for isolated tasks:

```
┌─────────────────────────────────────────────────────┐
│                 @orchestrator                        │
│          Load plan, verify boundaries               │
└─────────────────────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Subagent A │ │  Subagent B │ │  Subagent C │
│  Task A     │ │  Task B     │ │  Task C     │
│  Exclusive: │ │  Exclusive: │ │  Exclusive: │
│  [files]    │ │  [files]    │ │  [files]    │
└─────────────┘ └─────────────┘ └─────────────┘
         │              │              │
         └──────────────┼──────────────┘
                        ▼
┌─────────────────────────────────────────────────────┐
│               /integrate (auto)                      │
│     Merge, validate, full test suite                │
└─────────────────────────────────────────────────────┘
```

Each subagent:
- Has exclusive file ownership (can only modify their files)
- Follows same TDD loop
- Reports boundary violations immediately
- Works independently (no cross-communication)

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
- Passed: 52 ✓
- Coverage: 84%

Ready for /review
```

### Parallel Complete

```markdown
## Implementation Complete

### Mode: PARALLEL ⚡
Duration: 5m 23s (vs ~12m sequential)

### Task Results

#### Task A: User Management ✅
- Files modified: 4
- Tests added: 12
- Boundary violations: None
- Commits: 4

#### Task B: Product Catalog ✅
- Files modified: 5
- Tests added: 15
- Boundary violations: None
- Commits: 5

### Integration
- Merge conflicts: None ✓
- Full test suite: 67/67 passing ✓
- Interface consistency: ✓

Ready for /review
```

## Failure Handling

### Test Won't Pass (3 attempts)

```markdown
## BLOCKED: Test Failure

### Step: [which step]
### Test: [test name]

### Attempts
1. [approach] → [error]
2. [approach] → [error]
3. [approach] → [error]

### Checkpoint Created
Branch: checkpoint/[task]-[timestamp]

### Options
1. /implement --continue (after manual fix)
2. /plan "alternative approach" (try different design)
3. Ask for human help

### Needs
[Specific information or help needed]
```

### Parallel Boundary Violation

```markdown
## STOPPED: Boundary Violation

### Task: [which task]
### Attempted: Modify [file]
### Reason: File is in [read-only/forbidden] list

### Resolution
This file is owned by [other task / shared].
Options:
1. Wait for other task to complete
2. Redesign to not need this file
3. Move to sequential mode

### Status
- Task A: Stopped (violation)
- Task B: Continuing
- Task C: Continuing
```

## Notes

- Always run /plan before /implement
- /implement reads the plan from memory - don't modify manually
- Commits are automatic but push is NEVER automatic
- Use --continue to resume after fixing issues
- Parallel mode requires all tasks to complete before /integrate
