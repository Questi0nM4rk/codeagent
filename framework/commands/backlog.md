---
description: View and manage project backlog
---

# /backlog - Backlog Management

View and manage project backlog. Shows epics, tasks, bugs, and spike items with their statuses.

## Usage

```
/backlog                    # View backlog summary
/backlog ready              # View ready items
/backlog in-progress        # View items in progress
/backlog blocked            # View blocked items
/backlog EPIC-001           # View specific epic with tasks
/backlog TASK-001           # View specific task details
/backlog next               # Get recommended next item
/backlog groom              # AI-assisted backlog grooming
```

## Output Format

### Summary View (`/backlog`)

```markdown
## [Project Name] Backlog

### Summary

| Type     | Backlog | Ready | In Progress | Blocked | Done |
|----------|---------|-------|-------------|---------|------|
| Epics    | 1       | 2     | 1           | -       | 3    |
| Tasks    | 5       | 8     | 2           | 1       | 15   |
| Bugs     | 0       | 2     | 0           | -       | 5    |
| Spikes   | 1       | -     | 1           | -       | 4    |

### In Progress

- **TASK-015**: Add user profile endpoint [EPIC-002]
- **TASK-016**: Implement pagination [EPIC-003]
- **SPIKE-006**: Caching strategy investigation

### Ready (Priority Order)

1. **BUG-006**: Fix null reference in search [critical]
2. **TASK-017**: Add search to users endpoint [EPIC-002]
3. **TASK-018**: Add filtering to products [EPIC-003]

### Blocked

- **TASK-014**: Integrate payment gateway
  Blocked since: 2026-01-10
  Needs: API credentials from vendor

### Recommended Next

**BUG-006** - Critical bug should be fixed first.
Run: `/implement BUG-006`
```

### Ready View (`/backlog ready`)

```markdown
## Ready Items

### Bugs (fix first)

| ID | Name | Severity | Related |
|----|------|----------|---------|
| BUG-006 | Fix null reference in search | critical | TASK-012 |
| BUG-007 | Pagination off by one | medium | EPIC-003 |

### Tasks

| ID | Name | Epic | Priority |
|----|------|------|----------|
| TASK-017 | Add search to users endpoint | EPIC-002 | high |
| TASK-018 | Add filtering to products | EPIC-003 | medium |
| TASK-019 | Add sorting options | EPIC-003 | low |

### Commands

- `/implement BUG-006` - Fix critical bug first
- `/implement TASK-017` - Start next task
- `/backlog TASK-017` - View task details
```

### Epic View (`/backlog EPIC-001`)

```markdown
## Epic: EPIC-001 - User Authentication System

**Status:** in_progress
**Priority:** high
**Progress:** 2/3 tasks (67%)

### Description

Implement complete authentication flow including:
- JWT token generation and validation
- Refresh token rotation
- User registration and login

### Tasks

| ID | Name | Status | Depends On |
|----|------|--------|------------|
| TASK-001 | Add JWT middleware | done | - |
| TASK-002 | Implement login endpoint | done | TASK-001 |
| TASK-003 | Add refresh token | ready | TASK-002 |

### Context

**Files to reference:**
- src/Middleware/
- src/Services/IAuthService.cs

**Patterns to follow:**
- Use IAuthService for all token operations
- Follow existing middleware pattern

### Source

- Type: spike
- Ref: SPIKE-001

### Commands

- `/implement TASK-003` - Complete this epic
- `/backlog TASK-003` - View task details
```

### Task View (`/backlog TASK-001`)

```markdown
## Task: TASK-001 - Add JWT validation middleware

**Status:** done
**Epic:** EPIC-001 - User Authentication System
**Completed:** 2026-01-10T17:30:00Z

### Description

Create middleware that validates JWT tokens on protected routes.
Return 401 for invalid tokens, 403 for insufficient permissions.

### Implementation

**Files:**
- Exclusive: src/Middleware/AuthMiddleware.cs
- Readonly: src/Services/IAuthService.cs
- Forbidden: src/Database/

**Action:**
1. Create AuthMiddleware class implementing IMiddleware
2. Use IAuthService.ValidateToken()
3. Return 401/403 appropriately

**Verify:**
- dotnet test --filter AuthMiddleware

**Done criteria:**
- [x] AuthMiddleware.cs created
- [x] Middleware registered
- [x] All tests pass

### Summary

Added AuthMiddleware using JsonWebTokenHandler for JWT validation.
Positioned after UseRouting, before UseAuthorization.

### Commits

- abc123: test(auth): add tests for JWT validation
- def456: feat(auth): implement JWT validation middleware

### Dependencies

**Depends on:** (none)
**Blocks:** TASK-002

### Related

- Epic: EPIC-001
- Research: SPIKE-001
```

