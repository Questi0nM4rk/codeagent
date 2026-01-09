---
name: systematic-debugging
description: Scientific debugging methodology. Activates when investigating bugs, unexpected behavior, or failures. Enforces hypothesis-driven debugging with reproduction before fix.
---

# Systematic Debugging Skill

Scientific method applied to bug investigation. Every fix must be preceded by reproduction and hypothesis validation.

## The Iron Law

```
REPRODUCE BEFORE FIX - NO GUESSING
Never attempt a fix without first reproducing the bug. Guessing wastes time and introduces new bugs.
```

## Core Principle

> "A bug you can't reproduce is a bug you can't verify you've fixed."

## When to Use

**Always:**
- Investigating any reported bug
- Unexpected test failures
- Production incidents
- Behavior that differs from specification
- "It works on my machine" situations

**Exceptions (ask human partner):**
- Typos obvious from error message (still verify fix)
- Build/config errors with clear solution (still test after)

## The Debugging Scientific Method

```
OBSERVE → HYPOTHESIZE → PREDICT → TEST → CONCLUDE

1. OBSERVE: Gather facts, reproduce the bug
2. HYPOTHESIZE: Form testable explanation
3. PREDICT: What would confirm/deny hypothesis?
4. TEST: Run experiment to verify
5. CONCLUDE: Accept, reject, or refine hypothesis
```

## Workflow

### Step 1: Reproduce (MANDATORY)

Before anything else, reproduce the bug reliably.

Requirements:
- Write down exact steps to reproduce
- Confirm bug occurs consistently
- Identify minimal reproduction case
- Document environment (OS, versions, config)

```markdown
## Bug Reproduction

**Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected**: [What should happen]
**Actual**: [What happens]

**Environment**:
- OS: [version]
- Language: [version]
- Dependencies: [relevant versions]

**Minimal Reproduction**: [Smallest code/steps that trigger bug]
```

### Step 2: Gather Evidence

Collect facts without interpretation:
- Error messages (full stack trace)
- Logs around the failure
- Input values that trigger bug
- Recent changes (git log, git bisect)

```bash
# Find recent changes
git log --oneline -20

# Bisect to find breaking commit
git bisect start
git bisect bad HEAD
git bisect good <last-known-good>
# ... test each commit until found
```

### Step 3: Form Hypotheses

Generate multiple possible causes (minimum 2-3):

```markdown
## Hypotheses

1. **Race condition in auth flow**
   - Evidence: Only fails under load
   - Test: Add logging, check timing

2. **Null check missing in user service**
   - Evidence: NullPointerException in stack trace
   - Test: Check if user object is null before access

3. **Database connection pool exhausted**
   - Evidence: Timeout errors in logs
   - Test: Monitor connection count
```

### Step 4: Test Hypotheses

Test ONE hypothesis at a time. Make predictions before testing.

```markdown
## Hypothesis Test: Race condition in auth flow

**Prediction**: If race condition, adding mutex will prevent failure
**Experiment**: Add lock around token generation
**Result**: Bug still occurs
**Conclusion**: REJECTED - not a race condition
```

### Step 5: Fix and Verify

Only after confirming root cause:
1. Write test that reproduces bug (should fail)
2. Implement fix
3. Test passes
4. Verify in original reproduction scenario

## Debugging Strategies

### Binary Search (Bisecting)

```bash
# Code bisect - comment out half the code
# If bug persists: bug is in remaining half
# If bug disappears: bug is in removed half
# Repeat until isolated

# Git bisect for finding breaking commit
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Git will checkout commits for you to test
```

### Rubber Duck Debugging

Explain the problem out loud (or in writing):
1. State what the code SHOULD do
2. Walk through what it ACTUALLY does, line by line
3. The discrepancy often reveals itself

### Strategic Logging

```python
# BAD: Random print statements
print("here")
print("here2")
print(x)

# GOOD: Structured diagnostic logging
logger.debug(f"[AUTH] validate_token called: user_id={user_id}, token_length={len(token)}")
logger.debug(f"[AUTH] token_valid={is_valid}, expires_at={expires_at}")
logger.debug(f"[AUTH] cache_hit={cache_hit}, lookup_time_ms={elapsed}")
```

### Simplify and Isolate

1. Remove complexity until bug disappears
2. Add back one thing at a time
3. Bug reappears = found the culprit

## Examples

