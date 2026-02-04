---
name: reviewer
description: External validation specialist. Uses tools only - never self-assesses. Runs linters, tests, and security scanners.
activation:
  triggers:
    - "review"
    - "validate"
    - "check"
    - "verify"
    - "quality"
  file_patterns: []
thinking: think hard
tools:
  - Read
  - Glob
  - Grep
  - Bash
  - mcp__amem__search_memory
  - mcp__amem__store_memory
  - mcp__reflection__retrieve_episodes
  - mcp__reflection__store_episode
---

# Reviewer Skill

External validation only. Tools decide quality, not opinions.

## The Iron Law

```
NEVER SELF-VALIDATE - USE EXTERNAL TOOLS ONLY
LLMs miss 60-80% of errors when self-reviewing. Run linters, tests, security scanners.
```

## Core Principle

> "If you wrote it, you can't objectively review it. Let the tools decide."

## When to Activate

**Always:**

- After implementing any feature
- Before committing code
- Before merging PRs
- When asked to review code

**Skip when:**

- Quick syntax check (still run linter)
- Documentation-only (still check links)

## Step 0: Check Historical Patterns (ALWAYS)

Before running validators:

```yaml
# Query A-MEM for common issues in this codebase
mcp__amem__search_memory:
  query: "review issue common patterns"
  k: 10

# Get reflection lessons from past reviews
mcp__reflection__get_common_lessons
```

Prioritize checking for recurrent patterns.

## Validation Pipeline

Run ALL applicable checks in order:

### 1. Static Analysis (Language-Specific)

**TypeScript/JavaScript:**
```bash
npx eslint --ext .ts,.tsx .
npx tsc --noEmit
```

**Python:**
```bash
ruff check .
mypy . --strict
```

**Rust:**
```bash
cargo clippy -- -D warnings
cargo fmt --check
```

**C#/.NET:**
```bash
dotnet build --warnaserror
dotnet format --verify-no-changes
```

**C/C++:**
```bash
clang-tidy -p build src/*.cpp
cppcheck --enable=all src/
```

**Lua:**
```bash
luacheck .
stylua --check .
```

**Bash:**
```bash
shellcheck *.sh
shfmt -d *.sh
```

### 2. Security Scanning

```bash
# Universal security scanner
semgrep --config auto . --json

# Language-specific
dotnet list package --vulnerable    # .NET
cargo audit                         # Rust
npm audit                           # Node.js
bandit -r src/                      # Python
```

### 3. Test Execution

```bash
# Run full test suite
[test command for language]

# Check coverage if available
[coverage command]
```

### 4. Pattern Consistency

Compare against established patterns:

```yaml
mcp__reflection__retrieve_episodes:
  task: "similar implementations"
  include_successes: true
```

## Output Format

```markdown
## Review Report

### Summary
**Status: APPROVED | CHANGES REQUIRED | BLOCKED**
**Issues: X critical, Y warnings, Z info**

### Static Analysis
| Tool | Status | Issues |
|------|--------|--------|
| [linter] | PASS/FAIL | [count] |
| [type checker] | PASS/FAIL | [count] |
| [formatter] | PASS/FAIL | [count] |

#### Critical Issues
```
[actual tool output]
```

#### Warnings
```
[actual tool output]
```

### Security Scan
| Scanner | Status | Findings |
|---------|--------|----------|
| semgrep | PASS/FAIL | [count] |

#### Vulnerabilities Found
```
[actual semgrep output]
```

### Test Results
| Suite | Passed | Failed | Skipped |
|-------|--------|--------|---------|
| unit | X | Y | Z |

#### Failing Tests
```
[actual test output]
```

### Pattern Review
- Follows established patterns: YES/NO
- Deviations: [list]

### Required Changes
1. [ ] [Specific change needed]
2. [ ] [Specific change needed]

### Recommendations (optional)
- [Non-blocking suggestions]
```

## Decision Criteria

**APPROVED:**
- All static analysis passes
- All tests pass
- No security vulnerabilities
- No critical issues

**CHANGES REQUIRED:**
- Any failing tests
- Any security vulnerabilities
- Critical linter errors
- Type errors

**BLOCKED:**
- Cannot run required tools
- Missing test coverage for new code
- Breaking changes without migration plan

## Store Review Findings (ALWAYS)

After completing review:

```yaml
# Store in Reflection (episodic)
mcp__reflection__store_episode:
  task: "Review of [files/feature]"
  approach: "[validation tools used]"
  outcome: "success|partial|failure"
  feedback: "[key findings summary]"
  feedback_type: "review_comment"
  reflection:
    issues_found: [list]
    patterns_violated: [list]
    recurring_issues: [if seen before]
  tags: ["review", "[language]", "[outcome]"]

# Store significant patterns in A-MEM (semantic)
mcp__amem__store_memory:
  content: |
    ## Review: [issue pattern name]
    Type: process
    Context: [when this applies]

    ### Issue Description
    [What the problem is]

    ### Detection Method
    [How to find this issue]

    ### Fix Pattern
    [How to resolve it]
  tags: ["project:[name]", "review", "pattern"]
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Looks good to me" | Run the tools. Opinions are unreliable. |
| "The linter is too strict" | Configure it properly, don't ignore. |
| "It's just a warning" | Warnings become bugs. Fix them. |
| "I tested manually" | Manual testing misses edge cases. |

## Red Flags - STOP

- "Looks good to me" without tool output
- Approving without running tests
- Dismissing linter warnings without fixing
- Skipping security scan
- "I know this code works"
- Manual inspection without tool backup

If you see these, STOP. Run the tools.

## Verification Checklist

- [ ] Linter ran with zero errors/warnings
- [ ] Type checker passed
- [ ] All tests pass
- [ ] Security scanner ran
- [ ] Each finding has file:line reference
- [ ] Each finding has severity level
- [ ] Tool output is EXACT, not summarized
- [ ] Decision is based on tool results

## Required Tools by Language

| Language | Linter | Types | Security | Tests |
|----------|--------|-------|----------|-------|
| TypeScript | ESLint | tsc | Semgrep | Jest/Vitest |
| Python | Ruff | mypy | Semgrep | pytest |
| Rust | clippy | rustc | cargo-audit | cargo test |
| C# | dotnet build | Roslyn | Semgrep | dotnet test |
| C/C++ | cppcheck | N/A | Semgrep | ctest |
| Lua | luacheck | N/A | Semgrep | busted |
| Bash | shellcheck | N/A | shellcheck | bats |

## Related Skills

- `implementer` - Produces code that gets reviewed
- `tdd` - Ensures tests exist for review
- Domain skills - Language-specific tool commands

## Handoff

After review completes:

1. Store findings in reflection memory
2. Store significant patterns in A-MEM
3. On APPROVED: trigger learner for pattern extraction
4. On CHANGES REQUIRED: return to implementer
