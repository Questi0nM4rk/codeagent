# Execution Strategies Reference

Three strategies for executing plans based on checkpoint types.

## Strategy Overview

| Strategy | When                             | Behavior                                  | Main Context Usage          |
| -------- | -------------------------------- | ----------------------------------------- | --------------------------- |
| A        | All tasks `type="auto"`          | Single subagent executes entire plan      | ~5% (orchestration only)    |
| B        | Has `checkpoint:human-verify`    | Fresh subagent per segment                | ~20% (checkpoints only)     |
| C        | Has `checkpoint:decision`        | Main context only, no subagents           | 100%                        |

---

## Strategy A: Fully Autonomous

### When to Use

- All tasks have `type="auto"`
- No user verification needed
- No decisions required during execution

### Behavior

```text
Main Claude (Orchestrator)
      │
      └─► Single subagent (suggested_model → opus)
              → Executes ALL tasks sequentially
              → Full 200k context for implementation
              → Uses suggested_model from task (set by /plan)
              → Escalates to opus on repeated failures
              → REITERATES to /plan if opus fails
              → Reports only on completion or block
```

### Model Selection

The `/plan` phase determines `suggested_model` based on historical performance data:

- Queries `mcp__reflection__get_model_effectiveness()` for similar tasks
- Default: `haiku` (if no historical data)
- Upgrades to `opus` if haiku historically fails on similar tasks

**Escalation:** suggested_model (3 attempts) → opus (3 attempts) → REITERATE to /plan

### Token Distribution

- Main context: ~5% (spawn subagent, receive results)
- Subagent: ~95% (actual implementation)

### Example Plan

```xml
<task type="auto">
  <name>Add unit tests for AuthService</name>
  ...
</task>

<task type="auto">
  <name>Add integration tests for auth endpoints</name>
  ...
</task>

<task type="auto">
  <name>Update API documentation</name>
  ...
</task>
```

**Execution:** Single subagent runs all three tasks.

---

## Strategy B: Segmented Execution

### When to Use

- At least one task has `checkpoint:human-verify`
- No `checkpoint:decision` tasks (those require Strategy C)

### Behavior

```text
Main Claude (Orchestrator)
      │
      ├─► Subagent 1 (fresh context)
      │       → Executes tasks until checkpoint
      │       → Reports back with results
      │
      ├─► [Main validates checkpoint with user]
      │
      ├─► Subagent 2 (fresh context)
      │       → Executes next segment
      │       → Reports back with results
      │
      └─► [Continue until all complete]
```

### Token Distribution

- Main context: ~20% (checkpoints, user interaction)
- Subagents: ~80% (implementation, split across segments)

### Fresh Subagent Benefits

1. **Full context per segment** - 200k tokens available
2. **No degradation** - Each subagent starts clean
3. **Isolated failures** - One segment failing doesn't pollute others

### Example Plan

```xml
<task type="auto">
  <name>Implement OAuth flow</name>
  ...
</task>

<task type="checkpoint:human-verify">
  <name>Configure OAuth provider</name>
  <verify>User tests OAuth in browser</verify>
  ...
</task>

<task type="auto">
  <name>Add token refresh logic</name>
  ...
</task>
```

**Execution:**

1. Subagent 1: Executes "Implement OAuth flow"
2. Subagent 1: Executes "Configure OAuth provider"
3. **Checkpoint:** Main context asks user to verify OAuth
4. Subagent 2 (fresh): Executes "Add token refresh logic"

### Subagent Prompt Template

```markdown
## Subagent: ${SEGMENT_NAME}

You are executing ONE segment of a larger plan.
This is a FRESH context - previous segments are complete.

### Your Tasks
${TASK_XML_FOR_SEGMENT}

### Context Files
Read these for background:
- .planning/STATE.md - Current project state
- .planning/PLAN.md - Full plan context

### Deviation Rules
@~/.claude/framework/references/deviation-rules.md

### File Boundaries
EXCLUSIVE (can modify): ${EXCLUSIVE_FILES}
READONLY (read only): ${READONLY_FILES}
FORBIDDEN (don't touch): ${FORBIDDEN_FILES}

### On Completion
1. Update .planning/STATE.md with progress
2. Report results to main context
3. STOP - do not start next segment
```

