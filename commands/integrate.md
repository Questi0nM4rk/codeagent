---
name: integrate
description: Merge parallel work streams and validate consistency
---

# /integrate - Parallel Integration

Validates and integrates work from parallel implementation. Auto-triggers after parallel /implement completes.

## Usage

```
/integrate              # Usually auto-triggered
/integrate --verbose    # Detailed output
/integrate --skip-tests # Skip test run (not recommended)
```

## What This Does

1. Merges worktree branches into parent branch
2. Runs full test suite across all changes
3. Validates interface contracts between tasks
4. Checks pattern consistency across implementations
5. Verifies no orphaned or circular dependencies
6. Runs security scan

## Process

### Step 0: Worktree Merge and Cleanup

```bash
# For each parallel worktree:
codeagent worktree merge task-001
codeagent worktree merge task-002
```

On success:
- Task branch merged with `--no-ff`
- Worktree directory removed
- Task branch deleted

On merge conflict:
- Merge aborted
- Worktree preserved
- Error reported with conflict details

### Step 1: Merge Validation

Should be conflict-free since files were isolated:

```bash
git status
git diff --stat
```

If conflicts exist, isolation analysis was wrong.

### Step 2: Full Test Suite

Run ALL tests, not just new ones:

```bash
# .NET
dotnet test --verbosity normal

# Rust
cargo test

# TypeScript
npm test

# Python
pytest
```

### Step 3: Interface Contract Validation

Check that parallel implementations agree on:
- Shared interface signatures
- DTO structures
- Database schema assumptions
- API contracts

### Step 4: Pattern Consistency Check

Query A-MEM:
- Does Task A's code follow same patterns as Task B?
- Any style drift between parallel implementations?
- Naming conventions consistent?

### Step 5: Dependency Verification

Check:
- Any circular dependencies introduced?
- Any orphaned code (written but not called)?
- Any missing implementations (interface methods)?

### Step 6: Security Scan

```bash
semgrep --config auto --error .
```

## Expected Output

### Success

```markdown
## Integration Results

### Merge Status
| Metric | Value |
|--------|-------|
| Conflicts | None |
| Files changed | 24 |
| Lines added | +847 |
| Lines removed | -12 |

### Test Results
| Metric | Value |
|--------|-------|
| Total tests | 156 |
| Passed | 156 |
| Failed | 0 |
| Skipped | 0 |
| Coverage | 84% |

### Contract Validation
| Check | Status |
|-------|--------|
| Interface consistency | PASS |
| DTO consistency | PASS |
| Schema consistency | PASS |

### Pattern Consistency
| Check | Status | Notes |
|-------|--------|-------|
| Naming conventions | PASS | |
| Error handling | WARN | Task B uses exceptions, Task A uses Result<T> |
| Logging style | PASS | |

### Dependency Check
| Check | Status |
|-------|--------|
| Circular dependencies | None |
| Orphaned code | None |
| Missing implementations | None |

### Security
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

---

## VERDICT: INTEGRATION SUCCESSFUL

### Warnings (non-blocking)
1. Pattern drift in error handling - consider standardizing

Ready for /review
```

### Test Failure

```markdown
## INTEGRATION FAILED: Test failures

### Failing Tests
| Test | Error | Likely Cause |
|------|-------|--------------|
| UserServiceTests.Create | Expected Result.Failure | Contract mismatch |

### Root Cause Analysis
Task A expects ValidationException, shared code returns Result.Failure

### Resolution Options
1. Update Task A to use Result<T> pattern
2. Update shared validation to throw exceptions
3. Add adapter in Task A

### Recommendation
Option 1 - matches established project patterns
```

### Contract Mismatch

```markdown
## INTEGRATION FAILED: Contract mismatch

### Mismatch Details
Interface: IUserService.CreateUser

| Implementation | Signature |
|----------------|-----------|
| Shared interface | Task<Result<UserDTO>> CreateUser(CreateUserRequest) |
| Task A impl | Task<UserDTO> CreateUser(CreateUserRequest) |

### Resolution
Task A must update return type to match interface
```

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| --verbose | No | Detailed output |
| --skip-tests | No | Skip test run (not recommended) |

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Merged code | Main branch | Integrated changes |
| Report | Console | Integration results |

## Worktree Behavior

| Scenario | Worktree Action |
|----------|-----------------|
| All tests pass | Worktrees merged and cleaned |
| Merge conflict | Worktree preserved for manual fix |
| Test failure | Worktrees NOT cleaned (debug) |
| Pattern drift warning | Worktrees cleaned (non-blocking) |

Manual cleanup after debugging:
```bash
codeagent worktree cleanup task-001
codeagent worktree cleanup task-002
```

## Example

```bash
# Usually auto-triggered after parallel /implement
/integrate

# With verbose output
/integrate --verbose
```

## Notes

- /integrate auto-runs after parallel /implement
- If integration fails, individual tasks may need adjustment
- Pattern drift warnings are non-blocking but should be addressed
- Always run /review after successful /integrate
