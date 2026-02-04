---
name: architect
description: Solution design with Tree-of-Thought exploration. Generates multiple approaches and evaluates tradeoffs before recommending.
activation:
  triggers:
    - "design"
    - "architecture"
    - "how should we"
    - "what approach"
    - "plan the implementation"
    - "multiple options"
  file_patterns: []
thinking: ultrathink
tools:
  - Read
  - Glob
  - Grep
  - mcp__amem__search_memory
  - mcp__amem__store_memory
  - mcp__amem__list_memories
---

# Architect Skill

Structured solution design using Tree-of-Thought exploration. Always generate 3+ approaches.

## The Iron Law

```
MINIMUM 3 APPROACHES - NEVER RECOMMEND FIRST IDEA
The first solution is rarely the best. Always explore alternatives.
```

## Core Principle

> "Every design decision has tradeoffs. Make them explicit."

## When to Activate

**Always:**

- Designing new features
- Making architectural decisions
- When multiple valid solutions exist
- Refactoring significant code
- Planning complex changes

**Skip when:**

- Trivial implementation
- Clear single approach
- User explicitly chose approach

## Step 0: Check Past Decisions (ALWAYS)

Before designing, query A-MEM:

```yaml
mcp__amem__search_memory:
  query: "architecture decisions for [feature area]"
  k: 10

mcp__amem__list_memories:
  limit: 10
  project: "[project-name]"
```

Use past decisions to:

- Avoid reinventing existing patterns
- Build on established conventions
- Understand why previous approaches were chosen

## Structured Exploration Process

Use extended thinking (`ultrathink`) to explore systematically:

### 1. Problem Decomposition

Break down the problem into:

- **Core requirements** (must have)
- **Constraints** (technical, business, time)
- **Assumptions** to validate

### 2. Generate Approaches (minimum 3)

For each approach, document:

- **Description**: What the approach does
- **Rationale**: Why it might work
- **Implementation sketch**: Key components/patterns

### 3. Evaluate Each Approach

Score on:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Feasibility | 0.3 | Can we actually build this? |
| Complexity | 0.2 | How hard is it? (Higher = simpler) |
| Maintainability | 0.3 | Future dev experience |
| Performance | 0.2 | Runtime characteristics |

### 4. Select Best Path

Calculate weighted scores and select the best.
Document why alternatives were rejected.

### 5. Detail Selected Approach

Expand with:

- Specific implementation steps
- Files to modify
- Potential risks and mitigations

## Output Format

```markdown
## Design: [Feature Name]

### Problem Statement
[Clear definition of what we're solving]

### Constraints
- [Technical constraints]
- [Business constraints]
- [Time/resource constraints]

### Approaches Considered

#### Approach A: [Name]
**Description**: [What it does]
**Pros**: [Benefits]
**Cons**: [Drawbacks]
**Complexity**: [Low/Medium/High]
**Risk**: [Low/Medium/High]

#### Approach B: [Name]
[Same structure]

#### Approach C: [Name]
[Same structure]

### Evaluation Matrix

| Criterion | Weight | A | B | C |
|-----------|--------|---|---|---|
| Feasibility | 0.3 | 8 | 7 | 9 |
| Complexity | 0.2 | 6 | 8 | 5 |
| Maintainability | 0.3 | 7 | 6 | 8 |
| Performance | 0.2 | 8 | 9 | 7 |
| **Weighted** | | **7.2** | **7.3** | **7.4** |

### Recommendation

**Selected: Approach [X]**

Rationale: [Why this approach]

### Implementation Plan

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Files Affected
| File | Change Type | Description |
|------|-------------|-------------|

### Risks and Mitigations
| Risk | Mitigation |
|------|------------|

### Open Questions
- [Things that need clarification]
```

## Store Design Decision (ALWAYS)

After finalizing design:

```yaml
mcp__amem__store_memory:
  content: |
    ## Architecture: [Decision Name]
    Type: architectural
    Context: [when this applies]

    ### Decision
    [The chosen approach]

    ### Alternatives Considered
    - [Approach A]: [rejected because...]
    - [Approach B]: [rejected because...]

    ### Rationale
    [Why this approach was selected]

    ### Implementation Notes
    [Key implementation details]
  tags: ["project:[name]", "architecture", "decision"]
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "First idea is fine" | First ideas miss tradeoffs. Explore more. |
| "No time for analysis" | Poor architecture costs more time later. |
| "It's obvious" | Make it explicit. Future devs need context. |
| "One approach is enough" | Even simple problems have alternatives. |

## Red Flags - STOP

- Only considering one approach
- Not documenting tradeoffs
- Skipping A-MEM lookup
- No evaluation matrix
- Missing risk analysis
- Not storing decision in A-MEM

If you see these, stop and explore properly.

## Verification Checklist

- [ ] Queried A-MEM for past decisions
- [ ] Generated minimum 3 approaches
- [ ] Evaluated each with weighted criteria
- [ ] Documented rejected alternatives
- [ ] Listed risks and mitigations
- [ ] Stored decision in A-MEM

## Related Skills

- `researcher` - Provides context for design
- `orchestrator` - Analyzes parallelization potential
- `implementer` - Executes the design
- `spec-driven` - Specs inform design constraints

## Handoff

After design completes:

1. Store decision in A-MEM
2. Pass to orchestrator for execution analysis
3. Include in `/plan` output
