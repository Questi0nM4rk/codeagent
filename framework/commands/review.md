---
description: Validate implementation with external tools
---

# /review - External Validation

Independent validation using external tools. NEVER relies on self-assessment - every claim is backed by tool output.

## Usage

```
/review                 # Standard review
/review --security      # Extra security focus
/review --performance   # Include performance analysis
/review --stress        # Deep stress testing mode
```

## Agent Pipeline

```
Main Claude (Orchestrator)
      │
      └─► reviewer agent (opus)
              skills: [reviewer, domain skills based on file types]
              → Runs static analysis tools
              → Runs security scanners
              → Executes test suite
              → Checks pattern consistency
              → Returns: APPROVED or CHANGES REQUIRED
```

## What This Does

1. **Static Analysis**: Linting, formatting, build warnings
2. **Security Scan**: Vulnerability detection with Semgrep
3. **Test Verification**: Full test suite execution
4. **Memory Consistency**: Pattern matching against project standards
5. **Requirements Check**: Verify all /plan requirements met

## Validation Pipeline

The reviewer agent loads domain skills for language-specific tools:

### Static Analysis (from domain skills)

- **dotnet**: `dotnet format --verify-no-changes`, `dotnet build --warnaserror`
- **rust**: `cargo fmt --check`, `cargo clippy -- -D warnings`
- **cpp**: `clang-format --dry-run --Werror`, `clang-tidy`
- **python**: `ruff check`, `mypy`
- **frontend**: `eslint`, `tsc --noEmit`
- **lua**: `luacheck`, `stylua --check`
- **bash**: `shellcheck`, `shfmt -d`

### Security Scan

```bash
# Universal
semgrep --config auto --error .

# Language-specific
dotnet list package --vulnerable    # .NET
cargo audit                         # Rust
npm audit                           # JavaScript
bandit -r src/                      # Python
```

### Pattern Consistency

Uses MCPs to verify:
```
mcp__reflection__retrieve_episodes
    → Get established patterns from past implementations
```

## Output Format

### Approved

```markdown
## Review Results

### Summary
| Category | Status | Issues |
|----------|--------|--------|
| Static Analysis | PASS | 0 issues |
| Security | PASS | 0 findings |
| Tests | PASS | 52/52 passing |
| Patterns | PASS | 0 deviations |
| Requirements | PASS | 5/5 met |

### Tool Results
[Actual tool output for each category]

### Test Results
| Metric | Value |
|--------|-------|
| Total | 52 |
| Passed | 52 |
| Failed | 0 |
| Coverage | 84% |

---

## VERDICT: APPROVED

Code is ready for commit/PR.
Learner agent will extract patterns automatically.
```

### Changes Required

```markdown
## Review Results

### Summary
| Category | Status | Issues |
|----------|--------|--------|
| Static Analysis | FAIL | 2 issues |
| Security | WARN | 1 medium finding |
| Tests | PASS | 52/52 passing |
| Patterns | FAIL | 1 deviation |
| Requirements | PASS | 5/5 met |

---

## VERDICT: CHANGES REQUIRED

### Required Changes

| Priority | Location | Issue | Fix |
|----------|----------|-------|-----|
| HIGH | src/Auth/JwtService.cs:45 | Hardcoded secret | Move to configuration |
| MEDIUM | src/Auth/TokenValidator.cs:23 | Missing null check | Add validation |

### Security Findings

#### MEDIUM: Hardcoded Secret (CWE-798)
```
File: src/Auth/JwtService.cs:45
Code: private const string Secret = "my-secret-key";
Fix: Use IConfiguration to load from environment/secrets
```

### After Fixing
Run `/review` again to verify all issues resolved.
```

## Stress Test Mode (--stress)

Additional deep checks:

### Edge Cases
- [ ] Null inputs handled
- [ ] Empty collections handled
- [ ] Maximum values handled
- [ ] Concurrent access safe

### Error Scenarios
- [ ] External service failure
- [ ] Database unavailable
- [ ] Invalid input rejection
- [ ] Timeout handling

### Performance
- [ ] No N+1 queries
- [ ] No unbounded loops
- [ ] Reasonable memory usage
- [ ] Indexed queries

### Security Deep Dive
- [ ] SQL injection vectors
- [ ] XSS possibilities
- [ ] Auth bypass attempts
- [ ] Input validation complete

## A-MEM Integration

The reviewer agent uses A-MEM memory:

**Before reviewing:**
- Queries A-MEM for common issues in this codebase
- Checks for known code smell patterns
- References established review standards

**After review:**
- Stores significant issue patterns found
- A-MEM automatically links to related patterns

## Post-Review

On APPROVED:
- Learner agent automatically extracts patterns
- Stores success episode in reflection memory
- Updates A-MEM with new patterns (auto-links to existing)

On CHANGES REQUIRED:
- Fix listed issues
- Run `/review` again
- Repeat until APPROVED

## Notes

- Run /review after /implement (sequential) or /integrate (parallel)
- Security findings are NEVER "low priority"
- Missing tests for new code = automatic FAIL
- All tool output is real - not paraphrased or summarized
