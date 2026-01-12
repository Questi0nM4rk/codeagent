# Knowledge Accumulation System

Specification for how CodeAgent accumulates and maintains project knowledge across sessions.

## Overview

```
Task Completed
     │
     ├─► Generate Summary → .codeagent/knowledge/summaries/TASK-XXX-summary.md
     │
     ├─► Update PROJECT.md → .codeagent/knowledge/PROJECT.md
     │       ├─► Recent Completions section
     │       ├─► Key Decisions (if any)
     │       └─► Architecture (if new patterns)
     │
     ├─► Store in A-MEM → Global memory with project tag
     │       ├─► Patterns discovered
     │       ├─► Architecture decisions
     │       └─► Auto-links to related memories
     │
     └─► Update task.yaml → status: done, summary, commits
```

## Knowledge Hierarchy

```
Global (A-MEM)                    Per-Project (.codeagent/)
     │                                    │
     ├─► Patterns                         ├─► PROJECT.md (overview)
     ├─► Architecture decisions           ├─► Task summaries
     ├─► Cross-project learnings          ├─► Spike outputs
     └─► Auto-linked memories             └─► Backlog items
```

## PROJECT.md Structure

**Location:** `.codeagent/knowledge/PROJECT.md`

**Template:** `@~/.claude/framework/templates/project/PROJECT.md.template`

### Sections

| Section | Content | Auto-Updated |
|---------|---------|--------------|
| Overview | Project description, type, dates | On init |
| Architecture | Patterns, stack, structure | On pattern discovery |
| Key Decisions | ADRs from implementations | On decision made |
| Conventions | Naming, organization, testing | On pattern discovery |
| Recent Completions | Last 10 task summaries | On task done |
| Open Items | In-progress and blocked | On status change |
| External References | Docs, dependencies | On spike |
| A-MEM Links | Memory IDs for this project | On memory store |

### Section Markers

Use markers to enable safe auto-updates:

```markdown
<!-- RECENT_COMPLETIONS_START -->
### TASK-001: Add JWT middleware (2026-01-10)
Added AuthMiddleware using JsonWebTokenHandler...
<!-- RECENT_COMPLETIONS_END -->
```

### Update Rules

1. **Insert at markers**: Add new content between START/END markers
2. **Preserve manual edits**: Only touch marked sections
3. **Limit recent completions**: Keep last 10, archive older
4. **Append decisions**: Never remove, only add

## Task Summary Generation

**Location:** `.codeagent/knowledge/summaries/TASK-XXX-summary.md`

**Template:** `@~/.claude/framework/templates/project/summary.md.template`

### When to Generate

1. Task status changes to `done`
2. All done criteria met
3. Tests passing

### Content Sources

| Field | Source |
|-------|--------|
| Task name/ID | task.yaml |
| Epic info | epic.yaml |
| Files modified | Git diff |
| Commits | Git log |
| Tests | Test runner output |
| Patterns | Learner agent analysis |
| Decisions | STATE.md or user input |
| Deviations | STATE.md |
| Lessons | Learner agent extraction |

### Summary Format

```markdown
# Task Summary: TASK-001

**Name:** Add JWT validation middleware
**Epic:** EPIC-001 - User Authentication System
**Completed:** 2026-01-10T17:30:00Z

## What Was Done
Added AuthMiddleware class implementing IMiddleware...

## Files Modified
| File | Action | Lines |
|------|--------|-------|
| src/Middleware/AuthMiddleware.cs | Created | +120 |

## Patterns Used
- **Middleware pattern**: Request interception for auth
- **Dependency injection**: IAuthService via constructor

## Key Decisions
| Decision | Rationale |
|----------|-----------|
| JsonWebTokenHandler | JwtSecurityTokenHandler deprecated in .NET 10 |
```

## A-MEM Integration

### What to Store

| Type | When | Tags |
|------|------|------|
| Patterns | New pattern discovered | `project:NAME`, `pattern`, `TYPE` |
| Decisions | Architecture choice made | `project:NAME`, `decision` |
| Structure | On /scan complete | `project:NAME`, `structure` |
| Lessons | After successful impl | `project:NAME`, `lesson` |