### Blocked View (`/backlog blocked`)

```markdown
## Blocked Items

### TASK-014: Integrate payment gateway

**Blocked since:** 2026-01-10T14:00:00Z
**Epic:** EPIC-004

**Reason:**
Cannot proceed without API credentials from payment vendor.

**Needs:**
- API key from vendor
- Sandbox environment access
- Documentation URL

**Actions:**
1. Contact vendor for credentials
2. Once received, run `/implement TASK-014 --continue`

---

### No other blocked items
```

### Next View (`/backlog next`)

```markdown
## Recommended Next

### BUG-006: Fix null reference in search

**Why this item:**
1. Critical severity bug
2. Affects user-facing search feature
3. No dependencies
4. Quick fix estimated

**Quick info:**
- Severity: critical
- Related: TASK-012
- Root cause: Missing null check in SearchService

**Command:**
```
/implement BUG-006
```

### Alternative

If bug requires more context:
- **TASK-017**: Add search to users endpoint [ready, high priority]
```

### Groom View (`/backlog groom`)

AI-assisted backlog grooming:

```markdown
## Backlog Grooming

### Issues Found

1. **Stale items** (no activity > 7 days)
   - TASK-005: Add logging (backlog since 2026-01-03)
   - SPIKE-002: Investigate caching (in_progress since 2026-01-02)

2. **Missing dependencies**
   - TASK-020 depends on TASK-019 but TASK-019 not created

3. **Orphaned tasks**
   - TASK-021: No linked epic

4. **Duplicate spike**
   - SPIKE-003 and SPIKE-007 both investigate "caching"

### Recommendations

1. **Deprioritize or close stale items**
   - TASK-005: Still relevant? Move to backlog or close
   - SPIKE-002: Complete spike or mark done

2. **Create missing items**
   - TASK-019: [suggested name based on TASK-020 dependency]

3. **Link orphaned tasks**
   - TASK-021: Should link to EPIC-003 based on file patterns

4. **Consolidate spike**
   - Merge SPIKE-007 findings into SPIKE-003

### Actions

- `/backlog close TASK-005` - Mark as deprecated
- `/plan "create TASK-019"` - Create missing dependency
```

## Filters

| Filter | Shows |
|--------|-------|
| `ready` | Items ready for work |
| `in-progress` | Currently active items |
| `blocked` | Items waiting on something |
| `done` | Completed items (last 10) |
| `bugs` | All bugs |
| `spike` | All spike items |
| `high` | High/critical priority items |

## Item References

View any item by ID:

```
/backlog EPIC-001    # Epic details
/backlog TASK-001    # Task details
/backlog BUG-001     # Bug details
/backlog SPIKE-001     # Research details
```

## Management Commands

### Update Status

```
/backlog TASK-001 --status ready       # Move to ready
/backlog TASK-001 --status blocked     # Mark blocked
/backlog TASK-001 --status backlog     # Deprioritize
```

### Add Notes

```
/backlog TASK-001 --note "Waiting on API docs"
```

### Link Items

```
/backlog TASK-001 --blocks TASK-002
/backlog TASK-001 --depends-on TASK-000
```

## CLI Alternative

For quick backlog view from terminal:

```bash
codeagent backlog              # Summary
codeagent backlog --ready      # Ready items only
```

## Notes

- Backlog is read from `.codeagent/backlog/` YAML files
- BACKLOG.md is auto-generated, don't edit manually
- Use `/implement` to work on items, not `/backlog`
- Priority order: critical bugs > high bugs > high tasks > medium > low
- Blocked items need manual resolution before continuing
