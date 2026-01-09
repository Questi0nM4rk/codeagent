---
name: brainstorming
description: Creative problem-solving methodology. Activates when exploring solutions, generating alternatives, or facing novel problems. Enforces divergent thinking before convergent selection.
---

# Brainstorming Skill

Creative exploration methodology for generating multiple approaches before selecting one. Quantity precedes quality.

## The Iron Law

```
DIVERGE BEFORE CONVERGE - QUANTITY BEFORE QUALITY
Generate at least 5 options before evaluating ANY of them. Premature evaluation kills creativity.
```

## Core Principle

> "The first idea is rarely the best idea. The fifth idea is rarely the last idea."

## When to Use

**Always:**
- Designing new features or systems
- Solving problems with no obvious solution
- Exploring architectural decisions
- When first instinct feels too simple
- Breaking out of analysis paralysis
- When current approach isn't working

**Exceptions (ask human partner):**
- Bug with obvious root cause (use systematic-debugging instead)
- Standard CRUD operations with established patterns
- Direct implementation of well-defined spec

## The Brainstorming Phases

```
DIVERGE → INCUBATE → CONVERGE → SELECT

1. DIVERGE: Generate ideas without judgment (5+ minimum)
2. INCUBATE: Let ideas sit, combine, mutate
3. CONVERGE: Evaluate against criteria
4. SELECT: Choose best option(s) to pursue
```

## Workflow

### Step 1: Frame the Problem

Before generating solutions, ensure the problem is well-defined.

```markdown
## Problem Frame

**Current State**: [What exists now]
**Desired State**: [What we want]
**Constraints**: [Hard limits we can't change]
**Assumptions**: [Things we believe to be true - challenge these]

**Problem Statement**: How might we [achieve desired state] given [constraints]?
```

### Step 2: Diverge (GENERATE)

Rules during divergence:
- NO evaluation or criticism
- Quantity over quality
- Build on others' ideas ("Yes, and...")
- Wild ideas welcome
- Defer judgment completely

Generate ideas using these techniques:

**Technique 1: Constraint Removal**
```markdown
## What if we removed...
- Time constraints → "If we had unlimited time..."
- Technical constraints → "If any technology existed..."
- Resource constraints → "If we had unlimited budget..."
- Political constraints → "If everyone agreed..."
```

**Technique 2: Analogies**
```markdown
## How do others solve this?
- How does [other industry] solve this?
- How would [company/person] approach this?
- How does nature solve this?
- How did this work in [historical context]?
```

**Technique 3: Crazy 8s**
```markdown
## 8 ideas in 8 minutes
1. [first thought - get it out]
2. [opposite of first]
3. [simplest possible]
4. [most complex/complete]
5. [what if we did nothing?]
6. [what would [expert] do?]
7. [what if constraint X didn't exist?]
8. [combine ideas 2 and 4]
```

**Technique 4: Six Thinking Hats**
```markdown
## Perspectives
- WHITE (facts): What do we know? What data exists?
- RED (feelings): What's our gut reaction?
- BLACK (caution): What could go wrong?
- YELLOW (benefits): What are the advantages?
- GREEN (creativity): What new ideas emerge?
- BLUE (process): What's our next step?
```

**Technique 5: SCAMPER**
```markdown
## Transform existing solutions
- Substitute: What can we replace?
- Combine: What can we merge?
- Adapt: What can we borrow from elsewhere?
- Modify: What can we change (bigger/smaller/faster)?
- Put to other use: How else could this be used?
- Eliminate: What can we remove?
- Reverse: What if we did the opposite?
```

### Step 3: Incubate

After generating 5+ ideas:
- Take a mental break (even 5 minutes helps)
- Review ideas for combinations
- Let subconscious process
- Note any new ideas that emerge

### Step 4: Converge (EVALUATE)

Only NOW apply judgment. Evaluate against criteria:

```markdown
## Evaluation Matrix

| Idea | Feasibility (1-5) | Impact (1-5) | Effort (1-5) | Risk (1-5) | Score |
|------|-------------------|--------------|--------------|------------|-------|
| [1]  | 4 | 5 | 3 | 2 | 14 |
| [2]  | 3 | 4 | 4 | 3 | 14 |
| [3]  | 5 | 3 | 5 | 1 | 14 |
| [4]  | 2 | 5 | 2 | 4 | 13 |
| [5]  | 4 | 4 | 3 | 2 | 13 |
```

### Step 5: Select

Choose based on:
- Highest score with acceptable risk
- Prototype-ability (can we test quickly?)
- Reversibility (can we change our mind?)

## Examples

