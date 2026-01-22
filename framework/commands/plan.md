---
description: Research, design, create epics/tasks, and auto-detect parallel execution potential
---

# /plan - Unified Planning

Gathers context, designs solution, creates backlog items (epics/tasks), and determines if parallel execution is beneficial.

## Usage

```text
/plan "Add JWT authentication"              # Standard planning
/plan "Add users and products"              # Auto-detects if parallelizable
/plan --sequential "Complex refactoring"    # Force sequential mode
/plan --deep "Investigate performance"      # Extra research phase
```

## Agent Pipeline

This command spawns three agents:

```text
Main Claude (Orchestrator)
      │
      ├─► researcher agent (opus)
      │       skills: [domain skills based on file types]
      │       → Queries A-MEM, codebase, context7
      │       → Returns: context summary, confidence score
      │
      ├─► architect agent (opus)
      │       skills: [spec-driven, relevant domain skills]
      │       → Uses ultrathink for structured exploration
      │       → Returns: 3+ approaches with evaluation
      │
      └─► orchestrator agent (opus)
              → Analyzes file/dependency conflicts
              → Returns: PARALLEL or SEQUENTIAL decision
```

## Process

### Phase 0: BDD - Behavior Definition

Before technical research, define business behaviors in Gherkin format:

```gherkin
Feature: [Feature Name]
  As a [role]
  I want [capability]
  So that [business value]

  Scenario: [Happy path scenario]
    Given [initial state]
    And [additional preconditions]
    When [action taken]
    Then [expected outcome]
    And [additional assertions]

  Scenario: [Error case scenario]
    Given [initial state]
    When [invalid action]
    Then [error handling]

  Scenario: [Edge case scenario]
    Given [edge condition]
    When [action]
    Then [expected behavior]
```

**BDD Rules:**

- Write scenarios BEFORE technical design
- Each scenario = one acceptance test
- Use domain language, not technical terms
- Cover happy path AND error cases
- Minimum 3 scenarios per feature

**Output:** Include scenarios in plan output:

```gherkin
### Behaviors (BDD)

Feature: User Authentication
  As a user
  I want to login with my credentials
  So that I can access protected resources

  Scenario: Successful login with valid credentials
    Given a registered user with email "user@example.com"
    And password "SecurePass123!"
    When they submit the login form
    Then they receive a valid JWT token
    And are redirected to the dashboard

  Scenario: Failed login with invalid password
    Given a registered user with email "user@example.com"
    When they submit with password "WrongPassword"
    Then they receive a 401 error
    And see "Invalid credentials" message
```

These scenarios flow to the architect agent for technical specification, then to the implementer as test cases.

### Phase 1: Research (researcher agent)

```markdown
Research Priority:
1. Query A-MEM for similar past implementations
2. Analyze codebase for patterns and conventions (Grep/Glob/Read)
3. Only if needed: Context7 for docs, external research

Output: Context summary with confidence score
```

### Phase 1.5: Model Selection

Query historical performance to determine suggested model for implementation:

```python
# Extract task keywords from research phase
task_keywords = extract_keywords(task_description)  # e.g., "auth", "database", "api"

# Query reflection for model effectiveness on similar tasks
effectiveness = mcp__reflection__get_model_effectiveness(
    task_pattern=task_keywords[0],  # Primary task domain
    feedback_type=None  # Or specific type if known from research
)

suggested_model = effectiveness["recommended_model"]
# Returns: "haiku" (default) or "opus" (if haiku historically fails)
```

**Selection Rules:**

| Condition                  | Model | Reason                                |
| -------------------------- | ----- | ------------------------------------- |
| No historical data         | haiku | Start cheap, escalate if needed       |
| Haiku success >= 50%       | haiku | Working well enough                   |
| Haiku success < 50% (n>=3) | opus  | Historical data shows struggles       |
| Complex arch task          | opus  | Needs full reasoning (override)       |

**Output Addition:**

Include model recommendation in plan output:

```markdown
### Suggested Model: [haiku|opus]
Confidence: [low|medium|high]
Reason: [from mcp__reflection__get_model_effectiveness]
```

### Phase 2: Design (architect agent)

```markdown
Structured Exploration (ultrathink):
1. Decompose into sub-problems
2. Generate 3+ approaches per sub-problem
3. Evaluate each: feasibility, risk, complexity
4. Select best path with documented rationale

Output: Architecture decision with explored alternatives
```

