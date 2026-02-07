---
name: implement
description: Execute plan using TDD workflow
---

# /implement - TDD Implementation

Implements the plan using Test-Driven Development. Auto-uses parallel execution if plan detected isolated subtasks.

## Usage

```
/implement                  # Execute plan (uses mode from /plan)
/implement TASK-001         # Execute specific backlog task
/implement EPIC-001         # Execute all ready tasks in epic
/implement BUG-001          # Fix specific bug
/implement --sequential     # Force sequential even if parallel allowed
/implement --step 2         # Start from step 2 (sequential mode)
/implement --continue       # Continue from last checkpoint
```

## Agent Pipeline

### Strategy A: Fully Autonomous

```
Main Claude (Orchestrator) ~5% context
      |
      +-- Single subagent (opus)
              skills: [implementer, tdd, domain skills]
              --> Executes ALL tasks sequentially
              --> Full 200k context for implementation
              --> Reports only on completion or block
```

**When:** All tasks have `type="auto"`. No checkpoints needed.

### Strategy B: Segmented Execution

```
Main Claude (Orchestrator) ~20% context
      |
      +-- Subagent 1 (fresh context)
      |       --> Executes tasks until checkpoint
      |       --> Returns results to main
      |
      +-- [Main validates checkpoint with user]
      |
      +-- Subagent 2 (fresh context)
              --> Executes next segment
```

**When:** Has `checkpoint:human-verify` tasks.

### Parallel Mode

```
Main Claude (Orchestrator)
      |
      +-- SETUP WORKTREES (before spawning)
      |       codeagent worktree setup task-001
      |       codeagent worktree setup task-002
      |
      +-- implementer (Task A)
      |       working_dir: .worktrees/[branch]/task-001
      |       --> TDD loop for Task A
      |
      +-- implementer (Task B)
      |       working_dir: .worktrees/[branch]/task-002
      |       --> TDD loop for Task B
      |
      +-- (auto-triggers /integrate when complete)
```

## TDD Loop (Every Step)

```
1. Write test for the behavior
2. Run test --> MUST FAIL
3. Commit test
4. Write minimal implementation
5. Run test --> MUST PASS (max 3 attempts)
6. Commit implementation
7. Run full test suite --> check for regressions
8. Refactor if needed (tests must still pass)
9. Next step
```

## Expected Output

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
1. [approach] --> [error]
2. [approach] --> [error]
3. [approach] --> [error]

### Reflection Analysis
[From mcp__reflection__reflect_on_failure]

### Similar Past Issues
[From mcp__reflection__retrieve_episodes]

### Checkpoint Created
Branch: checkpoint/[task]-[timestamp]

### Options
1. /implement --continue (after manual fix)
2. /plan "alternative approach"
3. Ask for human help

### Needs
[Specific information or help needed]
```

## Deviation Handling

During implementation, handle unexpected situations:

| Rule | Condition | Action |
|------|-----------|--------|
| 1 | Bug discovered | Auto-fix, document |
| 2 | Missing security/validation | Auto-add, document |
| 3 | Blocker with clear fix | Auto-fix, document |
| 4 | Architectural change needed | STOP, ask user |
| 5 | Enhancement opportunity | Log to ISSUES.md |

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| task_id | No | Specific task/epic/bug ID |
| --sequential | No | Force sequential mode |
| --step N | No | Start from step N |
| --continue | No | Continue from checkpoint |

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Code | Working directory | Implemented features |
| Tests | Test directory | New tests |
| Commits | Git | Atomic commits |
| State | `.planning/STATE.md` | Progress tracking |
| Summary | `.planning/SUMMARY.md` | Completion summary |

## Failure Handling

The implementer uses reflection MCP on failures:

```yaml
mcp__reflection__reflect_on_failure:
  output: "[failed code]"
  feedback: "[error message]"

mcp__reflection__retrieve_episodes:
  task: "[current task]"
  error_pattern: "[error]"

# After 3 failures:
# --> Create checkpoint branch
# --> Output BLOCKED status
# --> Store episode in reflection
```

## Example

```bash
# Execute plan
/implement

# Work on specific task
/implement TASK-001

# Continue after fixing issue
/implement --continue

# Force sequential mode
/implement --sequential
```

## Notes

- Always run /plan before /implement
- Commits are automatic but push is NEVER automatic
- Use --continue to resume after fixing issues
- Parallel mode requires all tasks complete before /integrate
- Learner agent triggers automatically after success