### Storage Format

```markdown
## [Type]: [Name]
Context: [When this applies]

### Description
[What this is]

### Example
[Code or usage example]

### Source
- Task: TASK-XXX
- File: path/to/file.cs
```

### Retrieval

Researcher agent queries:
```python
mcp__amem__search_memory(
    query="[topic]",
    k=10,
    project="[project-name]"
)
```

### Auto-Linking

A-MEM automatically:
1. Extracts keywords from content
2. Finds similar existing memories
3. Creates bidirectional links
4. Updates related memories with new context

## Spike Output Storage

**Location:** `.codeagent/knowledge/outputs/SPIKE-XXX-output.md`

### Content

```markdown
# Spike: [Topic]

**ID:** SPIKE-XXX
**Completed:** [timestamp]
**Confidence:** X/10

## Question
[Original question]

## Summary
[Key findings]

## Detailed Findings
### 1. [Finding]
[Details with code examples]
**Source:** [where found]

## Recommendations
| Recommendation | Rationale | Priority |
|----------------|-----------|----------|

## Sources
- A-MEM: [memory IDs]
- Codebase: [file:line refs]
- External: [URLs]
```

## External Docs Caching

**Location:** `.codeagent/knowledge/external/`

### When to Cache

1. Context7 docs relevant to project
2. API documentation referenced during spikes
3. Library guides used for implementation

### Cache Format

```
.codeagent/knowledge/external/
├── library-name/
│   ├── metadata.json
│   └── docs/
│       ├── getting-started.md
│       └── api-reference.md
```

### Metadata

```json
{
  "library": "qdrant-client",
  "version": "1.12.0",
  "cached": "2026-01-10T15:00:00Z",
  "source": "context7",
  "relevance": "codebase indexing"
}
```

## Knowledge Flow by Command

### /analyze

```
Input: Question/topic
     │
     ├─► Query A-MEM for existing knowledge
     ├─► Query codebase index
     ├─► External investigation if needed
     │
     └─► Output:
         ├─► SPIKE-XXX.yaml (backlog)
         ├─► SPIKE-XXX-output.md (knowledge)
         ├─► PROJECT.md update (if significant)
         └─► A-MEM store (if reusable)
```

### /plan

```
Input: Task description
     │
     ├─► Researcher queries knowledge
     ├─► Architect designs solution
     ├─► Orchestrator analyzes parallelism
     │
     └─► Output:
         ├─► EPIC-XXX.yaml (if large scope)
         ├─► TASK-XXX.yaml (backlog)
         ├─► PLAN.md (planning context)
         └─► A-MEM store (design decisions)
```

### /implement

```
Input: Task ID or plan
     │
     ├─► Load task context
     ├─► TDD implementation
     ├─► Handle deviations
     │
     └─► Output:
         ├─► TASK-XXX.yaml update (status: done)
         ├─► TASK-XXX-summary.md (knowledge)
         ├─► PROJECT.md update (completions, decisions)
         ├─► A-MEM store (patterns, lessons)
         └─► Reflection episode (success/failure)
```

## Retention Policy

### Keep Forever

- PROJECT.md
- Key decisions
- Architecture patterns
- A-MEM memories (auto-evolve)

### Keep Recent (10)

- Task summaries in PROJECT.md Recent Completions
- Spike outputs (older moved to archive)

### Archive

- `.codeagent/knowledge/archive/`
- Old summaries beyond retention limit
- Superseded spikes

### Clean Up

- Session files after completion
- Planning context after implementation
- Cached external docs after 30 days unused

## Best Practices

1. **Don't duplicate**: Check A-MEM before storing new knowledge
2. **Use project tags**: Always tag with `project:NAME`
3. **Link to sources**: Reference task IDs, file:line, memory IDs
4. **Keep summaries concise**: 1-2 sentences for overview
5. **Store decisions immediately**: Don't wait for task completion
6. **Update, don't append**: Evolve existing knowledge vs creating new
7. **Trust A-MEM linking**: Let it connect related concepts
8. **Archive, don't delete**: Keep history for future reference