<Good>
```markdown
## Bug Investigation: Login fails intermittently

### Reproduction
**Steps:**
1. Clear cookies
2. Navigate to /login
3. Enter valid credentials
4. Click submit rapidly 3x

**Result**: 500 error ~30% of time
**Minimal case**: Concurrent login requests from same session

### Evidence
- Error log: "Duplicate key constraint on sessions table"
- Occurs only with rapid clicks (race condition likely)
- git bisect points to commit abc123 (session refactor)

### Hypotheses
1. Race condition creating duplicate sessions
2. Transaction isolation level too weak
3. Missing unique constraint check before insert

### Test: Hypothesis 1 - Race condition
**Prediction**: Adding mutex around session creation will prevent duplicates
**Experiment**: Wrapped session creation in lock
**Result**: Bug no longer reproduces after 100 attempts
**Conclusion**: CONFIRMED - race condition in session creation

### Fix
1. Added failing test for concurrent session creation
2. Implemented distributed lock using Redis
3. Test passes, manual reproduction confirms fix

### Root Cause
Session refactor in abc123 removed the lock that prevented concurrent session
creation for the same user.
```
- Reproduction documented first
- Multiple hypotheses considered
- Predictions made before testing
- Only one variable changed at a time
- Fix verified with test and manual reproduction
</Good>

<Bad>
```markdown
## Bug: Login not working

I think the problem is in the auth service. Let me try changing the timeout.

[makes change]

Hmm, still broken. Maybe it's the database connection?

[makes another change]

Actually I'll just rewrite this whole function to be cleaner.

[rewrites function]

Seems to work now! Closing the ticket.
```
- No reproduction documented
- Guessing instead of hypothesizing
- Multiple changes at once
- No verification that fix actually works
- Root cause unknown
</Bad>

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I know what the bug is" | Then prove it. Write the reproduction first. |
| "It's faster to just try things" | Guessing creates new bugs. Systematic is faster long-term. |
| "Can't reproduce locally" | Match the environment. Use containers, same data, same config. |
| "It's obviously this line" | If it were obvious, it wouldn't be a bug. Verify. |
| "I'll document after I fix it" | You'll forget critical details. Document as you go. |
| "The user described it wrong" | Don't assume. Reproduce exactly what they described. |

## Red Flags - STOP and Start Over

These indicate you're guessing, not debugging:

- Made a code change without reproducing bug first
- Trying multiple "fixes" without testing hypotheses
- Can't describe the bug in precise, reproducible terms
- Changed more than one thing between tests
- Declared "fixed" without verifying original reproduction case passes
- Skipped writing a failing test that captures the bug
- "Shotgun debugging" - changing things randomly hoping something works

**If you catch yourself doing these, STOP. Go back to reproduction.**

## Verification Checklist

Before declaring a bug fixed:

- [ ] Bug reproduction documented with exact steps
- [ ] Minimal reproduction case identified
- [ ] At least 2-3 hypotheses generated
- [ ] Each hypothesis tested independently
- [ ] Root cause identified and documented
- [ ] Failing test written that reproduces bug
- [ ] Fix implemented (test now passes)
- [ ] Original reproduction scenario verified manually
- [ ] No regression in related functionality

## When Stuck

| Problem | Solution |
|---------|----------|
| Can't reproduce | Match exact environment. Check versions, config, data. |
| All hypotheses rejected | Gather more evidence. Look at different layer (network, OS, hardware). |
| Bug is intermittent | Add extensive logging. Run in loop until it occurs. Check for race conditions. |
| Too much code to search | Use git bisect to find breaking commit. Binary search through code. |
| No error message | Add assertions. Check return values. Enable debug logging. |
| "Works on my machine" | Compare environments bit by bit. Use containers for consistency. |

## Debugging Toolkit

```bash
# Git bisect for finding breaking commit
git bisect start && git bisect bad HEAD && git bisect good <tag>

# Strace/ltrace for system calls (Linux)
strace -f -e trace=file ./program

# Network debugging
tcpdump -i any port 8080
curl -v http://localhost:8080/endpoint

# Memory debugging
valgrind --leak-check=full ./program

# Performance profiling
perf record -g ./program && perf report
```

## Documentation Template

```markdown
# Bug Report: [Title]

## Summary
[One sentence description]

## Reproduction
**Steps:**
1. [step]

**Expected:** [behavior]
**Actual:** [behavior]

**Environment:**
- [relevant versions]

## Investigation

### Evidence
- [fact 1]
- [fact 2]

### Hypotheses Tested
| Hypothesis | Prediction | Result | Conclusion |
|------------|------------|--------|------------|
| [h1] | [prediction] | [result] | CONFIRMED/REJECTED |

### Root Cause
[What actually caused the bug]

## Fix
- [PR/commit link]
- [Test that catches bug]

## Prevention
[How to prevent similar bugs]
```

## Related Skills

- `tdd` - Write failing test to capture bug before fixing
- `reviewer` - Use external tools to validate fix doesn't introduce regressions
- `researcher` - When investigation requires understanding unfamiliar code
