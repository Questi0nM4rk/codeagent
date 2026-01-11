# Task Formats Reference

YAML specifications for CodeAgent backlog items: Epics, Tasks, Bugs, and Research.

## File Locations

```
.codeagent/backlog/
├── epics/      EPIC-001.yaml, EPIC-002.yaml, ...
├── tasks/      TASK-001.yaml, TASK-002.yaml, ...
├── bugs/       BUG-001.yaml, BUG-002.yaml, ...
└── research/   RES-001.yaml, RES-002.yaml, ...
```

## ID Format

IDs use project prefix from `.codeagent/config.yaml`:

```
{PREFIX}-{TYPE_ABBREV}{NUMBER}

Examples:
- MP-EPIC-001  (MyProject Epic 1)
- MP-TASK-001  (MyProject Task 1)
- MP-BUG-001   (MyProject Bug 1)
- MP-RES-001   (MyProject Research 1)
```

Shorthand form (for CLI): `EPIC-001`, `TASK-001`, `BUG-001`, `RES-001`

---

## Epic Format

Epics are high-level features that contain multiple tasks.

**File:** `.codeagent/backlog/epics/EPIC-001.yaml`

```yaml
# Required fields
id: EPIC-001
type: epic
name: "User Authentication System"
description: |
  Implement complete authentication flow including:
  - JWT token generation and validation
  - Refresh token rotation
  - User registration and login

created: "2026-01-10T14:30:00Z"
updated: "2026-01-10T14:30:00Z"
status: ready  # backlog, ready, in_progress, done

# Priority and effort
priority: high  # critical, high, medium, low
estimated_effort: "2d"  # Duration estimate (optional)

# Labels for filtering
labels:
  - security
  - auth
  - mvp

# Source tracking
source:
  type: research  # user_request, research, bug_report, /plan
  ref: RES-001    # Reference to source item (optional)
  request: "Add auth to the API"  # Original user request (optional)

# Task relationships
tasks:
  - TASK-001
  - TASK-002
  - TASK-003

# Epic dependencies
dependencies: []  # Other epics that must complete first
blocks: []        # Other epics waiting on this one

# Progress tracking (auto-calculated)
progress:
  total_tasks: 3
  completed: 0
  percentage: 0

# Context for implementers
context:
  # Files to read for understanding
  files_to_reference:
    - src/Middleware/
    - src/Services/IAuthService.cs

  # Patterns to follow
  patterns_to_follow:
    - "Use IAuthService for all token operations"
    - "Follow existing middleware pattern"

  # Constraints to respect
  constraints:
    - "Must support both access and refresh tokens"
    - "Tokens must be rotatable without logout"

# Knowledge links
knowledge:
  amem_ids: []           # A-MEM memory IDs
  research_refs:
    - RES-001

# Completion (filled when done)
completed_at: null
summary: null
```

---

## Task Format

Tasks are implementation units derived from epics.

**File:** `.codeagent/backlog/tasks/TASK-001.yaml`

```yaml
# Required fields
id: TASK-001
type: task
name: "Add JWT validation middleware"
description: |
  Create middleware that validates JWT tokens on protected routes.
  Return 401 for invalid tokens, 403 for insufficient permissions.

created: "2026-01-10T14:35:00Z"
updated: "2026-01-10T14:35:00Z"
status: ready  # backlog, ready, in_progress, blocked, done

# Parent epic
epic: EPIC-001

# Task dependencies
depends_on: []     # Tasks that must complete first
blocks:            # Tasks waiting on this one
  - TASK-002

# Implementation details (from architect)
implementation:
  # File boundaries for parallel execution
  files:
    exclusive:       # Only this task modifies
      - src/Middleware/AuthMiddleware.cs
      - tests/Middleware/AuthMiddlewareTests.cs
    readonly:        # This task reads only
      - src/Services/IAuthService.cs
    forbidden:       # Must not touch
      - src/Database/

  # Specific instructions
  action: |
    1. Create AuthMiddleware class implementing IMiddleware
    2. Use IAuthService.ValidateToken() - NOT manual JWT parsing
    3. Return 401 for invalid tokens, 403 for insufficient permissions
    4. Register in pipeline AFTER UseRouting, BEFORE UseAuthorization

    Avoid: JwtSecurityTokenHandler (deprecated) - use JsonWebTokenHandler

  # Verification steps
  verify:
    - command: "dotnet test --filter AuthMiddleware"
      expected: "pass"
    - check: "curl -H 'Authorization: Bearer invalid' /api/users returns 401"

  # Acceptance criteria
  done:
    - "AuthMiddleware.cs created with IMiddleware interface"
    - "Middleware registered in correct pipeline position"
    - "Unauthorized requests return 401"
    - "Insufficient permission requests return 403"
    - "All existing tests pass"

# Execution metadata
execution:
  strategy: A           # A (auto), B (human-verify), C (decision)
  checkpoint_type: null # null, human-verify, decision, human-action
  estimated_duration: "30m"

# Blocker info (if blocked)
blocker:
  reason: null
  since: null
  needs: null

# Completion (filled when done)
completed_at: null
summary: null

# Learning (filled by learner agent)
lessons_learned: []
patterns_used: []
commits: []
```

