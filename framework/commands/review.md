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

## What This Does

1. **Static Analysis**: Linting, formatting, build warnings
2. **Security Scan**: Vulnerability detection with Semgrep
3. **Test Verification**: Full test suite execution
4. **Memory Consistency**: Pattern matching against project standards
5. **Requirements Check**: Verify all /plan requirements met

## Validation Pipeline

### 1. Static Analysis

```bash
# .NET
dotnet format --verify-no-changes
dotnet build --warnaserror

# Rust
cargo fmt --check
cargo clippy -- -D warnings

# C/C++
clang-format --dry-run --Werror src/*.cpp
clang-tidy src/*.cpp -- -std=c++23

# Lua
luacheck . --codes
stylua --check .
```

### 2. Security Scan

```bash
# Universal security scan
semgrep --config auto --error .

# Language-specific
dotnet list package --vulnerable    # .NET
cargo audit                         # Rust

# Secrets detection
grep -r "password\|secret\|api_key" --include="*.cs" | grep -v test
```

### 3. Test Execution

```bash
# Full test suite
dotnet test --verbosity normal      # .NET
cargo test                          # Rust
ctest --test-dir build              # C/C++
busted                              # Lua
```

### 4. Memory Consistency

Query Letta:
- Does this code match established project patterns?
- Any conflicting conventions?

Query code-graph:
- Any broken dependencies?
- Any orphaned code?
- Any circular dependencies?

### 5. Requirements Verification

Load original /plan output:
- [ ] All acceptance criteria met
- [ ] All specified files modified
- [ ] All specified tests added
- [ ] No scope creep

## Output Format

```markdown
## Review Results

### Summary
| Category | Status | Issues |
|----------|--------|--------|
| Static Analysis | ✅ PASS | 0 issues |
| Security | ✅ PASS | 0 findings |
| Tests | ✅ PASS | 52/52 passing |
| Patterns | ✅ PASS | 0 deviations |
| Requirements | ✅ PASS | 5/5 met |

### Static Analysis
```
[tool output]
```

### Security Scan
| Severity | Count | Details |
|----------|-------|---------|
| Critical | 0 | - |
| High | 0 | - |
| Medium | 0 | - |
| Low | 0 | - |

### Test Results
| Metric | Value |
|--------|-------|
| Total | 52 |
| Passed | 52 |
| Failed | 0 |
| Coverage | 84% |

### Pattern Consistency
- Error handling: ✓ Matches project standard (Result<T>)
- Naming: ✓ Follows conventions
- Structure: ✓ Consistent with existing code

### Requirements
- [x] JWT validation implemented
- [x] Token refresh working
- [x] Tests added for all paths
- [x] Error handling complete
- [x] Documentation updated

---

## VERDICT: ✅ APPROVED

### Notes
- All checks passed
- Code is ready for commit/PR
- @learner will extract patterns automatically
```

## Failure Output

```markdown
## Review Results

### Summary
| Category | Status | Issues |
|----------|--------|--------|
| Static Analysis | ❌ FAIL | 2 issues |
| Security | ⚠️ WARN | 1 medium finding |
| Tests | ✅ PASS | 52/52 passing |
| Patterns | ❌ FAIL | 1 deviation |
| Requirements | ✅ PASS | 5/5 met |

---

## VERDICT: ❌ CHANGES REQUIRED

### Required Changes

| Priority | Location | Issue | Fix |
|----------|----------|-------|-----|
| HIGH | src/Auth/JwtService.cs:45 | Hardcoded secret in code | Move to configuration |
| MEDIUM | src/Auth/TokenValidator.cs:23 | Missing null check | Add validation |
| MEDIUM | src/Auth/JwtService.cs | Uses exceptions, project uses Result<T> | Refactor to Result pattern |

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

Additional checks when stress testing:

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

## Notes

- Run /review after /implement (sequential) or /integrate (parallel)
- Security findings are NEVER "low priority"
- Missing tests for new code = automatic FAIL
- @learner triggers automatically on APPROVED verdict
- If CHANGES REQUIRED, fix and run /review again
