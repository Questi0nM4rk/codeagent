---
name: reviewer
description: Code review specialist using external validation tools. Activates when reviewing code, validating implementations, or checking for issues. Never relies on self-assessment.
---

# Code Review Skill

External validation methodology for code quality. Reviews must use tools - never self-assess.

## The Iron Law

```text
NEVER SELF-VALIDATE - USE EXTERNAL TOOLS ONLY
LLMs miss 60-80% of errors when self-reviewing. Run linters, tests, security scanners.
```text

## Core Principle

> "If you wrote it, you can't objectively review it. Let the tools decide."

## When to Use

**Always:**

- After implementing any feature (run tests, linters)
- Before committing code (pre-commit checks)
- Before merging PRs (full review suite)
- When asked to review code

**Exceptions (ask human partner):**

- Quick syntax checks (still run linter anyway)
- Documentation-only changes (still check links/spelling)

## Review Levels

 | Level | Scope | Time | Focus |
 | ------- | ------- | ------ | ------- |
 | Quick | < 100 lines, single file | 5-15 min | Correctness |
 | Standard | 100-500 lines, multiple files | 30-60 min | Design + Security |
 | Deep | 500+ lines, architectural | 2-4 hours | Scalability + Reliability |
 | Audit | Entire project | Days | Technical debt + Compliance |

## Workflow

### Step 1: Run External Tools First

Before ANY manual review, run appropriate tools:

```bash
# Language-agnostic
shellcheck *.sh              # Shell scripts
yamllint *.yml               # YAML files

# TypeScript/JavaScript
npx eslint --ext .ts,.tsx .
npx tsc --noEmit

# Python
ruff check .
mypy .

# Rust
cargo clippy -- -D warnings
cargo test

# C#
dotnet build --warnaserror
dotnet test

# Security (all languages)
semgrep --config auto .
```text

### Step 2: Analyze Tool Output

Document ALL findings. Don't dismiss warnings.

### Step 3: Targeted Manual Review

Only review what tools can't catch:

- Business logic correctness
- Design appropriateness
- API contracts

### Step 4: Document Findings

Use the finding format below for every issue.

## Examples

<Good>
```markdown
## Review Report

### Tool Results
 | Tool | Status | Issues |
 | ------ | -------- | -------- |
 | ESLint | PASS | 0 |
 | TypeScript | PASS | 0 |
 | Semgrep | WARN | 2 findings |
 | Jest | PASS | 47/47 tests |

### Security Findings

#### [HIGH] SQL Injection Risk
**Location**: `src/api/users.ts:42`
**Tool**: Semgrep (rule: typescript.lang.security.audit.sqli)

**Issue**: String concatenation in SQL query
**Impact**: Allows attackers to extract/modify database

**Code**:
```typescript
// Before (vulnerable)
const query = `SELECT * FROM users WHERE id = ${userId}`;

// After (parameterized)
const query = 'SELECT * FROM users WHERE id = $1';
const result = await db.query(query, [userId]);
```text

**Verdict**: CHANGES REQUIRED (1 HIGH severity)
```text

- Used external tools first
- Documented tool that found the issue
- Clear before/after fix
- Specific file:line reference

</Good>

<Bad>
```markdown
## Review

I looked at the code and it seems fine. The logic looks correct and I don't
see any obvious bugs. The code is well-structured and follows good practices.

Approved!
```text

- No tools run
- Subjective "seems fine" assessment
- No specific findings
- Self-validation (LLM reviewing LLM code)

</Bad>

## Finding Format

```markdown
### [SEVERITY] Title

**Location**: `file.ts:42`
**Category**: Security | Performance | Maintainability | Correctness
**Tool**: [which tool found this, or "Manual review"]

**Issue**: [What's wrong]
**Impact**: [Why it matters]

**Recommendation**:
[How to fix]

**Code**:
```language
// Before
[problematic code]

// After
[fixed code]
```

```text

