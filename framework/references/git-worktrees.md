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
├── TASK-001/          # Worktree for task 1
│   ├── src/
│   └── tests/
└── TASK-002/          # Worktree for task 2
    ├── src/
    └── tests/
```

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

## Commands

### Setup Worktree for Task

```bash
# Implementer runs before starting parallel task
setup_worktree() {
    local task_id="$1"
    local base_branch="${2:-main}"

    # Ensure .worktrees directory exists
    mkdir -p .worktrees

    # Create task branch from base
    git branch "task/$task_id" "$base_branch" 2>/dev/null || true

    # Create worktree
    git worktree add ".worktrees/$task_id" "task/$task_id"

    echo ".worktrees/$task_id"
}
```

### Cleanup Worktree

```bash
cleanup_worktree() {
    local task_id="$1"
    local delete_branch="${2:-true}"

    # Remove worktree
    git worktree remove ".worktrees/$task_id" --force 2>/dev/null || true

    # Optionally delete branch
    if [ "$delete_branch" = "true" ]; then
        git branch -D "task/$task_id" 2>/dev/null || true
    fi
}
```

### Merge Task to Main

```bash
merge_task() {
    local task_id="$1"

    # Ensure we're in main worktree
    cd "$(git rev-parse --show-toplevel)"

    # Merge task branch
    git merge "task/$task_id" --no-ff -m "Merge $task_id"

    # Cleanup
    cleanup_worktree "$task_id"
}
```

## Integration with /implement

### Sequential Mode (Strategy A)

No worktrees needed. All work in main worktree.

### Parallel Mode (Strategy B/C)

```
/implement (orchestrator detects parallel-safe)
     │
     ├─► For each parallel task:
     │       1. Create worktree: .worktrees/TASK-XXX/
     │       2. Spawn implementer agent with:
     │          - working_dir: .worktrees/TASK-XXX/
     │          - branch: task/TASK-XXX
     │       3. Agent works in isolation
     │
     ├─► Wait for all parallel tasks
     │
     └─► /integrate phase:
             1. Merge each task/TASK-XXX to main
             2. Run integration tests
             3. Cleanup worktrees
```

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
  worktree: .worktrees/TASK-001
  branch: task/TASK-001
  started_at: "2026-01-10T15:00:00Z"
  commits:
    - "abc123: test(auth): add validation tests"
    - "def456: feat(auth): implement validation"
```

### In .codeagent/sessions/current.yaml

```yaml
parallel_execution:
  active_worktrees:
    - task_id: TASK-001
      worktree: .worktrees/TASK-001
      branch: task/TASK-001
      status: in_progress
    - task_id: TASK-002
      worktree: .worktrees/TASK-002
      branch: task/TASK-002
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
# Remove all parallel worktrees
rm -rf .worktrees/

# Prune git's worktree registry
git worktree prune

# Delete orphaned task branches
git branch | grep "task/" | xargs git branch -D
```

## Best Practices

1. **Always create worktree before parallel execution** - Don't work in main for parallel tasks
2. **Use --force for cleanup** - Worktrees may have uncommitted changes on failure
3. **Check for conflicts before merge** - Use merge-tree to preview
4. **Keep worktrees on blocked tasks** - Allows easy continuation
5. **Clean up after successful merge** - Don't let worktrees accumulate
6. **Track worktrees in session** - Know what's active
7. **Respect file boundaries** - Worktrees isolate, boundaries prevent logical conflicts
