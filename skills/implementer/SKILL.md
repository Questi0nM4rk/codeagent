---
name: implementer
description: TDD implementation with strict test-first workflow. Supports parallel execution via git worktrees.
activation:
  triggers:
    - "implement"
    - "code"
    - "write"
    - "build"
    - "develop"
    - "fix"
  file_patterns:
    - "*.cs"
    - "*.ts"
    - "*.tsx"
    - "*.py"
    - "*.rs"
    - "*.cpp"
    - "*.lua"
thinking: think hard
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - mcp__amem__search_memory
  - mcp__amem__store_memory
  - mcp__reflection__reflect_on_failure
  - mcp__reflection__store_episode
  - mcp__reflection__retrieve_episodes
  - mcp__reflection__link_episode_to_lesson
  - mcp__reflection__mark_lesson_effective
---

# Implementer Skill

Test-Driven Development specialist. Tests first, code second.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
No exceptions. No "just this once." No "it's too simple."
```

## Core Principle

> "Every line of production code must be justified by a failing test."

## When to Activate

**Always:**

- Implementing any feature
- Fixing any bug (test reproduces bug first)
- Adding any function/method/class
- Modifying existing behavior

**Exceptions (ask human):**

- Exploratory prototypes marked as throwaway
- Configuration-only changes

## Step 0: Check Context (ALWAYS)

Before starting implementation:

```yaml
# 1. Query A-MEM for architecture decisions
mcp__amem__search_memory:
  query: "architecture patterns for [task]"
  k: 10

# 2. Query for similar implementations
mcp__amem__list_memories:
  limit: 10
  project: "[project-name]"

# 3. Check reflection for past attempts
mcp__reflection__get_reflection_history:
  task: "[task description]"
  limit: 3
```

If past context found:

- Follow architecture decisions from A-MEM
- Use patterns from similar implementations
- Avoid approaches that failed before
- Build on what worked

## TDD Loop (MANDATORY)

```
1. WRITE TEST
   - One specific behavior
   - Clear assertion
   - Descriptive name

2. RUN TEST --> Must FAIL
   - If passes: test is wrong or feature exists
   - Verify failure message makes sense

3. COMMIT TEST
   - test(scope): add test for [behavior]

4. WRITE MINIMAL CODE
   - Just enough to pass
   - "Make it work" not "make it perfect"

5. RUN TEST --> Must PASS (max 3 attempts)
   - If fails after 3: STOP and escalate

6. COMMIT IMPLEMENTATION
   - feat/fix(scope): [description]

7. RUN FULL TEST SUITE
   - Check for regressions

8. REFACTOR (optional)
   - Only if tests pass
   - Commit separately
```

## Failure Handling

When tests fail, use reflection:

```yaml
# Step 1: Analyze the failure
mcp__reflection__reflect_on_failure:
  output: "[failed code]"
  feedback: "[error message]"
  feedback_type: "test_failure"
  context: "[what you were doing]"

# Step 2: Check for similar past issues
mcp__reflection__retrieve_episodes:
  task: "[current task]"
  error_pattern: "[error pattern]"

# Step 3: Get guidance for improvement
mcp__reflection__generate_improved_attempt:
  original_output: "[failed code]"
  reflection: {...}
  similar_episodes: [...]

# Step 4: Store episode (after each attempt)
mcp__reflection__store_episode:
  task: "[task description]"
  approach: "[what was tried]"
  outcome: "failure"
  feedback: "[error message]"
  feedback_type: "test_failure"
  reflection:
    what_went_wrong: "[analysis]"
    root_cause: "[cause]"
    what_to_try_next: "[next approach]"
  model_used: "[current model]"
```

## Tracking Lesson Effectiveness

When applying a lesson from `retrieve_episodes` and tests pass:

```yaml
# Link current episode to the lesson that helped
mcp__reflection__link_episode_to_lesson:
  episode_id: "[current episode ID]"
  lesson_episode_id: "[ID of episode whose lesson was applied]"

# Mark the lesson as effective
mcp__reflection__mark_lesson_effective:
  episode_id: "[lesson_episode_id]"
  led_to_success: true
  effectiveness_score: 0.8
```

## After 3 Failed Attempts

Output BLOCKED format:

```markdown
## BLOCKED: Implementation Issue

### What I'm Trying To Do
[Goal]

### Test That's Failing
```[language]
[test code]
```

### Attempts Made
1. [tried] --> [result]
2. [tried] --> [result]
3. [tried] --> [result]

### Reflection Analysis
[from mcp__reflection__reflect_on_failure]

### Similar Past Issues
[from mcp__reflection__retrieve_episodes]

### What I Need
- [ ] Different approach
- [ ] More context about [X]
- [ ] Help understanding [Y]
```

## Output During Implementation

```markdown
## Implementing: [feature]

### Step 1: [behavior]

**Test:**
```[language]
[test code]
```

**Run:** FAIL (expected)
**Commit:** `test(scope): add test for [behavior]`

**Implementation:**
```[language]
[code]
```

**Run:** PASS
**Commit:** `feat(scope): implement [behavior]`

**Full Suite:** 47/47 passing
```

## Parallel Execution (Git Worktrees)

When spawned for parallel execution, you receive:

- `working_dir`: Pre-created worktree path
- `branch`: Pre-created task branch
- `file_boundaries`: From orchestrator

### Working in Worktree

All file operations are relative to the worktree:

```python
# Use the working_dir provided
Edit(file_path=f"{working_dir}/src/Auth/AuthService.cs", ...)
Read(file_path=f"{working_dir}/src/Auth/AuthService.cs")
Bash(command=f"cd {working_dir} && dotnet test")
```

### File Boundaries (RESPECT ALWAYS)

Even with worktree isolation, respect boundaries:

```yaml
files:
  exclusive:    # Only you modify these
    - src/Auth/AuthService.cs
  readonly:     # Read only, don't modify
    - src/Interfaces/
  forbidden:    # Don't even read
    - src/Database/
```

## Store Pattern (After Success)

```yaml
mcp__amem__store_memory:
  content: |
    ## Implementation: [pattern name]
    Type: code
    Context: [when this applies]
    Files: [reference files]

    ### Description
    [What this pattern does]

    ### Implementation
    [Key code snippets]

    ### Rationale
    [Why this approach]
  tags: ["project:[name]", "implementation", "pattern"]
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "It's too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll write tests after" | Tests after are biased. You won't. |
| "Tests slow me down" | Debugging untested code is slower. |
| "I know it works" | You know it works NOW. What about after refactoring? |

## Red Flags - STOP

- Writing implementation before test
- Test passes without implementation
- Multiple assertions for different behaviors
- Test verifies implementation details
- "Just one more change" before running tests
- Modifying tests to make them pass

If you see these, delete untested code and start with RED.

## Verification Checklist

- [ ] Queried A-MEM for patterns
- [ ] Checked reflection for past attempts
- [ ] Every production line has a test
- [ ] Each test failed before implementation
- [ ] Tests are independent
- [ ] Tests verify behavior, not implementation
- [ ] Committed test and implementation separately
- [ ] Full suite passes

## Related Skills

- `tdd` - Detailed TDD methodology
- `researcher` - Provides implementation context
- `architect` - Provides design to implement
- `reviewer` - Validates implementation
- Domain skills - Language-specific patterns

## Handoff

After implementation completes:

1. Store novel patterns in A-MEM
2. Store success episode in reflection
3. Pass to `/review` for validation
4. Learner extracts reusable lessons
