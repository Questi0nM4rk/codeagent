# Task States Reference

State machine for CodeAgent backlog items.

## State Diagram

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                     TASK LIFECYCLE                       │
                    │                                                          │
                    │  ┌─────────┐    ┌─────────┐    ┌─────────────┐          │
                    │  │ backlog │───►│  ready  │───►│ in_progress │          │
                    │  └─────────┘    └─────────┘    └─────────────┘          │
                    │       │              ▲               │                   │
                    │       │              │               ▼                   │
                    │       │              │         ┌─────────┐               │
                    │       │              │         │ blocked │               │
                    │       │              │         └─────────┘               │
                    │       │              │               │                   │
                    │       │              └───────────────┘                   │
                    │       │                      resolve                     │
                    │       │                                                  │
                    │       │         ┌─────────────────────────────┐         │
                    │       └────────►│           done              │         │
                    │    (deprecated) └─────────────────────────────┘         │
                    │                              ▲                          │
                    │                              │                          │
                    │                        tests pass                       │
                    │                              │                          │
                    │                        in_progress                      │
                    │                                                          │
                    └─────────────────────────────────────────────────────────┘
```

## States

### `backlog`

Item is recorded but not ready for work.

**Entry conditions:**
- Item created via /analyze (spike)
- Item created via /plan but dependencies not met
- Item deprioritized

**Exit conditions:**
- Dependencies met → `ready`
- Deprecated → (deleted or archived)

### `ready`

Item is ready to be worked on. All dependencies satisfied.

**Entry conditions:**
- From `backlog`: dependencies met
- From `blocked`: blocker resolved

**Exit conditions:**
- /implement started → `in_progress`
- Dependencies invalidated → `backlog`

### `in_progress`

Item is actively being worked on.

**Entry conditions:**
- /implement command started work
- Agent picked up task

**Exit conditions:**
- Tests pass, criteria met → `done`
- 3 failures, needs help → `blocked`
- Deprioritized → `backlog` (rare)

### `blocked`

Task cannot proceed without external help or decision.

**Entry conditions:**
- From `in_progress`: 3 test failures
- From `in_progress`: architectural decision needed (deviation rule 4)
- From `in_progress`: waiting on external dependency

**Exit conditions:**
- Blocker resolved → `ready`
- Converted to spike → (new SPIKE item created)

**Required fields when blocked:**
```yaml
blocker:
  reason: "Test fails: cannot mock IExternalService"
  since: "2026-01-10T16:00:00Z"
  needs: "Guidance on mocking external service"
```

### `done`

Item completed successfully.

**Entry conditions:**
- All acceptance criteria met
- All tests passing
- Summary generated

**Required fields when done:**
```yaml
completed_at: "2026-01-10T17:30:00Z"
summary: "Added AuthMiddleware using JsonWebTokenHandler for JWT validation"
commits:
  - "abc123: test(auth): add tests for JWT validation"
  - "def456: feat(auth): implement JWT validation middleware"
```

---

## State Transitions

### Valid Transitions

| From | To | Trigger | Agent |
|------|----|---------|-------|
| `backlog` | `ready` | Dependencies met | orchestrator |
| `ready` | `in_progress` | /implement | implementer |
| `in_progress` | `done` | Tests pass | implementer |
| `in_progress` | `blocked` | 3 failures OR rule 4 | implementer |
| `blocked` | `ready` | Blocker resolved | user/orchestrator |
| `ready` | `backlog` | Dependencies invalidated | orchestrator |
| `in_progress` | `backlog` | Deprioritized (rare) | user |

### Invalid Transitions

| From | To | Why Invalid |
|------|----|----|
| `backlog` | `in_progress` | Must go through `ready` |
| `done` | any | Completed items are final |
| `blocked` | `done` | Must resolve then complete work |
| `blocked` | `in_progress` | Must go through `ready` |

---

## State Changes by Command

### `/analyze`

Creates spike items in `in_progress` state.

### `/plan`

1. Creates epic in `ready` state (if no dependencies)
2. Creates tasks in `backlog` state
3. Checks dependencies, moves eligible to `ready`

### `/implement`

1. Picks next `ready` task
2. Moves to `in_progress`
3. On success: moves to `done`, generates summary
4. On 3 failures: moves to `blocked` (prompts for bug creation)

### `/backlog`

Read-only view. Does not change states.

### Manual state changes

Users can request:
- Deprioritize: any → `backlog`
- Unblock: `blocked` → `ready` (after resolving)

---

## Dependency Handling

### Task Dependencies

```yaml
# TASK-002 depends on TASK-001
id: TASK-002
depends_on:
  - TASK-001
```

**Behavior:**
- TASK-002 stays in `backlog` until TASK-001 is `done`
- When TASK-001 completes, orchestrator checks TASK-002
- If all dependencies met, TASK-002 moves to `ready`

### Epic Dependencies

```yaml
# EPIC-002 depends on EPIC-001
id: EPIC-002
dependencies:
  - EPIC-001
```

**Behavior:**
- All tasks in EPIC-002 stay `backlog` until EPIC-001 is `done`
- Epic completion = all tasks `done`

---

## Bug State Flow

Bugs follow simplified flow:

```
backlog → ready → in_progress → done
```

No `blocked` state for bugs. If a bug fix is blocked:
1. Document the blocker in description
2. Move back to `backlog` with updated priority
3. Create separate spike item if needed

---

## Spike State Flow

Spikes have minimal states:

```
backlog → in_progress → done
```

**Key differences:**
- No `ready` state (spikes start immediately)
- No `blocked` state (spikes continue or are abandoned)
- Time-boxed: spike ends when timebox expires or question answered
- `done` triggers auto-creation of derived items

---

## Progress Tracking

### Epic Progress

Calculated from task states:

```yaml
progress:
  total_tasks: 5
  completed: 2
  percentage: 40
```

### Sprint/Session Progress

Session file tracks:

```yaml
# .codeagent/sessions/current.yaml
started: "2026-01-10T09:00:00Z"
items_completed:
  - TASK-001
  - TASK-002
items_in_progress:
  - TASK-003
items_blocked:
  - TASK-004
```

---

## State Hooks

### Pre-transition hooks

Before state changes, agents may:
- Validate preconditions
- Check dependencies
- Request confirmation

### Post-transition hooks

After state changes:
- `→ done`: Generate summary, update PROJECT.md
- `→ blocked`: Create checkpoint branch
- `→ ready`: Notify if high priority

---

## Best Practices

1. **Don't skip states** - Always follow valid transitions
2. **Document blockers** - Fill blocker fields when moving to `blocked`
3. **Generate summaries** - Never mark `done` without summary
4. **Check dependencies** - Before moving to `ready`, verify all deps are `done`
5. **Keep backlog clean** - Periodically review and remove stale items
