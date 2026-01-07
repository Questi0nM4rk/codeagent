---
name: reviewer
description: Code review methodology and best practices. Activates when reviewing code, pull requests, or conducting project audits. Provides structured review frameworks for different project sizes.
---

# Code Review Methodology Skill

Comprehensive code review knowledge for projects of all sizes.

## Core Principle

**Never self-validate.** Reviews must use external tools - linters, type checkers, security scanners, tests. LLMs miss 60-80% of errors when self-reviewing.

## Review Levels

### Level 1: Quick Review (Small Changes)
**Scope**: Single file, < 100 lines, bug fixes, small features
**Time**: 5-15 minutes
**Focus**: Correctness, obvious issues

```markdown
## Quick Review Checklist

### Correctness
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Error handling present

### Style
- [ ] Follows existing patterns
- [ ] No obvious code smells
- [ ] Naming is clear

### Tests
- [ ] Tests added/updated
- [ ] Tests pass

### Tools Run
- [ ] Linter: [result]
- [ ] Type check: [result]
```

### Level 2: Standard Review (Medium Changes)
**Scope**: Multiple files, 100-500 lines, features, refactors
**Time**: 30-60 minutes
**Focus**: Design, maintainability, performance

```markdown
## Standard Review Checklist

### Design
- [ ] Appropriate abstraction level
- [ ] Single responsibility maintained
- [ ] Dependencies are sensible
- [ ] No circular dependencies introduced

### Code Quality
- [ ] DRY - no unnecessary duplication
- [ ] YAGNI - no speculative generality
- [ ] Clear intent in code
- [ ] Comments explain "why" not "what"

### Security
- [ ] Input validation
- [ ] No hardcoded secrets
- [ ] Proper authentication/authorization
- [ ] SQL injection prevention
- [ ] XSS prevention

### Performance
- [ ] No obvious N+1 queries
- [ ] Appropriate data structures
- [ ] No memory leaks
- [ ] Async where appropriate

### Tests
- [ ] Unit tests for business logic
- [ ] Integration tests for APIs
- [ ] Edge cases covered
- [ ] Test names describe behavior

### Tools Run
- [ ] Linter: [result]
- [ ] Type check: [result]
- [ ] Security scan: [result]
- [ ] Test suite: [result]
```

### Level 3: Deep Review (Large Changes)
**Scope**: Architectural changes, new systems, 500+ lines
**Time**: 2-4 hours (split sessions)
**Focus**: Architecture, scalability, long-term maintenance

```markdown
## Deep Review Checklist

### Architecture
- [ ] Fits overall system architecture
- [ ] Clear boundaries defined
- [ ] API contracts well-defined
- [ ] Backward compatibility considered
- [ ] Migration path clear

### Scalability
- [ ] Database queries optimized
- [ ] Caching strategy appropriate
- [ ] Horizontal scaling possible
- [ ] Resource limits defined

### Reliability
- [ ] Failure modes identified
- [ ] Retry logic appropriate
- [ ] Circuit breakers where needed
- [ ] Monitoring/alerting hooks

### Maintainability
- [ ] Documentation updated
- [ ] Configuration externalized
- [ ] Feature flags for rollout
- [ ] Logging sufficient for debugging

### Security (Deep)
- [ ] Threat model updated
- [ ] Authentication flows secure
- [ ] Authorization comprehensive
- [ ] Data encryption at rest/transit
- [ ] Audit logging

### Testing (Comprehensive)
- [ ] Unit test coverage adequate
- [ ] Integration tests complete
- [ ] E2E tests for critical paths
- [ ] Performance tests if applicable
- [ ] Chaos testing considered

### Tools Run
- [ ] Linter: [result]
- [ ] Type check: [result]
- [ ] Security scan (deep): [result]
- [ ] Dependency audit: [result]
- [ ] Test suite with coverage: [result]
- [ ] Performance benchmarks: [result]
```

