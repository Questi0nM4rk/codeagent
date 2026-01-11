# Deviation Rules Reference

Rules for handling unexpected situations during implementation.

## The Five Rules

| Rule | Condition | Action | Document In | Priority |
|------|-----------|--------|-------------|----------|
| **1** | Bug discovered during implementation | Auto-fix | STATE.md | High |
| **2** | Missing security/validation check | Auto-add | STATE.md | High |
| **3** | Blocker with clear fix | Auto-fix | STATE.md | High |
| **4** | Architectural change needed | **STOP** | Ask user | Critical |
| **5** | Enhancement opportunity | Log only | ISSUES.md | Low |

**Priority Order:** Rule 4 (stop) > Rules 1-3 (auto-fix) > Rule 5 (log)

---

## Rule 1: Auto-Fix Bugs

**Condition:** Bug discovered that blocks current task or affects correctness.

**Action:** Fix immediately, document in STATE.md.

**Examples:**
- Null reference in code you're modifying
- Off-by-one error in loop
- Missing null check
- Incorrect type casting

**Documentation:**
```markdown
## Deviations
| Time | Type | Issue | Action |
|------|------|-------|--------|
| 14:32 | bug | Null check missing in UserService.GetById | Added guard clause |
```

---

## Rule 2: Auto-Add Security/Validation

**Condition:** Security gap or missing validation that could cause issues.

**Action:** Add immediately, document in STATE.md.

**Examples:**
- SQL injection vulnerability
- Missing input validation
- Exposed sensitive data in logs
- Missing authentication check
- CORS misconfiguration

**Documentation:**
```markdown
## Deviations
| Time | Type | Issue | Action |
|------|------|-------|--------|
| 14:45 | security | SQL injection risk in search query | Parameterized query |
| 14:52 | validation | Email format not validated | Added regex validation |
```

---

## Rule 3: Auto-Fix Blockers

**Condition:** Issue blocks task completion but has clear fix.

**Action:** Fix to unblock, document in STATE.md.

**Examples:**
- Missing dependency import
- Incorrect method signature
- File not found (needs creation)
- Configuration missing

**Documentation:**
```markdown
## Deviations
| Time | Type | Issue | Action |
|------|------|-------|--------|
| 15:01 | blocker | DbContext not registered in DI | Added registration in Program.cs |
```

---

## Rule 4: STOP for Architectural Changes

**Condition:** Implementation requires changes that affect system design.

**Action:** STOP immediately. Ask user before proceeding.

**Examples:**
- Need to change database schema significantly
- Proposed pattern conflicts with existing architecture
- Requires modifying shared interfaces
- Scope creep beyond original task
- Changes affect multiple unrelated systems

**User Prompt Format:**
```markdown
## Architectural Decision Required

**Task:** [current task]

**Issue:** [what was discovered]

**Options:**
1. [Option A] - [tradeoffs]
2. [Option B] - [tradeoffs]
3. [Abandon task] - [implications]

**My recommendation:** [option] because [rationale]

Please choose an option to proceed.
```

---

## Rule 5: Log Enhancements

**Condition:** Opportunity for improvement not in scope.

**Action:** Log to ISSUES.md, continue with original task.

**Examples:**
- Could refactor for better performance
- Could add additional test cases
- Could improve error messages
- Could add logging/monitoring
- Could optimize database queries

**ISSUES.md Format:**
```markdown
# Issues Log

## Enhancements (Not in Scope)
| ID | Enhancement | Discovered During | Priority |
|----|-------------|-------------------|----------|
| ENH-001 | UserService could use caching | Add user auth | Medium |
| ENH-002 | Error messages could be more descriptive | Add validation | Low |

## Technical Debt
| ID | Debt | Location | Effort |
|----|------|----------|--------|
| TD-001 | Duplicate validation logic | UserController, AdminController | 2h |
```

---

## Decision Flow

```
Unexpected situation discovered
          │
          ▼
    Is it a bug?  ───Yes───► Rule 1: Auto-fix, document
          │
          No
          ▼
    Is it security/  ───Yes───► Rule 2: Auto-add, document
    validation gap?
          │
          No
          ▼
    Does it block  ───Yes───► Rule 3: Auto-fix, document
    the task?
          │
          No
          ▼
    Does it require  ───Yes───► Rule 4: STOP, ask user
    architectural
    changes?
          │
          No
          ▼
    Rule 5: Log to ISSUES.md, continue
```

---

## STATE.md Deviation Section

After implementation, STATE.md should contain all deviations:

```markdown
## Deviations During Implementation

### Auto-Fixed (Rules 1-3)
| Time | Type | Issue | Action | Files |
|------|------|-------|--------|-------|
| 14:32 | bug | Null check missing | Added guard clause | UserService.cs |
| 14:45 | security | SQL injection | Parameterized query | SearchRepo.cs |
| 15:01 | blocker | Missing DI registration | Added to Program.cs | Program.cs |

### Decisions Made (Rule 4)
| Time | Issue | Options | Selected | Rationale |
|------|-------|---------|----------|-----------|
| 15:30 | Schema change needed | A: Migrate, B: Workaround | A | Long-term maintainability |

### Deferred (Rule 5)
See ISSUES.md for logged enhancements.
```

---

## Integration with Reflection MCP

When applying deviation rules, store learning episodes:

```python
# After auto-fix (Rules 1-3)
mcp__reflection__store_episode(
    task="[current task]",
    approach="deviation: auto-fix [type]",
    outcome="success",
    feedback="[what was fixed]",
    feedback_type="deviation_autofix",
    reflection={
        "deviation_type": "bug|security|blocker",
        "original_issue": "[description]",
        "fix_applied": "[action taken]",
        "general_lesson": "[pattern to remember]"
    }
)

# After STOP decision (Rule 4)
mcp__reflection__store_episode(
    task="[current task]",
    approach="deviation: architectural decision",
    outcome="pending_decision",
    feedback="[issue requiring decision]",
    feedback_type="deviation_stop",
    reflection={
        "deviation_type": "architectural",
        "options_presented": "[list]",
        "user_decision": "[selected option]",
        "general_lesson": "[when this pattern applies]"
    }
)
```