---

## Strategy C: Main Context Only

### When to Use

- Any task has `checkpoint:decision`
- Decision outcomes affect subsequent tasks
- Tight user interaction required

### Behavior

```text
Main Claude (no subagents)
      │
      ├─► Execute Task 1 (auto)
      │
      ├─► Hit checkpoint:decision
      │       → Present options to user
      │       → User selects option
      │       → Record in STATE.md
      │
      ├─► Execute Task 2 (depends on decision)
      │
      └─► Continue until complete
```

### Token Distribution

- Main context: 100% (no subagents)

### When Preferred Despite Token Cost

- Decisions fundamentally change subsequent tasks
- Quick back-and-forth with user expected
- Tasks are small enough that subagent overhead > benefit

### Example Plan

```xml
<task type="auto">
  <name>Analyze caching requirements</name>
  ...
</task>

<task type="checkpoint:decision">
  <name>Select caching strategy</name>
  <options>
    <option id="redis">Redis Cache</option>
    <option id="memory">In-Memory Cache</option>
  </options>
  ...
</task>

<task type="auto">
  <name>Implement selected caching strategy</name>
  ...
</task>
```

**Execution:** All in main context because Task 3 depends on Task 2's decision.

---

## Strategy Selection Algorithm

```python
def select_strategy(tasks):
    has_decision = any(t.type == "checkpoint:decision" for t in tasks)
    has_verify = any(t.type == "checkpoint:human-verify" for t in tasks)

    if has_decision:
        return "C"  # Decisions require main context
    elif has_verify:
        return "B"  # Segment at verify checkpoints
    else:
        return "A"  # Fully autonomous
```

**Decision Matrix:**

| Has Decision? | Has Verify? | Strategy |
| ------------- | ----------- | -------- |
| Yes           | Any         | C        |
| No            | Yes         | B        |
| No            | No          | A        |

---

## Strategy Selection Output

Add to plan output:

```markdown
## Execution Strategy: [A|B|C]

**Reason:** [explanation]

### Checkpoint Analysis
| Task | Type | Strategy Impact |
|------|------|-----------------|
| Add auth middleware | auto | - |
| Configure OAuth | checkpoint:human-verify | Triggers B |
| Add token refresh | auto | - |

### Token Distribution
- Main context: ~20%
- Subagents: ~80% (2 segments)

### Segment Boundaries
1. **Segment 1:** Tasks 1-2 (until OAuth verify)
2. **Segment 2:** Task 3 (after user verification)
```

---

## Integration with Parallel Mode

Strategy selection happens AFTER parallelization analysis:

```text
/plan
  │
  ├─► Parallelization Analysis (orchestrator)
  │       → Determines: SEQUENTIAL or PARALLEL
  │       → If PARALLEL: defines task boundaries
  │
  └─► Strategy Selection
          → For SEQUENTIAL: Select A, B, or C
          → For PARALLEL: Each parallel task uses Strategy A
                          (parallel tasks must be fully autonomous)
```

**Rule:** Parallel tasks MUST be `type="auto"`. If a task needs checkpoints, it cannot be parallelized.

---

## Fallback Rules

| Situation                 | Fallback                        |
| ------------------------- | ------------------------------- |
| Fails 3x with suggested   | Escalate to opus (3 more)       |
| Fails 3x with opus        | REITERATE to /plan              |
| Checkpoint timeout        | Ask user to continue or abort   |
| Strategy unclear          | Default to Strategy C           |
| Mixed checkpoint types    | Strategy C (most interactive)   |

### REITERATE Protocol

When opus fails 3 times:

1. Store comprehensive failure analysis in reflection MCP
2. Return REITERATE status with all 6 attempts documented
3. Prompt user to re-run `/plan "[task]" --context="REITERATE: [summary]"`
4. /plan will re-analyze with failure context and may suggest different approach
