---
description: Execute plan/backlog using TDD (auto-detects parallel from plan)
---

# /implement - TDD Implementation

Implements the plan or backlog task using Test-Driven Development. Automatically uses parallel execution if the plan detected isolated subtasks.

## Usage

```text
/implement                  # Execute plan (uses mode from /plan)
/implement TASK-001         # Execute specific backlog task
/implement EPIC-001         # Execute all ready tasks in epic
/implement BUG-001          # Fix specific bug
/implement --sequential     # Force sequential even if plan allows parallel
/implement --step 2         # Start from step 2 (sequential mode)
/implement --continue       # Continue from last checkpoint
/implement --task=A         # Re-run specific parallel task
```

## Backlog Integration (via backlog-mcp)

### Task Selection Priority

When running `/implement` without arguments:

1. Continue from `.planning/STATE.md` if exists
2. Call `mcp__backlog__get_next_task()` for highest-priority ready task
3. If no ready tasks, report backlog status

### Picking from Backlog

```python
# Get next ready task with FULL context (single-task loading)
result = mcp__backlog__get_next_task(project="MP")

if result["found"]:
    task = result["task"]
    # task contains:
    #   - files_exclusive, files_readonly, files_forbidden
    #   - action (what to do)
    #   - verify (how to verify)
    #   - done_criteria (completion checklist)

    # Mark as in_progress
    mcp__backlog__update_task_status(
        task_id=task["id"],
        status="in_progress"
    )
else:
    # No ready tasks
    mcp__backlog__get_backlog_summary(project="MP")
```

### Task Context Loading

When starting a task, full context is returned by `get_next_task()`:

```python
task = {
    "id": "MP-TASK-001",
    "name": "Add JWT validation middleware",
    "type": "task",
    "status": "ready",
    "priority": 2,

    # Implementation boundaries (CRITICAL for parallel execution)
    "files_exclusive": ["src/Middleware/AuthMiddleware.cs"],
    "files_readonly": ["src/Services/IAuthService.cs"],
    "files_forbidden": ["src/Database/"],

    # Instructions
    "action": "1. Create AuthMiddleware...",
    "verify": ["dotnet test --filter AuthMiddleware"],
    "done_criteria": ["AuthMiddleware.cs created", ...],

    # Dependencies
    "depends_on": [],
    "blocks": ["MP-TASK-002"],
    "parent_id": "MP-EPIC-001",

    # Execution
    "execution_strategy": "A",
    "checkpoint_type": "auto"
}
```

## Agent Pipeline

### Execution by Strategy

Reference: `@~/.claude/framework/references/execution-strategies.md`

#### Strategy A: Fully Autonomous

```text
Main Claude (Orchestrator) ~5% context
      │
      └─► Single subagent (suggested_model → opus)
              skills: [tdd, domain skills]
              → Executes ALL tasks sequentially
              → Full 200k context for implementation
              → Escalates to opus on repeated failures
              → REITERATES if opus fails
              → Reports only on completion or block
```

**When:** All tasks have `type="auto"`. No checkpoints needed.

#### Strategy B: Segmented Execution (Fresh Subagent Per Task)

```text
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

```text
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

```text
Main Claude (Orchestrator)
      │
      ├─► SETUP WORKTREES (before spawning agents)
      │       codeagent worktree setup task-001
      │       codeagent worktree setup task-002
      │       → Store paths in STATE.md
      │
      ├─► implementer agent (Task A) - Strategy A only
      │       working_dir: .worktrees/<sanitized>/task-001
      │       branch: <sanitized>--task-001
      │       skills: [tdd, relevant domain skills]
      │       exclusive files: [list]
      │       → TDD loop for Task A
      │
      ├─► implementer agent (Task B) - Strategy A only
      │       working_dir: .worktrees/<sanitized>/task-002
      │       branch: <sanitized>--task-002
      │       skills: [tdd, relevant domain skills]
      │       exclusive files: [list]
      │       → TDD loop for Task B
      │
      └─► (auto-triggers /integrate when all complete)
```

