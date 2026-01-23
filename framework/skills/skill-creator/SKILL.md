---
name: skill-creator
description: Meta-skill for creating new CodeAgent skills. Activates when designing new skills, documenting methodologies, or extending the skill system. Enforces clear Iron Laws and actionable structure.
---

# Skill Creator Skill

Meta-skill for creating well-designed, effective skills for the CodeAgent framework. Every skill must have an unmistakable core rule.

## The Iron Law

```text
IRON LAW FIRST - IF YOU CAN'T STATE THE CORE RULE, DON'T CREATE THE SKILL
A skill without a clear, unmistakable Iron Law is not a skill - it's vague advice.
```text

## Core Principle

> "A skill is a compressed methodology. If you can't fit the core on a sticky note, it's not focused enough."

## When to Use

**Always:**

- Creating new skills for the CodeAgent framework
- Refining existing skills that lack clarity
- Documenting team methodologies as skills
- Converting best practices into actionable skills

**Exceptions (ask human partner):**

- One-off procedures (use runbook instead)
- Personal preferences (not universal enough for skill)
- Contextual advice (too situation-dependent)

## Skill Design Principles

### 1. Iron Law Must Be Unmistakable

The Iron Law should:

- Fit in one sentence (max 10 words)
- Be written in CAPS
- Leave zero ambiguity
- Apply universally within the skill's domain
- Be memorable ("NO CODE WITHOUT FAILING TEST")

<Good>
```text
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
NEVER SELF-VALIDATE - USE EXTERNAL TOOLS ONLY
REPRODUCE BEFORE FIX - NO GUESSING
```text
Clear, memorable, actionable.
</Good>

<Bad>
```text
Try to write tests when possible and practical
Consider using linters and other tools
Debug systematically when you have time
```text
Vague, conditional, forgettable.
</Bad>

### 2. Skills Compress Methodologies

A good skill takes a 50-page book and extracts:

- One core rule (Iron Law)
- 5-7 key steps (Workflow)
- Common pitfalls (Rationalizations)
- Recovery procedures (When Stuck)

### 3. Rationalizations Anticipate Failure

The best skills predict how people will avoid them:

 | Pattern | Example |
 | --------- | --------- |
 | Time pressure | "I don't have time for this" |
 | Overconfidence | "I know this works" |
 | Exception-seeking | "This case is different" |
 | Procrastination | "I'll do it later" |
 | Minimization | "It's too simple to need this" |

### 4. Examples Must Show Contrast

Good examples show BOTH correct and incorrect approaches with clear explanations of WHY one is good and the other is bad.

## Workflow

### Step 1: Identify the Methodology

What specific methodology or practice are you encoding?

```markdown
## Skill Discovery

**Methodology**: [Name of practice/methodology]
**Source**: [Book, framework, team practice]
**Domain**: [When this applies]
**Anti-pattern**: [What happens without this skill]
```text

### Step 2: Find the Iron Law

Extract the ONE non-negotiable rule:

```markdown
## Iron Law Candidates

1. [Attempt 1] - too long? too vague?
2. [Attempt 2] - clearer?
3. [Attempt 3] - unmistakable?

## Selected Iron Law
[FINAL VERSION IN CAPS]
```text

Test your Iron Law:

- Can someone remember it after one reading?
- Does it have exceptions? (if yes, refine it)
- Would violating it obviously cause problems?
- Is it actionable (not just philosophical)?

### Step 3: Define the Workflow

Break the methodology into 4-7 concrete steps:

```markdown
## Workflow Steps

1. [Action verb] [Object] - [Brief description]
2. [Action verb] [Object] - [Brief description]
...
```text

Each step should:

- Start with action verb (Write, Run, Check, Create)
- Be independently verifiable
- Have clear inputs and outputs

### Step 4: Enumerate Rationalizations

List every excuse people use to skip this skill:

```markdown
## Rationalizations

 | Excuse | Category | Reality Check |
 | -------- | ---------- | --------------- |
 | [excuse] | time pressure | [why it's wrong] |
 | [excuse] | overconfidence | [why it's wrong] |
```text

Be cynical. People are creative at avoiding good practices.

### Step 5: Create Contrasting Examples

For each major concept, show Good and Bad:

```markdown
<Good>
[example with code]

- Why this is good
- What principle it demonstrates

</Good>

<Bad>
[anti-example with code]

- What's wrong
- What principle it violates

</Bad>
```text

### Step 6: Build Verification Checklist

Create checkboxes for "done" criteria:

```markdown

- [ ] [Verifiable statement]
- [ ] [Verifiable statement]

```text

Each item should be binary (yes/no), not subjective.

### Step 7: Document Recovery Procedures

```markdown
## When Stuck

 | Problem | Solution |
 | --------- | ---------- |
 | [specific problem] | [specific solution] |
```text

Cover the most common ways the skill can fail.