## Severity Levels

 | Level | Description | Action |
 | ------- | ------------- | -------- |
 | CRITICAL | Security vulnerability, data loss | Block merge, fix NOW |
 | HIGH | Significant bug, security issue | Fix before merge |
 | MEDIUM | Code smell, maintainability | Should fix |
 | LOW | Style, minor improvement | Nice to have |
 | INFO | Learning opportunity | No action |

## Common Rationalizations

 | Excuse | Reality |
 | -------- | --------- |
 | "The linter is too strict" | Configure it properly, don't ignore it. |
 | "It's just a warning" | Warnings become bugs. Fix them. |
 | "I tested it manually" | Manual testing misses edge cases. Write tests. |
 | "Security scan has false positives" | Verify each one. False negatives are worse. |
 | "I know this code is correct" | Then prove it with tests. |
 | "No time for full review" | Quick review is better than none. Run tools at minimum. |

## Red Flags - STOP and Start Over

These indicate you're self-validating instead of using tools:

- "Looks good to me" without tool output
- Approving without running tests
- Dismissing linter warnings without fixing
- Skipping security scan "this time"
- "I already know this code works"
- Manual code inspection without tool backup
- Approving your own implementation without external check

**If you catch yourself doing these, STOP. Run the tools.**

## Verification Checklist

Before marking any review complete:

- [ ] Linter ran with zero errors/warnings (or documented exceptions)
- [ ] Type checker passed (where applicable)
- [ ] All tests pass
- [ ] Security scanner ran (semgrep or equivalent)
- [ ] Each finding has file:line reference
- [ ] Each finding has severity level
- [ ] Tool that found each issue is documented
- [ ] Before/after code shown for fixes

## Required Tools by Language

 | Language | Linter | Types | Security | Tests |
 | ---------- | -------- | ------- | ---------- | ------- |
 | TypeScript | ESLint | tsc | Semgrep | Jest/Vitest |
 | Python | Ruff | mypy | Semgrep | pytest |
 | Rust | clippy | rustc | cargo-audit | cargo test |
 | C# | dotnet build | Roslyn | Semgrep | dotnet test |
 | C/C++ | cppcheck | N/A | Semgrep | ctest |
 | Lua | luacheck | N/A | Semgrep | busted |
 | Bash | shellcheck | N/A | shellcheck | bats |
 | SQL | sqlfluff | N/A | Semgrep | pgTap |

## When Stuck

 | Problem | Solution |
 | --------- | ---------- |
 | Tool not installed | Install it. Don't skip the check. |
 | Too many warnings | Fix incrementally. Start with errors, then warnings. |
 | Don't understand finding | Look up the rule. Tools explain why. |
 | False positive | Document and suppress with comment explaining why. |
 | Can't run tests | Fix the test setup first. Untestable code can't be reviewed. |
 | Review too large | Split into sessions. Max 500 lines per review. |

## Context Management for Large Reviews

```markdown
## Review Progress

### Session 1: Core Logic
- Files: src/core/*.ts
- Tools: ESLint ✓, tsc ✓, Jest ✓
- Findings: 2 MEDIUM

### Session 2: API Layer
- Files: src/api/*.ts
- Tools: ESLint ✓, tsc ✓, Semgrep ✓
- Findings: 1 HIGH, 1 MEDIUM

### Remaining
- [ ] Tests coverage check
- [ ] Documentation review

```text

## Report Template

```markdown
# Code Review Report

**PR/Change**: [link]
**Reviewer**: [name]
**Date**: [date]
**Level**: Quick | Standard | Deep

## Summary

**Verdict**: APPROVED | CHANGES REQUIRED | BLOCKED

## Tool Results

 | Tool | Status | Issues |
 | ------ | -------- | -------- |
 | Linter | ✅/❌ | N |
 | Types | ✅/❌ | N |
 | Security | ✅/❌ | N |
 | Tests | ✅/❌ | N/M |

## Findings by Severity

### Critical
[none or list]

### High
[none or list]

### Medium
[none or list]

### Low
[none or list]

## Positive Notes
- [What was done well]

```text

## Related Skills

- `tdd` - Ensures tests exist for review to validate
- `systematic-debugging` - When review finds bugs to investigate
- `implementer` - Produces code that gets reviewed
