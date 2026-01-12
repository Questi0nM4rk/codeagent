---
description: Investigate before planning (creates spike items)
---

# /analyze - Spike Investigation

Time-boxed investigation of a topic before deriving tasks. Creates spike items in the backlog that auto-generate epics/tasks when findings are actionable.

**Spikes** are Jira/Agile terminology for time-boxed research to reduce uncertainty.

## Usage

```
/analyze "How should we handle auth?"     # Create spike item
/analyze SPIKE-001                          # Continue existing spike
/analyze --deep "Performance issues"        # Extended investigation
/analyze --list                             # Show all spike items
```

## Agent Pipeline

```
Main Claude (Orchestrator)
      │
      └─► analyst agent (opus)
              skills: [researcher, domain skills]
              → Query A-MEM for prior knowledge
              → Query codebase index for patterns
              → External research (Context7, web) if needed
              → Generate spike output
              → Auto-create derived epics/tasks
```

## Process

### Phase 1: Check Existing Knowledge

Before new investigation:

```
1. Query A-MEM for related memories
   mcp__amem__search_memory(query="[topic]", k=10)

2. Check existing spike items
   Read .codeagent/backlog/spikes/*.yaml

3. If sufficient knowledge exists:
   - Summarize existing knowledge
   - Skip to derived items
```

### Phase 2: Codebase Analysis

If knowledge gaps exist:

```
1. Query codebase index for patterns
   - Function/class definitions related to topic
   - Import patterns
   - Existing implementations

2. Read relevant files
   - Configuration files
   - Existing similar features
   - Test patterns
```

### Phase 3: External Research (if needed)

Only when codebase doesn't have answers:

```
1. Context7 for library documentation
   mcp__context7__resolve-library-id(...)
   mcp__context7__query-docs(...)

2. Web search for best practices
   mcp__tavily__tavily-search(query="[topic] best practices")
```

### Phase 4: Generate Output

Create spike item and output:

1. **Spike YAML**: `.codeagent/backlog/spikes/SPIKE-XXX.yaml`
2. **Spike output**: `.codeagent/knowledge/outputs/SPIKE-XXX-output.md`
3. **Update PROJECT.md**: Add findings to relevant section
4. **Store in A-MEM**: Key findings with project tag

### Phase 5: Auto-Create Derived Items

When findings are actionable:

```
1. Create epic if scope is large
   .codeagent/backlog/epics/EPIC-XXX.yaml

2. Create tasks from findings
   .codeagent/backlog/tasks/TASK-XXX.yaml

3. Link spike to derived items
   derived_items:
     - type: epic
       id: EPIC-001
```

## Output Format

```markdown
## Spike Complete: [Topic]

### Spike ID: SPIKE-XXX

### Summary
[1-2 sentence summary of findings]

### Key Findings

1. **[Finding 1]**
   Source: [A-MEM/codebase/Context7/web]
   [Details]

2. **[Finding 2]**
   [Details]

### Recommendations

Based on findings:
- [Recommendation 1]
- [Recommendation 2]

### Derived Items Created

| Type | ID | Name | Status |
|------|-----|------|--------|
| Epic | EPIC-001 | [name] | ready |
| Task | TASK-001 | [name] | backlog |
| Task | TASK-002 | [name] | backlog |

### Files Created

- `.codeagent/backlog/spikes/SPIKE-XXX.yaml` (spike item)
- `.codeagent/knowledge/outputs/SPIKE-XXX-output.md` (detailed findings)
- `.codeagent/knowledge/PROJECT.md` (updated)
- `.codeagent/backlog/epics/EPIC-XXX.yaml` (if created)
- `.codeagent/backlog/tasks/TASK-XXX.yaml` (if created)

### Confidence: X/10

### Next Steps

Run `/plan` to detail the created tasks, or:
- `/implement TASK-001` to start implementation
- `/analyze "[follow-up topic]"` for deeper research
```

## Spike Output Format

**File:** `.codeagent/knowledge/outputs/SPIKE-XXX-output.md`

```markdown
# Spike: [Topic]

**ID:** SPIKE-XXX
**Timebox:** 4h
**Completed:** [timestamp]
**Confidence:** X/10

## Question

[Original question or uncertainty to investigate]

## Summary

[2-3 sentence summary of key findings]

## Detailed Findings

### 1. [Finding Area 1]

[Detailed explanation with code examples if relevant]

**Source:** [A-MEM memory ID / codebase file:line / Context7 / URL]

### 2. [Finding Area 2]

[Details]

## Code Examples

```language
[Relevant code snippets from findings]
```

## Recommendations

| Recommendation | Rationale | Priority |
|----------------|-----------|----------|
| [Rec 1] | [Why] | High |
| [Rec 2] | [Why] | Medium |

## Sources

### A-MEM
- mem_XXX: [description]

### Codebase
- `src/path/file.cs:123`: [what was found]

### External
- [URL]: [description]
- Context7/library: [what was found]

## Derived Work Items

- [x] EPIC-XXX created: [name]
- [x] TASK-XXX created: [name]
- [x] TASK-XXX created: [name]

## Knowledge Integration

Added to PROJECT.md:
- Section: [section name]
- Key patterns documented
```

## Flags

| Flag | Effect |
|------|--------|
| `--deep` | Extended investigation with more external research |
| `--list` | Show all spike items and their status |
| `--no-derive` | Don't auto-create epics/tasks |
| `--timebox 2h` | Override default timebox (default: 4h) |

## A-MEM Integration

### Before Spike

```
mcp__amem__search_memory:
  query="[topic] patterns architecture"
  k=10
  project="[project-name]"
```

### After Spike

```
mcp__amem__store_memory:
  content="## Spike: [topic]
Type: spike
Context: [when this applies]

### Key Findings
[findings]

### Recommendations
[recommendations]"
  tags=["project:[name]", "spike", "[topic-tags]"]
```

## ID Generation

Spike IDs are auto-generated:

```
1. Read .codeagent/config.yaml for id_prefix
2. Find highest existing SPIKE-XXX number
3. Increment: SPIKE-{N+1}
```

## Derived Item Rules

**Create Epic when:**
- Scope requires multiple tasks
- Work spans multiple areas of codebase
- Estimated effort > 1 day

**Create Tasks when:**
- Findings are actionable
- Clear implementation steps identified
- Files/patterns to modify known

**Don't create items when:**
- Spike is exploratory only
- Findings require more research first
- User requested `--no-derive`

## Notes

- Spike items auto-create derived work (no confirmation needed)
- Use `--no-derive` if you only want investigation, not planning
- Deep spikes (`--deep`) cost more tokens but find more
- Always check A-MEM first to avoid redundant investigation
- Store all significant findings in A-MEM for future reference
- Spikes are time-boxed: respect the timebox to avoid scope creep
