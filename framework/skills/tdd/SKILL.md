---
name: tdd
description: Test-Driven Development methodology. Activates when implementing features, fixing bugs, or discussing testing strategies. Enforces strict test-first development workflow.
---

# Test-Driven Development Skill

Methodology for writing tests before implementation.

## Core Cycle

```
RED → GREEN → REFACTOR

1. RED: Write a failing test
2. GREEN: Write minimal code to pass
3. REFACTOR: Improve without changing behavior
```

## The TDD Mantra

> "Never write a line of production code without a failing test."

## Detailed Workflow

### 1. RED: Write Failing Test

```markdown
### Requirements
- Test ONE specific behavior
- Test name describes the requirement
- Test MUST fail initially
- Failure message should be meaningful

### Test Structure (AAA)
1. **Arrange**: Set up preconditions
2. **Act**: Execute the behavior
3. **Assert**: Verify the outcome

### Example
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

### Run Test
- Verify it FAILS
- If it passes: test is wrong OR feature already exists
- Check failure message makes sense
```

### 2. GREEN: Make It Pass

```markdown
### Requirements
- Write MINIMAL code to pass
- Don't optimize
- Don't handle edge cases yet
- "Make it work" not "make it perfect"

### Process
1. Run test → see it fail
2. Write simplest code that could work
3. Run test → see it pass
4. Resist urge to add more

### Anti-patterns
❌ Writing more than needed
❌ Handling cases not tested
❌ Optimizing prematurely
❌ Adding "just in case" code
```

### 3. REFACTOR: Clean Up

```markdown
### Requirements
- Tests MUST still pass
- No new functionality
- Improve structure/readability
- Remove duplication

### Safe Refactorings
- Rename for clarity
- Extract methods/functions
- Remove duplication
- Simplify conditionals
- Improve naming

### Process
1. Identify code smell
2. Run tests (green)
3. Make small change
4. Run tests (must stay green)
5. Repeat

### Commit After
- Separate commit for refactoring
- `refactor(scope): [description]`
```

## Test Types and When to Use

### Unit Tests
**What**: Test single unit in isolation
**When**: Business logic, pure functions, algorithms
**Speed**: Milliseconds
**Mocking**: External dependencies mocked

```typescript
// Unit test - isolated, fast
it('should calculate discount for premium user', () => {
  const pricing = new PricingService();
  const discount = pricing.calculateDiscount({ tier: 'premium' });
  expect(discount).toBe(0.2);
});
```

### Integration Tests
**What**: Test multiple units together
**When**: Database operations, API endpoints, service interactions
**Speed**: Seconds
**Mocking**: External services, not internal components

```typescript
// Integration test - real database
it('should create user and retrieve by email', async () => {
  const repo = new UserRepository(testDb);
  await repo.create({ email: 'test@example.com' });

  const user = await repo.findByEmail('test@example.com');

  expect(user).toBeDefined();
  expect(user.email).toBe('test@example.com');
});
```

### E2E Tests
**What**: Test full user flows
**When**: Critical paths, authentication, checkout
**Speed**: Minutes
**Mocking**: Nothing (maybe external APIs)

```typescript
// E2E test - browser automation
it('should complete checkout flow', async () => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');
  await page.fill('#email', 'user@example.com');
  await page.click('[data-testid="place-order"]');

  await expect(page.locator('.order-confirmation')).toBeVisible();
});
```

## Test Pyramid

```
        /\
       /  \  E2E (few)
      /----\
     /      \  Integration (some)
    /--------\
   /          \  Unit (many)
  --------------
```

**Ratio**: ~70% Unit, ~20% Integration, ~10% E2E

## TDD Patterns

### Test First for Bug Fixes

```markdown
1. Write test that reproduces the bug
2. Run test → RED (proves bug exists)
3. Fix the bug
4. Run test → GREEN (proves bug fixed)
5. Commit test and fix together
```

### Test First for Features

```markdown
1. Write test for simplest behavior
2. Make it pass
3. Write test for next behavior
4. Make it pass
5. Continue until feature complete
```

### Test First for Refactoring

```markdown
1. Ensure comprehensive tests exist
2. Run tests → GREEN
3. Make small refactoring change
4. Run tests → must stay GREEN
5. Repeat
```

## Failure Handling

### After 3 Failed Attempts

```markdown
## STUCK: Test Won't Pass

### Test
```language
[test code]
```

### Attempts
1. [what tried] → [error]
2. [what tried] → [error]
3. [what tried] → [error]

### Analysis
[Why I think it's failing]

### Options
- [ ] Simplify the test
- [ ] Question the requirement
- [ ] Ask for help
- [ ] Try different approach
```

### When to Question the Test

- Test is too complex
- Can't write minimal code to pass
- Test seems to test implementation details
- Multiple assertions testing different things

## Anti-Patterns

### Test After
❌ Writing implementation first, tests after
- Tests become biased by implementation
- Harder to achieve good coverage
- Tests verify code, not behavior

### Testing Implementation
❌ Testing HOW instead of WHAT
```typescript
// Bad: testing implementation
expect(user.hashedPassword).toMatch(/^\\$2b\\$/);

// Good: testing behavior
expect(await user.verifyPassword('secret')).toBe(true);
```

### Over-Mocking
❌ Mocking everything
- Tests become brittle
- Don't test real behavior
- False confidence

### Test Pollution
❌ Tests depending on each other
- Run in isolation
- Each test sets up own state
- Clean up after

## Commit Strategy

```bash
# Test commit
git commit -m "test(auth): add test for password validation"

# Implementation commit
git commit -m "feat(auth): implement password validation"

# Refactor commit
git commit -m "refactor(auth): extract validation to separate function"
```

## TDD Benefits

1. **Design feedback** - Hard to test = bad design
2. **Documentation** - Tests show how to use code
3. **Confidence** - Refactor without fear
4. **Focus** - One thing at a time
5. **Coverage** - Tests exist by default