### Phase 3: Parallelization Analysis (orchestrator agent)

**Automatically runs if task has multiple subtasks.**

```markdown
Conflict Detection:
For each pair of subtasks (A, B):
  files_A = files modified by A
  files_B = files modified by B
  deps_A = dependencies of files_A
  deps_B = dependencies of files_B

  If (files_A ∩ files_B) ≠ ∅ → CONFLICT
  If (files_A ∩ deps_B) ≠ ∅ → CONFLICT
  If (deps_A ∩ files_B) ≠ ∅ → CONFLICT
  Else → PARALLELIZABLE
```

## Output Format

### Sequential Mode

```markdown
## Plan: [Task Name]

### Execution Mode: SEQUENTIAL
Reason: [single task / conflicts in X files / user requested]

### Research Summary
[From researcher agent - context gathered, confidence score]

### Architecture Decision
[From architect agent - chosen approach, alternatives explored]

### Implementation Steps
1. [ ] Step 1 - [description] - [files]
2. [ ] Step 2 - [description] - [files]
3. [ ] Step 3 - [description] - [files]

### Test Strategy
- Unit tests: [what to test]
- Integration tests: [what to test]
- Edge cases: [list]

### Risks
| Risk | Mitigation |
|------|------------|
| [risk] | [how to handle] |

### Confidence: X/10

Ready for /implement
```

### Parallel Mode

```markdown
## Plan: [Task Name]

### Execution Mode: PARALLEL
Reason: X independent subtasks, no file conflicts
Estimated speedup: Y%

### Research Summary
[From researcher agent]

### Architecture Decision
[From architect agent]

### Parallelization Analysis
[From orchestrator agent - isolation boundaries]

#### Task A: [name]
Exclusive files: [list - can modify]
Read-only: [list - can read only]
Forbidden: [list - don't touch]

#### Task B: [name]
Exclusive files: [list]
Read-only: [list]
Forbidden: [list]

### Shared Code (LOCKED - no task may modify)
- [files that are read-only for all tasks]

### Confidence: X/10

Ready for /implement (will auto-parallelize)
```

### XML Tasks Section (NEW)

After architecture decision, include XML task format from architect:

```markdown
## XML Tasks

<task type="auto|checkpoint:human-verify|checkpoint:decision">
  <name>[Task name]</name>
  <files>
    <exclusive>[Files to modify]</exclusive>
    <readonly>[Files to read]</readonly>
    <forbidden>[Files to avoid]</forbidden>
  </files>
  <action>[Specific instructions]</action>
  <verify>[Verification command/check]</verify>
  <done>
    - [ ] [Criterion 1]
    - [ ] [Criterion 2]
  </done>
</task>
```

Reference: `@~/.claude/framework/references/xml-task-format.md`

### Execution Strategy Section (NEW)

After parallelization analysis, include strategy from orchestrator:

```markdown
## Execution Strategy: [A|B|C]

**Reason:** [Based on checkpoint types in tasks]

| Strategy | When | Behavior |
|----------|------|----------|
| A | All auto | Single subagent, full plan |
| B | Has verify | Fresh subagent per segment |
| C | Has decision | Main context only |

### Checkpoint Analysis
| Task | Type | Impact |
|------|------|--------|
```

Reference: `@~/.claude/framework/references/execution-strategies.md`

## Mode Detection Rules

| Condition                          | Mode       | Reason                     |
| ---------------------------------- | ---------- | -------------------------- |
| Single subtask                     | SEQUENTIAL | Nothing to parallelize     |
| `--sequential` flag                | SEQUENTIAL | User forced                |
| Any file modified by 2+ subtasks   | SEQUENTIAL | Conflict risk              |
| Subtask A modifies B's dependency  | SEQUENTIAL | Dependency conflict        |
| Estimated speedup < 30%            | SEQUENTIAL | Overhead not worth it      |
| All subtasks fully isolated        | PARALLEL   | Safe to proceed            |

## A-MEM Integration

The planning pipeline uses A-MEM memory throughout:

**Researcher agent queries A-MEM for:**

- Past similar designs (avoids reinventing)
- Project-specific constraints and conventions
- Previous architecture decisions

**Architect agent stores:**

