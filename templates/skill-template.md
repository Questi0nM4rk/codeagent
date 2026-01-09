# Skill Template

Use this template when creating new skills for CodeAgent.

---

```markdown
---
name: skill-name
description: One-line description of when this skill activates. Be specific about triggers.
---

# Skill Name

Brief overview (1-2 sentences) explaining the skill's purpose.

## The Iron Law

```
UNMISTAKABLE CORE RULE IN CAPS
No exceptions. This is the non-negotiable principle.
```

## Core Principle

> "Quotable one-liner that captures the essence."

## When to Use

**Always:**
- Scenario 1
- Scenario 2

**Exceptions (ask human partner):**
- Exception 1 (why it's an exception)

## Workflow / Process

### Step 1: [Name]

Description of step.

### Step 2: [Name]

Description of step.

## Examples

<Good>
```language
// Good example code
// With proper formatting
```
- Clear explanation of why this is good
- What principle it demonstrates
</Good>

<Bad>
```language
// Bad example code
// That violates the skill
```
- What's wrong with this
- What principle it violates
</Bad>

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "It's too simple" | Simple code breaks too. The skill applies. |
| "I'll do it later" | Later never comes. Do it now. |
| "This is different" | No, it follows the same pattern. |

## Red Flags - STOP and Start Over

These indicate you've violated the skill:

- Red flag 1
- Red flag 2
- Red flag 3

If you see these, stop and restart the process.

## Verification Checklist

Before considering the task complete:

- [ ] Checkpoint 1
- [ ] Checkpoint 2
- [ ] Checkpoint 3
- [ ] Checkpoint 4

## When Stuck

| Problem | Solution |
|---------|----------|
| Problem 1 | How to resolve |
| Problem 2 | How to resolve |
| Problem 3 | How to resolve |

## Related Skills

- `related-skill-1` - Why it's related
- `related-skill-2` - Why it's related
```

---

## Template Sections Explained

### Frontmatter (Required)
- `name`: lowercase, hyphens for spaces
- `description`: When this skill activates (triggers)

### The Iron Law (Required)
- One unmistakable rule in a code block
- Written in CAPS for emphasis
- No exceptions - this is the core principle

### Core Principle (Optional)
- Quotable summary of the skill
- Used in quick reference

### When to Use (Required)
- Clear scenarios when skill applies
- Explicit exceptions with reasoning

### Workflow (Recommended)
- Step-by-step process
- Numbered or named steps

### Examples (Required)
- Use `<Good>` and `<Bad>` tags
- Include code examples
- Explain why each is good/bad

### Rationalizations (Recommended)
- Common excuses for not following skill
- Reality check for each

### Red Flags (Recommended)
- Signs you've violated the skill
- Triggers to stop and restart

### Verification Checklist (Required)
- Checkbox items for completion
- Concrete, verifiable items

### When Stuck (Recommended)
- Common problems
- Concrete solutions

### Related Skills (Optional)
- Cross-references to related skills
- Why they're related

---

## Formatting Guidelines

1. **Iron Laws**: Always in code blocks, CAPS, unmistakable
2. **Good/Bad**: Use literal `<Good>` and `<Bad>` tags (not code blocks)
3. **Tables**: Use for structured comparison data
4. **Checklists**: Use `- [ ]` for verification items
5. **Code Examples**: Include language identifier in code blocks
6. **Quotations**: Use `>` blockquotes for principles
7. **Length**: Keep under 500 lines for token efficiency
