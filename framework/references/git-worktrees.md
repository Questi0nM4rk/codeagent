# Git Worktrees for Parallel Execution

Specification for using git worktrees to enable parallel task execution without file conflicts.

## Overview

When executing tasks in parallel (Strategy B/C), each task gets its own git worktree. This prevents:
- File conflicts between parallel tasks
- Merge conflicts during integration
- Context degradation from mixed changes

```
Main Worktree (.)
├── src/
├── tests/
└── .codeagent/

Parallel Worktrees (.worktrees/)
└── qsm-ath-256-implement-auth/    # Grouped by parent branch (sanitized)
    ├── task-001/                   # Worktree for task 1
    │   ├── src/
    │   └── tests/
    └── task-002/                   # Worktree for task 2
        ├── src/
        └── tests/
```

## Naming Convention

| Component | Format | Example |
|-----------|--------|---------|
| Parent branch | `user/ticket-description` | `qsm/ath-256-implement-auth` |
| Sanitized name | Slashes → dashes | `qsm-ath-256-implement-auth` |
| Task branch | `<sanitized>--<task-id>` | `qsm-ath-256-implement-auth--task-001` |
| Worktree path | `.worktrees/<sanitized>/<task-id>` | `.worktrees/qsm-ath-256-implement-auth/task-001` |

**Note:** Task branches use double-dash (`--`) separator to avoid git ref conflicts with parent branch.

## Worktree Lifecycle

### Creation (before parallel task starts)

```bash
# Create branch for task
git branch task/TASK-001

# Create worktree in .worktrees/
git worktree add .worktrees/TASK-001 task/TASK-001

# Each task runs in its isolated worktree
cd .worktrees/TASK-001
# ... implementation happens here
```

### During Implementation

Each parallel implementer agent:
1. Works in its own worktree
2. Has isolated file system
3. Commits to its own branch
4. Cannot conflict with other tasks

### Completion (after task passes)

```bash
# In main worktree, merge task branch
git merge task/TASK-001

# Remove worktree
git worktree remove .worktrees/TASK-001

# Optionally delete branch
git branch -d task/TASK-001
```

### Failure/Blocked (checkpoint)

```bash
# Keep worktree for later continuation
# Branch preserved as checkpoint/TASK-001

# To resume later:
cd .worktrees/TASK-001
# ... continue work
```

## Utility Commands

All worktree operations use the `codeagent worktree` utility. This is internal plumbing - you don't run these manually.

### Setup Worktree

```bash
# Called by /implement before spawning parallel agents
codeagent worktree setup task-001

# Returns JSON:
# {"worktree": ".worktrees/qsm-ath-256-implement-auth/task-001",
#  "branch": "qsm-ath-256-implement-auth--task-001",
#  "status": "created"}
```

### Cleanup Worktree

```bash
# Remove worktree and delete branch
codeagent worktree cleanup task-001

# Keep branch (for debugging)
codeagent worktree cleanup task-001 keep-branch
```

### Merge and Cleanup

```bash
# Called by /integrate after all tasks complete
codeagent worktree merge task-001

# Merges branch to parent with --no-ff, then cleans up
```

### List Active Worktrees

```bash
codeagent worktree list
codeagent worktree status  # More detailed output
```

## Integration with /implement

### Sequential Mode (Strategy A)

No worktrees needed. All work in main worktree.

### Parallel Mode (Strategy B/C)

```
/implement (orchestrator detects parallel-safe)
     │
     ├─► SETUP PHASE (before spawning):
     │       codeagent worktree setup task-001
     │       codeagent worktree setup task-002
     │       → Store paths in STATE.md
     │
     ├─► For each parallel task:
     │       Spawn implementer agent with:
     │          - working_dir: .worktrees/<sanitized>/task-XXX
     │          - branch: <sanitized>--task-XXX
     │       Agent works in isolation (worktree pre-created)
     │
     ├─► Wait for all parallel tasks
     │
     └─► /integrate phase:
             codeagent worktree merge task-001
             codeagent worktree merge task-002
             → Run integration tests
             → Worktrees cleaned up automatically
```

**Key point:** Implementer agents do NOT create worktrees. They receive `working_dir` pre-created.

## Agent Working Directory

When an implementer agent spawns for parallel execution:

```python
# Agent receives worktree path
working_dir = ".worktrees/TASK-001"

# All file operations are relative to worktree
Edit(file_path=f"{working_dir}/src/Auth/AuthService.cs", ...)
Read(file_path=f"{working_dir}/src/Auth/AuthService.cs")
Bash(command=f"cd {working_dir} && dotnet test")
```

## File Boundaries

Even with worktrees, respect file boundaries from orchestrator:

```yaml
# TASK-001 can only touch:
implementation:
  files:
    exclusive:
      - src/Auth/AuthService.cs
    readonly:
      - src/Interfaces/IAuthService.cs
    forbidden:
      - src/Database/  # Even in own worktree
```

The worktree isolates file system, but boundaries prevent logical conflicts.

## Conflict Detection

Before merging:

```bash
# Check for conflicts
git merge-tree "$(git merge-base main task/TASK-001)" main task/TASK-001

# If conflicts detected:
# 1. Flag for manual resolution
# 2. Keep worktrees until resolved
```

## .gitignore

Add to project .gitignore:

```
# Git worktrees for parallel execution
.worktrees/
```

## Status Tracking

### In TASK-XXX.yaml

```yaml
execution:
  worktree: .worktrees/qsm-ath-256-implement-auth/task-001
  branch: qsm-ath-256-implement-auth--task-001
  parent_branch: qsm/ath-256-implement-auth
  started_at: "2026-01-10T15:00:00Z"
  commits:
    - "abc123: test(auth): add validation tests"
    - "def456: feat(auth): implement validation"
```

### In STATE.md (parallel execution)

```yaml
parallel_execution:
  parent_branch: qsm/ath-256-implement-auth
  active_worktrees:
    - task_id: task-001
      worktree: .worktrees/qsm-ath-256-implement-auth/task-001
      branch: qsm-ath-256-implement-auth--task-001
      status: in_progress
    - task_id: task-002
      worktree: .worktrees/qsm-ath-256-implement-auth/task-002
      branch: qsm-ath-256-implement-auth--task-002
      status: in_progress
```

## Recovery

### After Crash

```bash
# List dangling worktrees
git worktree list

# Prune stale worktrees
git worktree prune

# Resume work in existing worktree
cd .worktrees/TASK-001
git status
```

### Manual Cleanup

```bash
# List what needs cleanup
codeagent worktree list

# Clean up specific task
codeagent worktree cleanup task-001

# Nuclear option - remove all worktrees
rm -rf .worktrees/
git worktree prune

# Delete orphaned branches (careful!)
git branch | grep -E "^  .*/task-" | xargs git branch -D
```

## Best Practices

1. **Use the utility** - Always use `codeagent worktree` instead of raw git commands
2. **Don't create manually** - Let /implement handle worktree creation
3. **Check before merge** - Utility checks for conflicts automatically
4. **Keep worktrees on blocked tasks** - Allows easy continuation
5. **Clean up after successful merge** - /integrate handles this automatically
6. **Track worktrees in STATE.md** - Know what's active
7. **Respect file boundaries** - Worktrees isolate, but boundaries prevent logical conflicts
8. **Branch inheritance** - Task branches are created from current HEAD, not main
