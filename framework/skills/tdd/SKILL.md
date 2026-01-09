---
name: tdd
description: Test-Driven Development methodology. Activates when implementing features, fixing bugs, or writing any production code. Enforces strict test-first development workflow.
---

# Test-Driven Development Skill

Methodology for writing tests before implementation. Every line of production code must be justified by a failing test.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
No exceptions. No "just this once." No "it's too simple."
```

## Core Principle

> "Never write a line of production code without a failing test."

## The TDD Cycle

```
RED → GREEN → REFACTOR

1. RED: Write a failing test (must fail for right reason)
2. GREEN: Write MINIMAL code to pass (nothing more)
3. REFACTOR: Improve without changing behavior (tests stay green)
```

## When to Use

**Always:**
- Implementing any new feature
- Fixing any bug (test reproduces bug first)
- Adding any new function/method/class
- Modifying existing behavior

**Exceptions (ask human partner):**
- Exploratory prototypes explicitly marked as throwaway
- Learning/experimentation code not intended for production

## Workflow

### 1. RED: Write Failing Test

Requirements:
- Test ONE specific behavior
- Test name describes the requirement
- Test MUST fail initially (if it passes, something is wrong)
- Failure message should be meaningful

```
Arrange → Act → Assert
```

<Good>
```typescript
describe('Calculator', () => {
  it('should add two positive numbers', () => {
    // Arrange
    const calc = new Calculator();

    // Act
    const result = calc.add(2, 3);

    // Assert
    expect(result).toBe(5);
  });
});
```
- Clear test name describes behavior
- Single assertion
- AAA structure
- Tests behavior, not implementation
</Good>

<Bad>
```typescript
it('test calculator', () => {
  const calc = new Calculator();
  expect(calc.add(2, 3)).toBe(5);
  expect(calc.subtract(5, 3)).toBe(2);
  expect(calc.multiply(2, 3)).toBe(6);
  expect(calc.divide(6, 2)).toBe(3);
});
```
- Vague test name
- Multiple unrelated assertions
- Tests multiple behaviors
- If one fails, hard to know which
</Bad>

### 2. GREEN: Make It Pass

Requirements:
- Write MINIMAL code to pass
- Don't optimize
- Don't handle edge cases yet
- "Make it work" not "make it perfect"

<Good>
```typescript
// Test expects add(2, 3) = 5
// Minimal implementation:
add(a: number, b: number): number {
  return a + b;
}
```
Minimal code that passes the test.
</Good>

<Bad>
```typescript
// Test only expects add(2, 3) = 5
// Over-engineered implementation:
add(a: number, b: number): number {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Invalid input');
  }
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    throw new Error('Must be finite');
  }
  const result = a + b;
  if (!Number.isFinite(result)) {
    throw new Error('Overflow');
  }
  return result;
}
```
- Adds untested error handling
- Handles cases no test requires
- "Just in case" code
</Bad>

### 3. REFACTOR: Clean Up

Requirements:
- Tests MUST still pass
- No new functionality
- Improve structure/readability
- Remove duplication

Safe refactorings:
- Rename for clarity
- Extract methods/functions
- Remove duplication
- Simplify conditionals

## Test Types

| Type | What | When | Speed | Mocking |
|------|------|------|-------|---------|
| Unit | Single unit | Business logic, algorithms | ms | External deps |
| Integration | Multiple units | DB, API, services | sec | External services |
| E2E | Full user flow | Critical paths | min | Nothing |

**Pyramid Ratio**: ~70% Unit, ~20% Integration, ~10% E2E

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "It's too simple to test" | Simple code breaks. Test takes 30 seconds to write. |
| "I'll write tests after" | Tests after are biased by implementation. You won't. |
| "I'm just exploring" | Mark it as prototype. If it ships, it needs tests. |
| "Tests slow me down" | Debugging untested code slows you down more. |
| "I know it works" | You know it works NOW. What about after refactoring? |
| "It's just a small change" | Small changes cause big bugs. Test first. |
| "Deadline pressure" | Bugs cost more time than tests save. |

## Red Flags - STOP and Start Over

These indicate you've violated TDD:

- Test passes without writing implementation (test is wrong)
- Wrote implementation before test
- Test requires multiple assertions for different behaviors
- Test verifies implementation details instead of behavior
- Making "just one more change" before running tests
- Tests pass but you're not confident in the code
- Adding "obvious" code without a failing test first

**If you see these, delete the untested code and start with RED.**

## Verification Checklist

Before considering any code complete:

- [ ] Every line of production code was written to make a test pass
- [ ] Each test fails before implementation, passes after
- [ ] Tests are independent (can run in any order)
- [ ] Tests verify behavior, not implementation details
- [ ] No test has multiple unrelated assertions
- [ ] Refactoring didn't change test behavior (only production code)
- [ ] Test names describe the requirement, not the implementation

## When Stuck

| Problem | Solution |
|---------|----------|
| Test won't fail | Test is wrong or feature exists. Check test logic. |
| Can't write minimal code | Test may be too complex. Split into smaller tests. |
| Tests depend on each other | Each test must set up own state. Isolate them. |
| Test is too complex | You're testing too much. One behavior per test. |
| 3 failed attempts | Stop. Document attempts. Ask for help or simplify. |

## Failure Protocol

After 3 failed attempts, STOP and report:

```markdown
## STUCK: Test Won't Pass

### Test
[test code]

### Attempts
1. [what tried] → [error]
2. [what tried] → [error]
3. [what tried] → [error]

### Analysis
[Why I think it's failing]

### Request
Simplify test OR question requirement OR different approach
```

## Related Skills

- `reviewer` - Validates test quality during review
- `systematic-debugging` - When tests reveal bugs to investigate
- `spec-driven` - Specs inform what tests to write
