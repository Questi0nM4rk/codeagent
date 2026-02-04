---
name: learner
description: Pattern extractor that stores lessons learned after successful implementations. Updates project knowledge.
activation:
  triggers:
    - "extract patterns"
    - "what did we learn"
    - "store lessons"
    - "update knowledge"
  file_patterns: []
thinking: think
tools:
  - Read
  - Write
  - Edit
  - Glob
  - mcp__amem__search_memory
  - mcp__amem__store_memory
  - mcp__amem__update_memory
  - mcp__reflection__store_episode
  - mcp__reflection__export_lessons
  - mcp__reflection__get_common_lessons
---

# Learner Skill

Knowledge curator that extracts patterns from successful implementations.

## The Iron Law

```
ONLY STORE GENUINELY REUSABLE PATTERNS
Don't store trivial or obvious things. Include concrete examples.
```

## Core Principle

> "Lessons are only valuable if they prevent future mistakes."

## When to Activate

**Always:**

- After successful implementation
- After approved review
- When patterns emerge during work
- End of significant task

**Skip when:**

- Implementation followed existing patterns exactly
- Nothing new to learn
- Trivial changes

## Step 0: Check Existing Lessons (ALWAYS)

Before extracting new patterns:

```yaml
# Get proven lessons from reflection memory
mcp__reflection__export_lessons:
  min_occurrences: 2
  min_success_rate: 0.5

# Get aggregated lessons by feedback type
mcp__reflection__get_common_lessons
```

Compare new patterns against these:

- If 80%+ overlap: skip extraction, note "already captured"
- If partial overlap: update existing memory instead of new

## Workflow

### 1. Analyze Implementation

Review what was built:

- What problem was solved?
- What approach was taken?
- What patterns were used?
- What made it successful?

### 2. Extract Patterns

Look for:

**Architectural Patterns**
- How components are organized
- Dependency relationships
- Data flow patterns

**Code Patterns**
- Error handling approaches
- Validation patterns
- API design patterns

**Testing Patterns**
- Test structure
- Mock/stub approaches
- Assertion patterns

**Process Patterns**
- What worked in the TDD loop
- Useful debugging approaches
- Effective refactoring steps

### 3. Store in A-MEM

```yaml
mcp__amem__store_memory:
  content: |
    ## Pattern: [Name]
    Type: [architectural|code|testing|process]
    Context: [when to use]
    Implementation: [how it was done]
    Files: [reference files]
    Learned: [date]

    ### Description
    [What this pattern solves]

    ### Example
    [Code snippet or reference]

    ### Gotchas
    [What to watch out for]
  tags: ["project:[name]", "[type]", "pattern"]
```

### 4. Store Success Episode

```yaml
mcp__reflection__store_episode:
  task: "[task description]"
  approach: "[what was done]"
  outcome: "success"
  feedback: "[what worked well]"
  feedback_type: "implementation_success"
  reflection:
    what_worked: "[key success factors]"
    reusable_pattern: "[pattern name]"
    time_saved_by: "[approach that saved time]"
  file_path: "[main file]"
  tags: ["success", "[language]", "[pattern-type]"]
```

### 5. Check for Existing Patterns

Before storing, check if pattern already exists:

```yaml
mcp__amem__search_memory:
  query: "[pattern name]"
  k: 5
```

If exists, update rather than duplicate:

```yaml
mcp__amem__update_memory:
  memory_id: "[existing]"
  content: "[updated with new example]"
```

### 6. Update PROJECT.md

Add task completion to `.codeagent/knowledge/PROJECT.md`:

**Recent Completions section:**
```markdown
## Recent Completions

### TASK-XXX: [name] ([date])
[1-2 sentence summary]

- Files: [main files] (+X lines)
- Tests: X tests, Y% coverage
- See: summaries/TASK-XXX-summary.md
```

**Key Decisions section (if applicable):**
```markdown
## Key Decisions

| Date | Decision | Rationale | Task |
|------|----------|-----------|------|
| [date] | [decision] | [why] | TASK-XXX |
```

### 7. Generate Task Summary

**File:** `.codeagent/knowledge/summaries/TASK-XXX-summary.md`

```markdown
# Task Summary: TASK-XXX

**Name:** [task name]
**Epic:** EPIC-XXX
**Completed:** [timestamp]

## What Was Done

[Detailed description of implementation]

## Files Modified

| File | Action | Lines |
|------|--------|-------|
| [file] | Created/Modified | +X, -Y |

## Tests Added

| Test | Description |
|------|-------------|
| [test name] | [what it tests] |

## Patterns Used

- [Pattern 1]: [how applied]
- [Pattern 2]: [how applied]

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| [choice] | [why] |

## Lessons Learned

[What was discovered during implementation]
```

## Output Format

```markdown
## Learning Report

### Implementation Summary
- Task: [TASK-XXX: name]
- Epic: [EPIC-XXX: name]
- Duration: [time taken]
- Outcome: Success

### Files Created/Updated

| File | Action |
|------|--------|
| .codeagent/knowledge/summaries/TASK-XXX-summary.md | Created |
| .codeagent/knowledge/PROJECT.md | Updated |

### Patterns Extracted

#### Pattern 1: [Name]
- Type: [architectural|code|testing|process]
- Reusability: [high|medium|low]
- Stored: A-MEM memory [id]

#### Pattern 2: [Name]
[same structure]

### Knowledge Updates
| Type | Action | ID |
|------|--------|-----|
| A-MEM memory | created | [id] |
| Reflection episode | stored | [id] |
| Existing pattern | updated | [id] |

### Recommendations for Future
- [What to do differently]
- [What to keep doing]

### Nothing New (if applicable)
This implementation followed existing patterns. No new learnings extracted.
Task summary still generated for record.
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Nothing new here" | Even incremental improvements are worth noting. |
| "It's obvious" | Obvious to you now. Not to future developers. |
| "No time for docs" | Good docs save more time than they take. |
| "Memory is already full" | A-MEM handles duplicates. Store anyway. |

## Red Flags - STOP

- Storing trivial patterns
- No concrete examples
- Abstract descriptions without code
- Duplicating existing patterns
- Missing file/line references
- Not checking existing lessons first

If you see these, reconsider what's worth storing.

## Verification Checklist

- [ ] Checked existing lessons first
- [ ] Pattern is genuinely reusable
- [ ] Includes concrete examples
- [ ] Links to actual files
- [ ] Stored in A-MEM with proper tags
- [ ] Stored success episode in reflection
- [ ] Updated PROJECT.md
- [ ] Generated task summary

## Related Skills

- `researcher` - Queries patterns stored by learner
- `architect` - Uses learned patterns in designs
- `implementer` - Follows learned patterns

## Handoff

After learning completes:

1. Patterns available in A-MEM for future queries
2. Success episodes inform future reflection
3. PROJECT.md updated for project overview
4. Task summary available for reference
