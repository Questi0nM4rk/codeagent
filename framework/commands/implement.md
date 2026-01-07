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

### Sequential Mode

```
Main Claude (Orchestrator)
      │
      └─► implementer agent (opus)
              skills: [tdd, domain skills based on file types]
              → Executes TDD loop for each step
              → Uses reflection MCP for failure learning
              → Returns: implementation results, commits made
```

### Parallel Mode

```
Main Claude (Orchestrator)
      │
      ├─► implementer agent (Task A)
      │       skills: [tdd, relevant domain skills]
      │       exclusive files: [list]
      │       → TDD loop for Task A
      │
      ├─► implementer agent (Task B)
      │       skills: [tdd, relevant domain skills]
      │       exclusive files: [list]
      │       → TDD loop for Task B
      │
      └─► (auto-triggers /integrate when all complete)
```

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
9. Update code-graph index
10. Next step
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

## Notes

- Always run /plan before /implement
- /implement reads the plan from memory - don't modify manually
- Commits are automatic but push is NEVER automatic
- Use --continue to resume after fixing issues
- Parallel mode requires all tasks to complete before /integrate
- Learner agent triggers automatically after successful implementation