### Level 4: Project Audit (Enterprise)
**Scope**: Entire project or major subsystem
**Time**: Days to weeks
**Focus**: Technical debt, compliance, strategic alignment

```markdown
## Project Audit Framework

### Phase 1: Overview (Day 1)
- [ ] Architecture documentation review
- [ ] Dependency inventory
- [ ] Build system analysis
- [ ] CI/CD pipeline review

### Phase 2: Code Quality (Days 2-3)
- [ ] Static analysis (full)
- [ ] Code coverage analysis
- [ ] Complexity metrics
- [ ] Technical debt inventory

### Phase 3: Security (Days 4-5)
- [ ] SAST scan (Semgrep, SonarQube)
- [ ] Dependency vulnerability scan
- [ ] Secret scanning
- [ ] OWASP Top 10 check

### Phase 4: Infrastructure (Day 6)
- [ ] Container security
- [ ] Network policies
- [ ] Access controls
- [ ] Backup/recovery procedures

### Phase 5: Documentation (Day 7)
- [ ] API documentation completeness
- [ ] Runbook accuracy
- [ ] Architecture diagrams current
- [ ] Onboarding guide quality

### Deliverables
1. Executive summary
2. Detailed findings with severity
3. Remediation roadmap
4. Metrics baseline
```

## Review Documentation

### Finding Format

```markdown
### [SEVERITY] Title

**Location**: `file.ts:42`
**Category**: Security | Performance | Maintainability | Correctness

**Issue**:
[What's wrong]

**Impact**:
[Why it matters]

**Recommendation**:
[How to fix]

**Code Example**:
```language
// Before
[problematic code]

// After
[fixed code]
```
```

### Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| CRITICAL | Security vulnerability, data loss risk | Block merge, fix immediately |
| HIGH | Significant bug, performance issue | Fix before merge |
| MEDIUM | Code smell, maintainability concern | Should fix, can defer |
| LOW | Style, minor improvement | Nice to have |
| INFO | Observation, learning opportunity | No action required |

## Review Report Template

```markdown
# Code Review Report

**PR/Change**: [link or description]
**Reviewer**: [name]
**Date**: [date]
**Review Level**: Quick | Standard | Deep

## Summary

**Verdict**: APPROVED | CHANGES REQUIRED | BLOCKED

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

## Tool Results

| Tool | Status | Issues |
|------|--------|--------|
| Linter | ✅ | 0 |
| Types | ✅ | 0 |
| Security | ⚠️ | 2 |
| Tests | ✅ | 47/47 |

## Findings

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

## Recommendations
- [Suggestions for improvement]
```

## Context Management

### Avoid Context Bloat

For large reviews:
1. Review in chunks (max 500 lines per session)
2. Use separate agents for different aspects
3. Summarize findings between sessions
4. Keep running tally of issues

### Document as You Go

```markdown
## Review Progress

### Session 1: Core Logic
- Files: src/core/*.ts
- Duration: 45 min
- Findings: 2 medium, 1 low

### Session 2: API Layer
- Files: src/api/*.ts
- Duration: 30 min
- Findings: 1 high, 1 medium

### Remaining
- [ ] Tests
- [ ] Documentation
```

## Common Patterns to Catch

### Security
- Hardcoded credentials
- SQL injection (string concatenation in queries)
- Missing input validation
- Improper error messages (leaking info)
- Missing authentication/authorization

### Performance
- N+1 queries
- Missing database indexes
- Synchronous blocking in async context
- Memory leaks (event listeners, subscriptions)
- Unbounded data fetching

### Maintainability
- God classes/functions (too many responsibilities)
- Deep nesting (> 3 levels)
- Magic numbers/strings
- Duplicate code
- Missing error handling

## Language-Specific Tools

Load the appropriate domain skill for tool commands:
- TypeScript/JavaScript → frontend skill
- C# → dotnet skill
- Rust → rust skill
- C/C++ → cpp skill
- Python → python skill
- Lua → lua skill
- Bash → bash skill
- SQL → postgresql skill
