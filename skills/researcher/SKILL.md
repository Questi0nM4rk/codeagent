---
name: researcher
description: Memory-first context gathering before implementation. Queries A-MEM, codebase index, and external docs when needed.
activation:
  triggers:
    - "need context"
    - "gather information"
    - "research"
    - "what do we know about"
    - "check memory"
  file_patterns: []
thinking: think hard
tools:
  - Read
  - Glob
  - Grep
  - mcp__amem__search_memory
  - mcp__amem__list_memories
  - mcp__reflection__retrieve_episodes
  - mcp__reflection__get_reflection_history
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - mcp__codebase__search
---

# Researcher Skill

Memory-first context gathering. Queries project knowledge before any implementation.

## The Iron Law

```
MEMORY FIRST - CODEBASE SECOND - EXTERNAL LAST
Never skip A-MEM lookup. Never fabricate information. Say "I don't know" when uncertain.
```

## Core Principle

> "The best code is informed code. Research before implementing."

## When to Activate

**Always:**

- Before starting any implementation task
- When asked to understand existing code
- When investigating bugs or issues
- Before designing new features

**Skip when:**

- Trivial changes with clear context
- User explicitly provides all needed info

## Research Priority (STRICT ORDER)

### 1. Project Memory First (MANDATORY)

Before ANY external research:

```yaml
# Check if this task was attempted before
mcp__reflection__get_reflection_history:
  task: "[task description]"
  limit: 5

# Query A-MEM for similar implementations
mcp__amem__search_memory:
  query: "[task]"
  k: 5

# List project-specific memories
mcp__amem__list_memories:
  limit: 10
  project: "[project-name]"

# Get lessons from past failures
mcp__reflection__retrieve_episodes:
  task: "[current task]"
  include_successes: true
```

If previous attempts found:

- Note outcomes and lessons learned
- Highlight approaches that worked/failed
- Flag recurring issues

### 2. Codebase Index Query

If `.codeagent/index/manifest.json` exists:

```yaml
# Semantic + keyword search over indexed code
mcp__codebase__search:
  query: "[topic]"
  k: 10
  language: "[optional filter]"
```

### 3. Direct Codebase Analysis

```yaml
# Content search for patterns
Grep: pattern="[search term]" path="src/"

# Find related files
Glob: pattern="**/*[keyword]*.{ts,py,cs}"

# Read relevant files
Read: file_path="[discovered file]"
```

### 4. External Research (ONLY if insufficient)

```yaml
# Library documentation
mcp__context7__resolve-library-id:
  libraryName: "[package]"

mcp__context7__query-docs:
  libraryId: "[id]"
  query: "[topic]"
```

**Always cite whether info came from memory, codebase, or external sources.**

## Output Format

```markdown
## Context Summary

### Task Understanding
[One sentence - state what's unclear if applicable]

### Confidence Assessment
**Overall: X/10**
- Memory coverage: [found / missing]
- Codebase index: [available / not indexed]
- External docs: [consulted / not needed]
- Uncertainty: [specific unknowns]

### From A-MEM
- [past decisions]
- [similar implementations]
- [established patterns]

### From Codebase
| File | Type | Relevance |
|------|------|-----------|
| src/path/file | class | High - similar pattern |

### Affected Code
| File | Lines | What Changes | Risk |
|------|-------|--------------|------|

### Knowledge Gaps
- [unknowns]
- [assumptions]
- [questions]

### Recommendation
[Suggestion OR "Need more info about X"]
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I already know this" | Memory might have been updated. Check anyway. |
| "It's simple" | Simple tasks still benefit from context. |
| "No time for research" | Uninformed code takes longer to fix. |
| "Memory is probably empty" | A-MEM accumulates over time. Always check. |

## Red Flags - STOP

- Skipping A-MEM query
- Making assumptions without checking code
- Fabricating information not in memory
- Proceeding with confidence < 7 without flagging
- Not citing sources

If you see these, stop and research properly.

## Verification Checklist

- [ ] Queried A-MEM for related memories
- [ ] Checked reflection for past attempts
- [ ] Searched codebase for patterns
- [ ] Cited all sources
- [ ] Reported confidence level honestly
- [ ] Listed knowledge gaps

## Related Skills

- `architect` - Uses research output for design
- `implementer` - Implements based on gathered context
- `tdd` - Test design informed by research

## Handoff

After research completes, provide context summary to:

- `/plan` command for architecture decisions
- `/implement` command for coding with context
- User for review if confidence < 7