**Note:** Parallel tasks MUST be `type="auto"`. Tasks with checkpoints cannot be parallelized.

### Parallel Worktree Setup (before spawning agents)

When PARALLEL mode is detected:

1. **For each parallel task:**

```bash
result=$(codeagent worktree setup "$TASK_ID")
worktree_path=$(echo "$result" | jq -r '.worktree')
task_branch=$(echo "$result" | jq -r '.branch')
```

1. **Store in STATE.md:**

```yaml
parallel_execution:
  parent_branch: qsm/ath-256-implement-auth
  active_worktrees:
    - task_id: task-001
      worktree: .worktrees/qsm-ath-256-implement-auth/task-001
      branch: qsm-ath-256-implement-auth--task-001
      status: pending
    - task_id: task-002
      worktree: .worktrees/qsm-ath-256-implement-auth/task-002
      branch: qsm-ath-256-implement-auth--task-002
      status: pending
```

1. **Spawn implementer with pre-created paths:**

```text
working_dir: $worktree_path
branch: $task_branch
file_boundaries: [from orchestrator]
```

**Important:** Implementer agents receive `working_dir` already created. They do NOT run worktree commands themselves.

## Model Selection

The `/plan` phase determines `suggested_model` based on historical performance data.

### At Implementation Time

1. **Load task** with `suggested_model` from backlog
2. **Use suggested model** (default: haiku if not set)
3. **Escalate to opus** if suggested model fails 3x
4. **Reiterate planning** if opus fails 3x

### Escalation Flow

```text
suggested_model (from /plan)
    │
    ├─► Attempt 1-3: Use suggested_model
    │       Success → Done
    │       Failure → Escalate
    │
    ├─► Attempt 4-6: Use opus
    │       Success → Done (store lesson: "opus needed for this type")
    │       Failure → Reiterate
    │
    └─► REITERATE: Return to /plan with failure context
            → Re-analyze approach
            → May need different architecture
            → May need human guidance
```

**No sonnet tier.** Either haiku works (cheap/fast) or opus is needed (full reasoning). The /plan phase decides this upfront using historical data.

### Model Usage by Phase

| Phase          | Model            | Rationale                                    |
| -------------- | ---------------- | -------------------------------------------- |
| Test writing   | opus             | Correctness critical - tests define contract |
| Implementation | suggested_model  | From task, based on historical data          |

### Reflection-Guided Retry

Before each retry attempt, check for lessons from past failures:

```python
for attempt in 1..6:  # Max 6 attempts (3 suggested + 3 opus)
    # Query past failures for THIS type of problem
    episodes = mcp__reflection__retrieve_episodes(
        task=current_task,
        error_pattern=last_error
    )

    if episodes:
        # Apply lessons learned
        guidance = mcp__reflection__generate_improved_attempt(
            original_output=failed_code,
            reflection=reflection_result,
            similar_episodes=episodes
        )

    current_model = suggested_model if attempt <= 3 else "opus"
    result = spawn_impl_agent(prompt, model=current_model)

    if result.success:
        if lesson_applied:
            mcp__reflection__mark_lesson_effective(episode_id, True)
        if attempt > 3:
            # Store lesson: opus was needed for this task type
            mcp__reflection__store_episode(
                task=current_task,
                outcome="success",
                model_used="opus",
                reflection={"lesson": "opus needed for this task pattern"}
            )
        break

    # Store failure for future learning
    mcp__reflection__store_episode(
        task=current_task,
        outcome="failure",
        model_used=current_model,
        feedback=error_message,
        feedback_type=error_type
    )

# If all 6 attempts failed → REITERATE
if not result.success:
    return REITERATE(task, failure_summary)
```

### Reiteration Protocol

When opus fails 3x, return to planning:

```markdown
## REITERATE: Implementation Failed

### Task: [task name]
### Suggested Model: [model from plan]
### Escalated To: opus

### Failure Summary
- Attempt 1 ([suggested]): [error]
- Attempt 2 ([suggested]): [error]
- Attempt 3 ([suggested]): [error]
- Attempt 4 (opus): [error]
- Attempt 5 (opus): [error]
- Attempt 6 (opus): [error]

### Reflection Analysis
[From mcp__reflection__reflect_on_failure]

### Recommended Action
1. Re-run /plan with this context
2. Consider different architectural approach
3. May need human guidance for [specific issue]

Run: /plan "[task]" --context="REITERATE: [summary]"
```