- New design decisions (with alternatives considered)
- Tradeoff analysis and rationale
- Implementation notes for future reference

**Orchestrator agent queries/stores:**

- Past parallelization decisions
- Known file conflict patterns

A-MEM automatically links related memories and evolves existing context.

## Context File Generation

After planning completes, generate context files in `.planning/` directory:

### Directory Structure

```text
.planning/
├── STATE.md       # Session state and progress tracking
├── PLAN.md        # Executable task definitions (XML format)
└── ISSUES.md      # Deferred enhancements (created during /implement)
```

### .planning/STATE.md

Generated from template: `@~/.claude/framework/templates/planning/STATE.md.template`

Contents:

- Session ID (timestamp-based)
- Current position (phase, task, status)
- Decisions table (empty, filled during /implement)
- Blockers table
- A-MEM/Reflection memory links

### .planning/PLAN.md

Generated from template: `@~/.claude/framework/templates/planning/PLAN.md.template`

Contents:

- Task name and metadata
- Execution mode (SEQUENTIAL/PARALLEL)
- Execution strategy (A/B/C)
- XML tasks from architect
- Deviation rules reference
- Verification steps

### Output Addition

Add to plan output:

```markdown
## Context Files Created

- `.planning/STATE.md` - Session state tracking (empty decisions table)
- `.planning/PLAN.md` - Executable XML task definitions

Ready for `/implement` with strategy [A|B|C]
```

## Backlog Integration (via backlog-mcp)

After planning completes, create tasks in Convex via backlog-mcp.
**Convex is the single source of truth** - no local YAML files.

### Project Setup (first time)

If project doesn't exist in Convex:

```python
mcp__backlog__create_project(
    name="MyProject",
    prefix="MP",
    description="Project description"
)
```

### Epic Creation (if scope is large)

```python
mcp__backlog__create_task(
    project="MP",
    task_type="epic",
    name="User Authentication System",
    action="Implement complete auth flow with JWT",
    priority=2,  # 1=critical, 2=high, 3=medium, 4=low
    description="From architect's architecture decision",
    done_criteria=[
        "All subtasks completed",
        "Integration tests pass"
    ]
)
# Returns: {id: "MP-EPIC-001", status: "ready"}
```

### Task Creation

```python
mcp__backlog__create_task(
    project="MP",
    task_type="task",
    name="Add JWT validation middleware",
    action="""
    1. Create AuthMiddleware implementing IMiddleware
    2. Use IAuthService.ValidateToken()
    3. Return 401/403 appropriately
    """,
    priority=2,
    files_exclusive=["src/Middleware/AuthMiddleware.cs"],
    files_readonly=["src/Services/IAuthService.cs"],
    files_forbidden=["src/Database/"],
    verify=["dotnet test --filter AuthMiddleware"],
    done_criteria=[
        "AuthMiddleware.cs created",
        "Middleware registered",
        "All tests pass"
    ],
    depends_on=[],  # Task IDs that must complete first
    parent_id="MP-EPIC-001",  # Link to parent epic
    execution_strategy="A",  # A (auto), B (human-verify), C (decision)
    checkpoint_type="auto",
    suggested_model=suggested_model  # FROM MODEL SELECTION PHASE (haiku/opus)
)
# Returns: {id: "MP-TASK-001", status: "ready", suggested_model: "haiku"}
```

**Note:** The `suggested_model` field is determined by Phase 1.5 and passed to implementation.

### Verify Creation

```python
mcp__backlog__get_backlog_summary(project="MP")
# Returns summary with counts and ready items
```

**Dashboard:** [http://localhost:6791](http://localhost:6791)

## Integration with /analyze

If `/analyze` was run first:

- Link epic to spike: `source.type: spike`, `source.ref: SPIKE-{N}`
- Import findings as context
- Reference spike output in epic description

## Notes

- Always run /scan before first /plan in a project
- /plan stores its output in memory for /implement to use
- Use `--deep` for complex investigative tasks
- If confidence < 7, the plan will recommend human review
- Architecture decisions are stored in A-MEM for future reference
- Context files are generated in `.planning/` directory
- Backlog items are created via backlog-mcp (Convex backend)
- Maximum 2-3 tasks per plan to prevent context degradation
- Dashboard at [http://localhost:6791](http://localhost:6791) for human backlog view
