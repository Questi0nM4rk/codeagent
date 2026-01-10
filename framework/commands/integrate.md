---
description: Integrate parallel work and validate consistency (auto-triggers after parallel /implement)
---

# /integrate - Parallel Integration

Validates and integrates work from parallel implementation. Auto-triggers when /implement completes in PARALLEL mode.

## Usage

```
/integrate              # Usually auto-triggered
/integrate --verbose    # Detailed output
/integrate --skip-tests # Skip test run (not recommended)
```

## What This Does

1. Verifies no merge conflicts (should be none if isolation was correct)
2. Runs full test suite across all changes
3. Validates interface contracts between tasks
4. Checks pattern consistency across parallel implementations
5. Verifies no orphaned or circular dependencies

## Process

### Step 1: Merge Validation

Should be conflict-free since files were isolated:

```bash
git status
git diff --stat
```

If conflicts exist → isolation analysis was wrong → manual resolution needed.

### Step 2: Full Test Suite

Run ALL tests, not just new ones:

```bash
# .NET
dotnet test --verbosity normal

# Rust
cargo test

# C/C++
ctest --test-dir build --output-on-failure

# Lua
busted
```

### Step 3: Interface Contract Validation

Check that parallel implementations agree on:
- Shared interface signatures
- DTO structures
- Database schema assumptions
- API contracts

Verify using Grep/Read:
- Do all implementations of IUserService match the interface?
- Are all DTOs used consistently?
- Any type mismatches across boundaries?

### Step 4: Pattern Consistency Check

Query Letta:
- Does Task A's code follow same patterns as Task B?
- Any style drift between parallel implementations?
- Naming conventions consistent?

### Step 5: Dependency Verification

Check using Grep/Read:
- Any circular dependencies introduced?
- Any orphaned code (written but not called)?
- Any missing implementations (interface methods)?

### Step 6: Security Scan

```bash
semgrep --config auto --error .
```

## Output Format

```markdown
## Integration Results

### Merge Status
| Metric | Value |
|--------|-------|
| Conflicts | None ✓ |
| Files changed | 24 |
| Lines added | +847 |
| Lines removed | -12 |

### Test Results
| Metric | Value |
|--------|-------|
| Total tests | 156 |
| Passed | 156 ✓ |
| Failed | 0 |
| Skipped | 0 |
| Coverage | 84% |

### Contract Validation
| Check | Status |
|-------|--------|
| Interface consistency | ✓ PASS |
| DTO consistency | ✓ PASS |
| Schema consistency | ✓ PASS |

### Pattern Consistency
| Check | Status | Notes |
|-------|--------|-------|
| Naming conventions | ✓ PASS | |
| Error handling | ⚠ WARN | Task B uses exceptions, Task A uses Result<T> |
| Logging style | ✓ PASS | |

### Dependency Check
| Check | Status |
|-------|--------|
| Circular dependencies | None ✓ |
| Orphaned code | None ✓ |
| Missing implementations | None ✓ |

### Security
| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

---

## VERDICT: ✅ INTEGRATION SUCCESSFUL

### Warnings (non-blocking)
1. Pattern drift in error handling - consider standardizing

Ready for /review
```

## Failure Handling

### Test Failures

```markdown
## INTEGRATION FAILED: Test failures

### Failing Tests
| Test | Error | Likely Cause |
|------|-------|--------------|
| UserServiceTests.Create | Expected Result.Failure, got exception | Contract mismatch |

### Root Cause Analysis
Task A expects ValidationException, shared code returns Result.Failure

### Resolution Options
1. Update Task A to use Result<T> pattern (matches project standard)
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

### Pattern Drift

```markdown
## INTEGRATION WARNING: Pattern drift

### Details
Error handling inconsistency:

| Task | Pattern | Files |
|------|---------|-------|
| Task A | Result<T> monad | 3 files |
| Task B | Exceptions | 4 files |
| Project standard | Result<T> | (from CLAUDE.md) |

### Recommendation
Refactor Task B to use Result<T>
Priority: MEDIUM (code works but inconsistent)

### Action Required
- [ ] Refactor Task B error handling
- [ ] Re-run /review after refactor
```

## Notes

- /integrate auto-runs after parallel /implement
- If integration fails, individual tasks may need adjustment
- Pattern drift warnings are non-blocking but should be addressed
- Always run /review after successful /integrate
