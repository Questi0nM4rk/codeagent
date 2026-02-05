Comment Types & Severity Levels

1. Issue Comments

**Severity:** Major | Minor | Nitpick
**Category:** <category_name>

<description_of_issue>

<optional_code_suggestion>

Severity Levels:

    Major: Security vulnerabilities, data loss risks, system crashes, logic errors, significant bugs
    Minor: Code quality issues, maintainability concerns, potential bugs, minor improvements
    Nitpick: Style inconsistencies, formatting, minor optimization opportunities

2. Suggestion Comments

**Suggestion:** <improvement_type>

<description_of_suggestion>

<optional_code_example>

Suggestion Types:

    Performance optimization
    Code refactoring
    Best practice alignment
    Readability improvement
    Maintainability enhancement

3. Praise/Positive Comments

**Positive:** <aspect>

<description_of_good_practice>

4. Question Comments

**Question:** <topic>

<clarifying_question>

Common Categories

    Security: Authentication, authorization, data exposure, injection vulnerabilities
    Performance: Inefficient algorithms, resource leaks, scaling issues
    Error Handling: Missing error checks, poor error messages, unhandled exceptions
    Testing: Missing tests, inadequate coverage, test quality
    Documentation: Missing docs, unclear comments, outdated information
    Code Quality: Complexity, duplication, naming, structure
    Type Safety: Type errors, missing types, unsafe casts
    Concurrency: Race conditions, deadlocks, thread safety
    Resource Management: Memory leaks, unclosed resources, excessive allocation

Summary Format

At the PR level, I provide:

## Summary

- **Total Comments:** X
- **Major:** X
- **Minor:** X
- **Nitpick:** X
- **Suggestions:** X

Code Suggestion Format

When providing code fixes:

    // suggested code here

This structure helps prioritize review feedback and track issues systematically.