## TDD Loop (Every Step)

```text
1. Write test for the behavior (opus - correctness critical)
2. Run test → MUST FAIL
3. Commit test
4. Write minimal implementation (suggested_model from task)
5. Run test → MUST PASS (max 3 attempts, then escalate to opus)
6. Commit implementation
7. Run full test suite → check for regressions
8. Refactor if needed (tests must still pass)
9. Next step
```

**Note:** Test writing always uses opus for correctness. Implementation uses suggested_model (from /plan's historical analysis), escalating to opus if needed.

## Deviation Handling

Reference: `@~/.claude/framework/references/deviation-rules.md`

During implementation, handle unexpected situations with these rules:

### The Five Rules

| Rule | Condition                        | Action      | Document In |
| ---- | -------------------------------- | ----------- | ----------- |
| 1    | Bug discovered                   | Auto-fix    | STATE.md    |
| 2    | Missing security/validation      | Auto-add    | STATE.md    |
| 3    | Blocker with clear fix           | Auto-fix    | STATE.md    |
| 4    | Architectural change needed      | STOP        | Ask user    |
| 5    | Enhancement opportunity          | Log only    | ISSUES.md   |

**Priority:** Rule 4 (stop) > Rules 1-3 (auto-fix) > Rule 5 (log)

### Auto-Fix Examples (Rules 1-3)

```markdown
## Deviations in STATE.md

| Time  | Type      | Issue                  | Action                   | Files          |
| ----- | --------- | ---------------------- | ------------------------ | -------------- |
| 14:32 | bug       | Null check missing     | Added guard clause       | UserService.cs |
| 14:45 | security  | SQL injection risk     | Parameterized query      | SearchRepo.cs  |
| 15:01 | blocker   | Missing DI registration| Added to Program.cs      | Program.cs     |
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

| ID      | Enhancement                    | Discovered During | Priority |
| ------- | ------------------------------ | ----------------- | -------- |
| ENH-001 | UserService could use caching  | Add user auth     | Medium   |
```

## Failure Handling

The implementer agent uses reflection MCP on failures:

```text
mcp__reflection__reflect_on_failure
    → Analyze what went wrong
    → Check similar past failures
    → Generate improved attempt

After 6 failures (3 suggested + 3 opus):
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

### Reiterate (All Attempts Failed)

```markdown
## REITERATE: Implementation Failed After 6 Attempts

### Task: [task name]
### Suggested Model: [from plan]

### Attempt History
| # | Model | Error Type | Error |
|---|-------|------------|-------|
| 1 | [suggested] | [type] | [error] |
| 2 | [suggested] | [type] | [error] |
| 3 | [suggested] | [type] | [error] |
| 4 | opus | [type] | [error] |
| 5 | opus | [type] | [error] |
| 6 | opus | [type] | [error] |

### Reflection Analysis
[From mcp__reflection__reflect_on_failure]

### Similar Past Issues
[From mcp__reflection__retrieve_episodes]

### Root Cause Analysis
[Combined insights from reflection]

### Checkpoint Created
Branch: checkpoint/[task]-[timestamp]

### Recommended Actions
1. **Re-plan**: `/plan "[task]" --context="REITERATE: [summary]"`
2. **Manual fix**: Fix issue, then `/implement --continue`
3. **Human guidance**: [Specific question or decision needed]

### What Went Wrong
[Summary of why all 6 attempts failed - likely architectural issue]
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

```text
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

```text
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

### 4. Update Backlog (via backlog-mcp)

**Complete task and unblock dependents:**

```python
result = mcp__backlog__complete_task(
    task_id="MP-TASK-001",
    summary="Added AuthMiddleware using JsonWebTokenHandler for JWT validation.",
    commits=[
        "abc123: test(auth): add tests for JWT validation",
        "def456: feat(auth): implement JWT validation"
    ]
)

# result = {
#   "completed": True,
#   "id": "MP-TASK-001",
#   "unblocked": ["MP-TASK-002"]  # Tasks now ready
# }
```

**Automatic behaviors:**

- Task status → `done`
- `completed_at` timestamp set
- Dependent tasks with all deps done → status `ready`
- Dashboard updates automatically at [http://localhost:6791](http://localhost:6791)

### 5. Update PROJECT.md

Add task summary to `.codeagent/knowledge/PROJECT.md`:

```markdown
## Recent Completions

### TASK-001: Add JWT middleware (2026-01-10)
Added AuthMiddleware using JsonWebTokenHandler for token validation.
Positioned after UseRouting, before UseAuthorization.

- Files: AuthMiddleware.cs (+120 lines)
- Tests: 5 tests, 100% coverage
- See: TASK-001-summary.md

## Key Decisions

| Date | Decision | Rationale | Task |
|------|----------|-----------|------|
| 2026-01-10 | JsonWebTokenHandler | JwtSecurityTokenHandler deprecated | TASK-001 |
```

### 6. Generate Task Summary

**File:** `.codeagent/knowledge/summaries/TASK-XXX-summary.md`

```markdown
# Task Summary: TASK-XXX

**Name:** [task name]
**Epic:** EPIC-XXX
**Completed:** [timestamp]

## What Was Done

[Detailed description of implementation]

## Files Modified

| File | Action | Lines |
|------|--------|-------|
| src/Middleware/AuthMiddleware.cs | Created | +120 |
| Program.cs | Modified | +5 |

## Tests Added

| Test | Description |
|------|-------------|
| ValidToken_ReturnsOk | Validates JWT with valid token |
| ExpiredToken_Returns401 | Rejects expired tokens |

## Commits

- abc123: test(auth): add tests for JWT validation
- def456: feat(auth): implement JWT validation

## Patterns Used

- Middleware pattern for request interception
- IAuthService for token operations

## Deviations

[Any auto-fixes from Rules 1-3]

## Lessons Learned

[Captured for future reference]
```

### 7. Clean Up

- Archive `.planning/PLAN.md` to `.planning/history/[timestamp]-PLAN.md`
- Keep STATE.md for session continuity
- ISSUES.md persists for future reference

## Failure Handling with Backlog

When implementation fails after 6 attempts (3 suggested + 3 opus):

### Option 1: Create Bug

If user confirms, create bug item via backlog-mcp:

```python
mcp__backlog__create_task(
    project="MP",
    task_type="bug",
    name="[description of failure]",
    action="""
    Root cause: [from reflection analysis]

    Reproduction:
    1. [what was attempted]

    Expected: [expected behavior]
    Actual: [actual error]

    Previous attempts:
    1. [approach 1] → [error 1]
    2. [approach 2] → [error 2]
    3. [approach 3] → [error 3]
    """,
    priority=2,  # Bugs typically high priority
    files_exclusive=[],  # TBD during fix
    verify=["Test that proves bug is fixed"],
    done_criteria=["Bug no longer reproduces", "Tests pass"]
)
```

### Option 2: Block Task

Mark task as blocked via backlog-mcp:

```python
mcp__backlog__update_task_status(
    task_id="MP-TASK-001",
    status="blocked",
    blocker_reason="[from reflection analysis]",
    blocker_needs="[what help is needed]"
)
```

Then create checkpoint branch:

```bash
git checkout -b checkpoint/MP-TASK-001-$(date +%s)
git add -A && git commit -m "checkpoint: blocked on [reason]"
```

## Notes

- Always run /plan before /implement
- /implement uses backlog-mcp to get task context (single-task loading)
- Commits are automatic but push is NEVER automatic
- Use --continue to resume after fixing issues
- Parallel mode requires all tasks to complete before /integrate
- Learner agent triggers automatically after successful implementation
- Dashboard at [http://localhost:6791](http://localhost:6791) shows backlog in real-time
