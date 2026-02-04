---
name: plan
description: Research, design, and create implementation approach
---

# /plan - Unified Planning

Gathers context, designs solution, creates tasks, and determines execution strategy.

## Usage

```
/plan "Add JWT authentication"              # Standard planning
/plan "Add users and products"              # Auto-detects if parallelizable
/plan --sequential "Complex refactoring"    # Force sequential mode
/plan --deep "Investigate performance"      # Extra research phase
```

## Agent Pipeline

```
Main Claude (Orchestrator)
      |
      +-- researcher agent (opus)
      |       skills: [researcher, domain skills]
      |       --> Queries A-MEM, codebase, context7
      |       --> Returns: context summary, confidence score
      |
      +-- architect agent (opus)
      |       skills: [architect, spec-driven, domain skills]
      |       --> Uses ultrathink for structured exploration
      |       --> Returns: 3+ approaches with evaluation
      |
      +-- orchestrator agent (opus)
              skills: [orchestrator]
              --> Analyzes file/dependency conflicts
              --> Returns: PARALLEL or SEQUENTIAL decision + strategy
```

## Process

### Phase 1: Research (researcher agent)

```markdown
Research Priority:
1. Query A-MEM for similar past implementations
2. Analyze codebase for patterns and conventions
3. Only if needed: Context7 for docs, external research

Output: Context summary with confidence score
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

```markdown
Conflict Detection:
For each pair of subtasks (A, B):
  files_A = files modified by A
  files_B = files modified by B

  If (files_A intersection files_B) not empty --> CONFLICT
  Else --> PARALLELIZABLE
```

## Expected Output

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

### Execution Strategy: [A|B|C]

### Confidence: X/10

Ready for /implement (will auto-parallelize)
```

## Execution Strategies

| Strategy | When | Behavior |
|----------|------|----------|
| A | All auto tasks | Single subagent, full plan |
| B | Has verify checkpoints | Fresh subagent per segment |
| C | Has decision checkpoints | Main context only |

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| task | Yes | Description of what to implement |
| --sequential | No | Force sequential execution |
| --deep | No | Extended research phase |

## Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Plan | `.planning/PLAN.md` | Executable task definitions |
| State | `.planning/STATE.md` | Session state tracking |
| Backlog | `.codeagent/backlog/` | Task YAML files |
| A-MEM | Memory system | Architecture decisions |

## Context Files Generated

After planning:

```
.planning/
  STATE.md       # Session state and progress
  PLAN.md        # Executable task definitions
```

## A-MEM Integration

The planning pipeline uses A-MEM throughout:

**Researcher queries for:**
- Past similar designs
- Project conventions
- Previous architecture decisions

**Architect stores:**
- New design decisions
- Tradeoff analysis
- Implementation notes

**Orchestrator queries/stores:**
- Past parallelization decisions
- Known conflict patterns

## Example

```bash
# Standard planning
/plan "Add user authentication with JWT"

# Force sequential for complex refactoring
/plan --sequential "Migrate from REST to GraphQL"

# Deep research for investigation
/plan --deep "Optimize database queries"
```

## Notes

- Always run /scan before first /plan in a project
- /plan stores output in memory for /implement
- Use --deep for complex investigative tasks
- If confidence < 7, plan recommends human review
- Maximum 2-3 tasks per plan to prevent context degradation