<Good>
```markdown
## Problem: API rate limiting system design

### Problem Frame
**Current**: No rate limiting, vulnerable to abuse
**Desired**: Fair usage limits, good UX for legitimate users
**Constraints**: Must work in distributed system, <10ms latency overhead
**Assumptions**: We have Redis available, most users are legitimate

### Divergent Ideas (10 minutes, no judgment)

1. **Token bucket per user** - Classic, well-understood
2. **Sliding window log** - More accurate but memory-heavy
3. **Fixed window counter** - Simple but bursty at boundaries
4. **Leaky bucket** - Smooths traffic but delays legitimate bursts
5. **Adaptive limits** - Adjust based on user behavior/trust score
6. **Circuit breaker pattern** - Fail fast when overwhelmed
7. **Tiered limits** - Different limits for different user tiers
8. **Collaborative filtering** - Learn from abuse patterns across users
9. **Client-side exponential backoff** - Push some work to client
10. **Do nothing differently** - Just scale up? What would that cost?

### Combinations
- 1 + 7: Token bucket with tiered limits by subscription
- 5 + 8: Adaptive limits informed by abuse pattern detection
- 6 + 9: Circuit breaker with client backoff

### Evaluation
| Idea | Feasibility | Impact | Effort | Risk | Score |
|------|-------------|--------|--------|------|-------|
| Token bucket + tiers | 5 | 4 | 3 | 1 | 13 |
| Adaptive + patterns | 3 | 5 | 2 | 3 | 13 |
| Sliding window | 4 | 4 | 4 | 2 | 14 |
| Circuit + backoff | 4 | 3 | 4 | 2 | 13 |

### Selection
**Primary**: Token bucket + tiers (proven, low risk, good enough)
**Consider for v2**: Adaptive limits once we have usage data
```
- Problem framed before solutions
- Generated 10+ ideas without judgment
- Combined ideas to create new options
- Evaluated systematically
- Selected with rationale
</Good>

<Bad>
```markdown
## Problem: API rate limiting

Solution: We should use token bucket algorithm because it's the standard
approach. Here's the implementation...

[proceeds to implement immediately]
```
- No divergent phase
- First idea accepted without alternatives
- No evaluation criteria
- Missed potentially better options
- No consideration of problem framing
</Bad>

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I already know the best solution" | You might. Generate alternatives anyway to confirm. |
| "We don't have time to brainstorm" | Bad solutions cost more time than brainstorming saves. |
| "The options are obvious" | Obvious to you isn't obvious to everyone. Make them explicit. |
| "My first idea is usually right" | Confirmation bias. Test it against alternatives. |
| "This problem is too simple" | Simple problems have multiple solutions. Explore them. |
| "Brainstorming is fluffy/soft" | It's structured creativity with measurable output. |

## Red Flags - STOP and Start Over

These indicate you're converging too early:

- Implementing before generating alternatives
- Evaluating ideas AS they're generated
- Stopping at 2-3 ideas ("that's enough")
- Dismissing ideas as "impractical" during divergence
- Jumping to "the obvious solution"
- Not writing down rejected ideas
- Skipping the incubation phase entirely

**If you catch yourself doing these, STOP. Go back to divergence. Generate more ideas.**

## Verification Checklist

Before selecting a solution:

- [ ] Problem framed with constraints and assumptions
- [ ] Generated at least 5 distinct ideas
- [ ] Divergence phase had NO evaluation
- [ ] Wild/impractical ideas were welcomed
- [ ] Looked for idea combinations
- [ ] Evaluation criteria defined before scoring
- [ ] All ideas evaluated against same criteria
- [ ] Selection rationale documented
- [ ] Alternative options preserved for future consideration

## When Stuck

| Problem | Solution |
|---------|----------|
| Can't think of ideas | Use SCAMPER on existing solutions. Try analogies. |
| All ideas seem bad | You're still judging. Generate more without evaluating. |
| Ideas too similar | Add constraints or remove them. Try opposite approaches. |
| Paralyzed by options | Use evaluation matrix. Score and rank. |
| Team can't agree | Vote independently first, then discuss outliers. |
| Time pressure | Timebox: 5 min diverge, 2 min evaluate, decide. |

## Facilitation Tips

For brainstorming with others:

```markdown
## Session Setup
1. Define problem clearly (2 min)
2. Diverge silently first (3 min writing)
3. Share and build on ideas (5 min)
4. Crazy ideas round (2 min - encourage wild)
5. Combine and cluster (3 min)
6. Evaluate against criteria (5 min)
7. Select and assign (2 min)
```

## Idea Documentation Template

```markdown
# Brainstorm: [Topic]

## Problem Frame
**Current State**:
**Desired State**:
**Constraints**:
**Assumptions**:

## Ideas Generated
1. [idea] - [one line description]
2. [idea] - [one line description]
...

## Combinations Explored
- [idea A] + [idea B] = [new idea]

## Evaluation Criteria
- [criterion 1]: weight X
- [criterion 2]: weight Y

## Evaluation Matrix
| Idea | C1 | C2 | ... | Score |
|------|----|----|-----|-------|

## Selected Approach
**Primary**: [choice] because [rationale]
**Backup**: [alternative] if [condition]

## Parking Lot (for future consideration)
- [idea not selected but worth remembering]
```

## Related Skills

- `architect` - Use ToT for deep evaluation after brainstorming narrows options
- `spec-driven` - Brainstorm approaches before writing detailed specs
- `researcher` - Gather context before brainstorming to inform ideas
