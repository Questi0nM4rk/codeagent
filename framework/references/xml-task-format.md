# XML Task Format Reference

Structured task specification for Claude Code planning and execution.

## Task Structure

```xml
<task type="auto|checkpoint:decision|checkpoint:human-verify|checkpoint:human-action">
  <name>Imperative task name (e.g., "Add JWT validation middleware")</name>
  <files>
    <exclusive>Files this task modifies (can write)</exclusive>
    <readonly>Files task reads but doesn't modify</readonly>
    <forbidden>Files task must never touch</forbidden>
  </files>
  <action>
    1. What to do (specific, not vague)
    2. How to do it (patterns, conventions to follow)
    3. What to avoid and WHY (prevent common mistakes)
  </action>
  <verify>
    Concrete verification command or check:
    - Command: `dotnet test --filter "TestName"`
    - File check: Verify file X contains pattern Y
    - API check: Request returns expected response
  </verify>
  <done>
    - [ ] Acceptance criterion 1 (measurable)
    - [ ] Acceptance criterion 2 (testable)
    - [ ] No regressions in existing tests
  </done>
</task>
```

## Task Types

| Type | Usage | Frequency | Behavior |
|------|-------|-----------|----------|
| `auto` | No user input needed | ~50% | Execute autonomously |
| `checkpoint:human-verify` | Verification after automation | ~40% | Pause for user confirmation |
| `checkpoint:decision` | Choice between options | ~9% | Present options, await selection |
| `checkpoint:human-action` | Manual step required | ~1% | Guide user through action |

### Type: auto

Fully autonomous execution. No stoppage needed.

```xml
<task type="auto">
  <name>Add unit tests for UserService</name>
  <files>
    <exclusive>src/Tests/UserServiceTests.cs</exclusive>
    <readonly>src/Services/UserService.cs</readonly>
  </files>
  <action>
    Write unit tests covering:
    1. CreateUser - valid input returns success
    2. CreateUser - duplicate email returns error
    3. GetUser - existing user returns data
    4. GetUser - missing user returns null
  </action>
  <verify>`dotnet test --filter "UserServiceTests"` passes</verify>
  <done>
    - [ ] 4 test methods created
    - [ ] All tests pass
    - [ ] No existing tests broken
  </done>
</task>
```

### Type: checkpoint:human-verify

Automation complete, needs user verification before proceeding.

```xml
<task type="checkpoint:human-verify">
  <name>Configure OAuth provider</name>
  <files>
    <exclusive>src/Config/AuthConfig.cs, appsettings.json</exclusive>
  </files>
  <action>
    1. Add OAuth configuration section
    2. Set up redirect URIs
    3. Configure scopes
  </action>
  <verify>
    User verifies:
    1. OAuth flow works in browser
    2. Correct scopes granted
    3. Token refresh works
  </verify>
  <done>
    - [ ] User confirms OAuth flow works
    - [ ] No security warnings in browser
  </done>
</task>
```

### Type: checkpoint:decision

Requires user to choose between options.

```xml
<task type="checkpoint:decision">
  <name>Select caching strategy</name>
  <files>
    <readonly>src/Services/*.cs</readonly>
  </files>
  <action>
    Analyze caching requirements and present options.
  </action>
  <verify>User selects preferred option</verify>
  <done>
    - [ ] Decision recorded in STATE.md
    - [ ] Implementation proceeds with selected option
  </done>
  <options>
    <option id="redis">
      <name>Redis Cache</name>
      <pros>Distributed, persistent, fast</pros>
      <cons>External dependency, operational overhead</cons>
    </option>
    <option id="memory">
      <name>In-Memory Cache</name>
      <pros>No external deps, simple</pros>
      <cons>Not shared across instances, lost on restart</cons>
    </option>
  </options>
</task>
```

### Type: checkpoint:human-action

Truly unavoidable manual step (use sparingly).

```xml
<task type="checkpoint:human-action">
  <name>Generate API key in third-party dashboard</name>
  <files>
    <exclusive>.env</exclusive>
  </files>
  <action>
    I automated: Created .env template with placeholder

    Need your help with:
    1. Go to https://dashboard.provider.com/api-keys
    2. Click "Generate New Key"
    3. Copy the key value

    Then provide the key and I'll add it to .env
  </action>
  <verify>API key added to .env and validated</verify>
  <done>
    - [ ] API key obtained
    - [ ] Key added to .env
    - [ ] Test API call succeeds
  </done>
</task>
```

## File Boundaries

The `<files>` section enforces isolation for parallel execution:

| Boundary | Meaning | Violation Action |
|----------|---------|------------------|
| `<exclusive>` | Task owns these files, can modify freely | None (allowed) |
| `<readonly>` | Task can read but NOT modify | STOP, report conflict |
| `<forbidden>` | Task must not access at all | STOP, report violation |

## Best Practices

### Action Section

**Good:**
```xml
<action>
  1. Create AuthMiddleware class in src/Middleware/
  2. Use IAuthService.ValidateToken() - NOT manual JWT parsing
  3. Return 401 for invalid tokens, 403 for insufficient permissions
  4. Add to pipeline AFTER routing, BEFORE authorization

  Avoid: Don't use deprecated JwtSecurityTokenHandler (use JsonWebTokenHandler)
</action>
```

**Bad:**
```xml
<action>
  Add authentication middleware to the application.
</action>
```

### Verify Section

**Good:**
```xml
<verify>
  1. `curl -H "Authorization: Bearer invalid" /api/users` returns 401
  2. `curl -H "Authorization: Bearer valid" /api/users` returns 200
  3. All existing tests pass: `dotnet test`
</verify>
```

**Bad:**
```xml
<verify>Test the middleware works</verify>
```

### Done Section

**Good:**
```xml
<done>
  - [ ] AuthMiddleware.cs exists in src/Middleware/
  - [ ] Middleware registered in Program.cs
  - [ ] Unauthorized requests return 401
  - [ ] No regressions in AuthTests
</done>
```

**Bad:**
```xml
<done>
  - [ ] Authentication works
</done>
```

## Task Limit

**Maximum 2-3 tasks per plan.** Research shows context quality degrades after 3 tasks.

If more tasks needed:
1. Complete current plan with `/implement`
2. Generate next plan with `/plan`
3. Chain plans via ROADMAP.md phases