---

## Bug Format

Bugs are defects discovered during implementation or testing.

**File:** `.codeagent/backlog/bugs/BUG-001.yaml`

```yaml
# Required fields
id: BUG-001
type: bug
name: "Login returns 500 on empty password"
description: |
  When user submits login with empty password, API returns 500
  instead of 400 validation error.

created: "2026-01-10T15:00:00Z"
updated: "2026-01-10T15:00:00Z"
status: ready  # backlog, ready, in_progress, done

# Severity and priority
severity: medium  # critical, high, medium, low
priority: high    # Can differ from severity based on impact

# Reproducibility
reproducible: always  # always, sometimes, rare, unknown

# Reproduction steps
reproduction:
  steps:
    - "POST /api/auth/login with { email: 'test@test.com', password: '' }"
    - "Observe response"
  expected: "400 Bad Request with validation message"
  actual: "500 Internal Server Error"
  environment: "Development, .NET 10"

# Affected code
affected_files:
  - src/Controllers/AuthController.cs
  - src/Services/AuthService.cs

# Root cause analysis
root_cause: |
  AuthService.Login() doesn't validate empty password before
  attempting hash comparison, causing NullReferenceException.

# Fix approach
fix:
  action: |
    1. Add validation in AuthController before calling service
    2. Return 400 with "Password is required" message
    3. Add unit test for empty password case

  verify:
    - "POST with empty password returns 400"
    - "POST with valid credentials still works"
    - "Existing login tests pass"

  done:
    - "Validation added to AuthController"
    - "Test added for empty password"
    - "All existing tests pass"

# Relationships
related_epic: EPIC-001
related_tasks:
  - TASK-002
discovered_during: TASK-002  # Task where bug was found

# Source
source:
  type: test_failure  # test_failure, user_report, review, manual
  details: "Failed during /implement TASK-002"

# Completion
completed_at: null
summary: null
commits: []
```

---

## Research Format

Research items are investigations that may derive tasks.

**File:** `.codeagent/backlog/research/RES-001.yaml`

```yaml
# Required fields
id: RES-001
type: research
name: "Authentication patterns for .NET 10"
question: |
  What authentication approach should we use?
  - JWT vs session cookies?
  - Token storage best practices?
  - Refresh token rotation?

created: "2026-01-10T14:00:00Z"
updated: "2026-01-10T14:30:00Z"
status: done  # backlog, in_progress, done

# Research scope
scope:
  - "Compare JWT vs session-based auth for API"
  - "Investigate refresh token best practices"
  - "Review .NET 10 authentication changes"

# Sources to check
sources_checked:
  - type: amem
    query: "authentication patterns .NET"
    found: true
  - type: codebase
    query: "existing auth implementation"
    found: false
  - type: context7
    library: "Microsoft.AspNetCore.Authentication.JwtBearer"
    found: true
  - type: web
    query: "OWASP JWT security best practices"
    found: true

# Research output
output:
  file: "RES-001-output.md"  # Detailed findings in knowledge/outputs/
  summary: |
    Recommendation: JWT with refresh token rotation.
    - Use JsonWebTokenHandler (not JwtSecurityTokenHandler)
    - Store refresh tokens in HttpOnly cookies
    - Implement sliding expiration for refresh tokens

# Confidence in findings
confidence: 9  # 1-10

# Derived work items (auto-created)
derived_items:
  - type: epic
    id: EPIC-001
    description: "User Authentication System"
  - type: task
    id: TASK-001
    description: "Add JWT middleware"

# Knowledge stored
knowledge_refs:
  amem_ids:
    - "mem_auth_001"
  project_md_section: "## Authentication"

completed_at: "2026-01-10T14:30:00Z"
```

---

## Status Values

| Status | Meaning | Valid For |
|--------|---------|-----------|
| `backlog` | Not ready for work | All |
| `ready` | Dependencies met, can start | Epic, Task, Bug |
| `in_progress` | Currently being worked on | All |
| `blocked` | Waiting on something | Task |
| `done` | Completed | All |

See `task-states.md` for state transitions.

---

## Priority Values

| Priority | Meaning |
|----------|---------|
| `critical` | Must be done immediately, blocks everything |
| `high` | Important, do soon |
| `medium` | Normal priority |
| `low` | Nice to have, do when time permits |

---

## Naming Conventions

**Epics:** Noun phrase describing the feature
- "User Authentication System"
- "Product Catalog Management"
- "Real-time Notifications"

**Tasks:** Imperative verb phrase describing the action
- "Add JWT validation middleware"
- "Implement login endpoint"
- "Create user registration form"

**Bugs:** Description of the symptom
- "Login returns 500 on empty password"
- "Search results not paginated"
- "Memory leak in WebSocket handler"

**Research:** Question or topic to investigate
- "Authentication patterns for .NET 10"
- "Caching strategy comparison"
- "Performance profiling results"
