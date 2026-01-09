---
name: frontend
description: Frontend development expertise for React, TypeScript, and modern web development. Activates when working with .tsx, .jsx, .ts, .js files or discussing UI components, state management, or web APIs.
---

# Frontend Development Skill

Domain knowledge for modern frontend development with React and TypeScript.

## The Iron Law

```
TYPESCRIPT STRICT + NO ANY + TEST USER INTERACTIONS
tsc --strict passes. No `any` escapes. Every user interaction is tested.
```

## Core Principle

> "The DOM is a leaky abstraction. TypeScript and tests are your safety net."

## When to Use

**Always:**
- Building React components
- Writing TypeScript for web
- Implementing UI state management
- Creating user interaction handlers

**Exceptions (ask human partner):**
- Legacy JavaScript codebases
- Simple static pages without interactivity

## Stack

| Component | Technology |
|-----------|------------|
| Framework | React 18+ with hooks |
| Language | TypeScript 5+ strict mode |
| Build | Vite, Next.js |
| Styling | Tailwind CSS, CSS Modules |
| State | React Query, Zustand |
| Testing | Vitest, React Testing Library, Playwright |

## Essential Commands

```bash
# Type check (strict!)
tsc --noEmit

# Lint + format
npx eslint src/ --ext .ts,.tsx
npx prettier --check "src/**/*.{ts,tsx}"

# Test
npx vitest
npx vitest --coverage
npx playwright test
```

## Patterns

### Component Structure

<Good>
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export function Button({
  variant,
  children,
  onClick,
  disabled = false
}: ButtonProps) {
  return (
    <button
      type="button"
      className={cn(styles.button, styles[variant])}
      onClick={onClick}
      disabled={disabled}
      aria-disabled={disabled}
    >
      {children}
    </button>
  );
}
```
- Explicit interface for props
- Union types for variants
- Accessibility attributes
- Default values in destructuring
</Good>

<Bad>
```typescript
export function Button(props: any) {
  return (
    <button onClick={props.onClick}>
      {props.children}
    </button>
  );
}
```
- `any` type loses all safety
- No accessibility
- No type documentation
- Missing button type attribute
</Bad>

### Custom Hooks

<Good>
```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// With AbortController for fetch
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch(url, { signal: controller.signal })
      .then(res => res.json())
      .then(setData)
      .catch(err => {
        if (err.name !== 'AbortError') setError(err);
      });

    return () => controller.abort();
  }, [url]);

  return { data, error };
}
```
- Generic types for reusability
- Cleanup in useEffect
- AbortController prevents memory leaks
</Good>

### Data Fetching (React Query)

<Good>
```typescript
interface User {
  id: string;
  email: string;
  name: string;
}

function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: async (): Promise<User> => {
      const res = await fetch(`/api/users/${id}`);
      if (!res.ok) throw new Error('Failed to fetch user');
      return res.json();
    },
    staleTime: 5 * 60 * 1000,
  });
}

// Usage with loading/error states
function UserProfile({ id }: { id: string }) {
  const { data: user, isLoading, error } = useUser(id);

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;

  return <div>{user.name}</div>;
}
```
- Typed query function
- Proper error handling
- Loading states
</Good>

### Error Boundaries

```typescript
<ErrorBoundary
  fallback={<ErrorFallback />}
  onError={(error) => logToService(error)}
>
  <Suspense fallback={<Loading />}>
    <LazyComponent />
  </Suspense>
</ErrorBoundary>
```

### Form Handling

<Good>
```typescript
interface FormData {
  email: string;
  password: string;
}

function LoginForm() {
  const [errors, setErrors] = useState<Partial<FormData>>({});

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);

    const data: FormData = {
      email: formData.get('email') as string,
      password: formData.get('password') as string,
    };

    // Validate
    const newErrors: Partial<FormData> = {};
    if (!data.email) newErrors.email = 'Required';
    if (!data.password) newErrors.password = 'Required';

    if (Object.keys(newErrors).length) {
      setErrors(newErrors);
      return;
    }

    // Submit
    submitForm(data);
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      <input
        name="email"
        type="email"
        aria-invalid={!!errors.email}
        aria-describedby={errors.email ? 'email-error' : undefined}
      />
      {errors.email && <span id="email-error">{errors.email}</span>}
      {/* ... */}
    </form>
  );
}
```
- Type-safe form data
- Accessible error states
- Native FormData API
</Good>

## Testing Patterns

### Component Tests

<Good>
```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Click me</Button>);

    await user.click(screen.getByRole('button', { name: /click me/i }));

    expect(handleClick).toHaveBeenCalledOnce();
  });

  it('does not call onClick when disabled', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick} disabled>Click</Button>);

    await user.click(screen.getByRole('button'));

    expect(handleClick).not.toHaveBeenCalled();
  });
});
```
- userEvent over fireEvent
- Query by role (accessible)
- Test disabled behavior
</Good>

### Hook Tests

```typescript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useCounter } from './useCounter';

it('increments counter', () => {
  const { result } = renderHook(() => useCounter());

  act(() => result.current.increment());

  expect(result.current.count).toBe(1);
});
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "`any` is faster to write" | It disables TypeScript. You'll pay in bugs later. |
| "Testing is slow" | Debugging production is slower. Test interactions. |
| "Strict mode is too strict" | It catches real bugs. Enable it. |
| "I'll add types later" | Later never comes. Type from the start. |

## Red Flags - STOP

- `any` type anywhere (use `unknown` if needed)
- Missing error boundaries
- `useEffect` without cleanup for async operations
- Inline styles for dynamic values (use CSS vars or Tailwind)
- Direct DOM manipulation (`document.getElementById`)
- Missing loading/error states
- Tests that use `fireEvent` instead of `userEvent`
- Missing ARIA attributes on interactive elements

If you see these, stop and fix before continuing.

## Verification Checklist

- [ ] `tsc --noEmit` passes with strict mode
- [ ] `eslint` passes clean
- [ ] No `any` types in code
- [ ] All user interactions have tests
- [ ] Components handle loading/error states
- [ ] Interactive elements have ARIA attributes
- [ ] useEffect cleanups prevent memory leaks
- [ ] Bundle size is acceptable

## Review Tools

```bash
tsc --noEmit --pretty              # Type check
npx eslint src/ --ext .ts,.tsx     # Lint
npx vitest --coverage              # Tests + coverage
npx lighthouse --view              # Performance audit
npm audit                          # Security
```

## When Stuck

| Problem | Solution |
|---------|----------|
| Hydration mismatch | Use `useEffect` for client-only code, check `typeof window` |
| State update on unmounted | Add cleanup, use AbortController |
| Re-renders | Profile with React DevTools, memoize with `useMemo`/`useCallback` |
| Type inference failing | Add explicit type annotations, use `satisfies` operator |

## Related Skills

- `tdd` - Test-first development workflow
- `reviewer` - Uses eslint/tsc for validation
- `typescript` - Advanced type patterns