## Template Sections Reference

Use the template at `templates/skill-template.md`. Required sections:

 | Section | Purpose | Required |
 | --------- | --------- | ---------- |
 | Frontmatter | Name, trigger description | Yes |
 | Iron Law | Core non-negotiable rule | Yes |
 | Core Principle | Quotable summary | Recommended |
 | When to Use | Activation triggers | Yes |
 | Workflow | Step-by-step process | Recommended |
 | Examples | Good/Bad contrasts | Yes |
 | Rationalizations | Anticipated excuses | Recommended |
 | Red Flags | Signs of violation | Recommended |
 | Verification Checklist | Done criteria | Yes |
 | When Stuck | Recovery procedures | Recommended |
 | Related Skills | Cross-references | Optional |

## Examples

<Good>
```markdown
---
name: code-review
description: External validation of code quality. Activates after implementation.
---

# Code Review Skill

External validation methodology.

## The Iron Law

```text
NEVER SELF-VALIDATE - USE EXTERNAL TOOLS ONLY
```text

## Workflow

### Step 1: Run Linters
[specific commands]

### Step 2: Run Tests
[specific commands]

...

## Examples

<Good>
[example showing tool-based review]
</Good>

<Bad>
[example showing self-validation]
</Bad>
```text

- Clear Iron Law (7 words)
- Specific workflow with commands
- Contrasting examples

</Good>

<Bad>
```markdown
# Code Quality Guidelines

Writing good code is important. Here are some tips:

- Try to use linters when you can
- Tests are helpful
- Consider security
- Clean code is better

Remember to be thoughtful about quality!
```text

- No Iron Law
- Vague "tips" instead of methodology
- No concrete workflow
- No examples
- No verification criteria

</Bad>

## Common Rationalizations

 | Excuse | Reality |
 | -------- | --------- |
 | "The methodology is too complex for a skill" | Break it into multiple skills. Each should be focused. |
 | "There are too many exceptions" | Your Iron Law is wrong. Find a more universal rule. |
 | "People will know what to do" | If they did, you wouldn't need the skill. Be explicit. |
 | "Examples are obvious" | What's obvious to you isn't obvious to everyone. Show both good and bad. |
 | "Rationalizations section is negative" | It's realistic. Anticipate how people avoid good practices. |
 | "This skill overlaps with another" | That's fine. Document the relationship in Related Skills. |

## Red Flags - STOP and Start Over

These indicate a poorly designed skill:

- Iron Law has "usually", "often", "when possible", or "consider"
- Iron Law is more than 10 words
- Can't think of any rationalizations (you haven't thought hard enough)
- Examples only show good patterns, not bad ones
- Workflow steps are vague ("think about X" instead of "write X")
- Verification checklist has subjective items ("code is clean")
- Skill tries to cover too many methodologies at once

**If you see these, refine the skill before publishing.**

## Verification Checklist

Before publishing a new skill:

- [ ] Iron Law is under 10 words, in CAPS, no exceptions
- [ ] Iron Law is memorable (can recall without looking)
- [ ] Workflow has 4-7 concrete, actionable steps
- [ ] At least 3 rationalizations documented with reality checks
- [ ] Good and Bad examples provided with explanations
- [ ] Examples include actual code, not just descriptions
- [ ] Red flags section identifies violation signs
- [ ] Verification checklist has binary (yes/no) items only
- [ ] "When Stuck" covers common failure modes
- [ ] Related skills cross-referenced where applicable
- [ ] Total length under 500 lines (for token efficiency)

## When Stuck

 | Problem | Solution |
 | --------- | ---------- |
 | Can't find Iron Law | The methodology isn't focused enough. Split into multiple skills. |
 | Too many steps | Combine related steps. Max 7. Core essence only. |
 | Can't think of bad examples | What would someone who's never heard of this do? That's the bad example. |
 | Skill too long | Cut secondary content. Keep Iron Law, Workflow, Examples, Checklist. |
 | Overlaps with existing skill | Check if existing skill should be extended instead. |
 | Not sure if it should be a skill | Ask: Does violating this cause real problems? Is there a clear alternative? |

## Skill Naming Guidelines

```markdown
## Good Names
- tdd (methodology name)
- systematic-debugging (adjective + domain)
- code-review (domain name)

## Bad Names
- better-code (vague)
- tips (not a methodology)
- misc-practices (unfocused)

```text

Names should be:

- Lowercase with hyphens
- 1-3 words
- Descriptive of the methodology
- Searchable/memorable

## File Structure

```text
framework/skills/
  skill-name/
    SKILL.md      # The skill definition (required)
    examples/     # Extended examples (optional)
    README.md     # Implementation notes (optional)
```text

## Related Skills

- `reviewer` - Review skills before publishing
- `brainstorming` - Generate skill ideas before narrowing
- `researcher` - Research methodologies before encoding as skills
