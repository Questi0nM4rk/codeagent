---
name: frontend
description: Frontend development expertise for React, TypeScript, and modern web development. Activates when working with .tsx, .jsx, .ts, .js files or discussing UI components, state management, or web APIs.
---

# Frontend Development Skill

Domain knowledge for modern frontend development with React and TypeScript.

## Stack

- **Framework**: React 18+ with hooks
- **Language**: TypeScript 5+
- **Build**: Vite, Next.js, or similar
- **Styling**: Tailwind CSS, CSS Modules, or styled-components
- **State**: React Query, Zustand, or Redux Toolkit
- **Testing**: Vitest, React Testing Library, Playwright

## Commands

### Development

```bash
# Start dev server
npm run dev
pnpm dev
yarn dev

# Type checking
tsc --noEmit
npx tsc --noEmit

# Linting
npm run lint
npx eslint src/ --ext .ts,.tsx

# Formatting
npx prettier --check "src/**/*.{ts,tsx}"
npx prettier --write "src/**/*.{ts,tsx}"

# Testing
npm test
npx vitest
npx vitest run
npx vitest --coverage

# Single test
npx vitest -t "test name"
npx vitest src/components/Button.test.tsx

# E2E tests
npx playwright test
npx playwright test --ui
```

### Build

```bash
npm run build
npx vite build
npx next build

# Analyze bundle
npx vite-bundle-visualizer
npx @next/bundle-analyzer
```

## Patterns

### Component Structure

```typescript
// Prefer function components with TypeScript
interface ButtonProps {
  variant: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export function Button({ variant, children, onClick, disabled }: ButtonProps) {
  return (
    <button
      className={cn(styles.button, styles[variant])}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
```

### Hooks Pattern

```typescript
// Custom hooks for reusable logic
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

### Data Fetching (React Query)

```typescript
function useUser(id: string) {
  return useQuery({
    queryKey: ['user', id],
    queryFn: () => fetchUser(id),
    staleTime: 5 * 60 * 1000,
  });
}
```

### Error Boundaries

```typescript
<ErrorBoundary fallback={<ErrorFallback />}>
  <Suspense fallback={<Loading />}>
    <Component />
  </Suspense>
</ErrorBoundary>
```

## Testing Patterns

### Component Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### Hook Tests

```typescript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

it('increments counter', () => {
  const { result } = renderHook(() => useCounter());

  act(() => result.current.increment());

  expect(result.current.count).toBe(1);
});
```

## Review Tools

```bash
# Linting
npx eslint src/ --ext .ts,.tsx --format stylish

# Type checking
tsc --noEmit --pretty

# Security
npm audit
npx snyk test

# Bundle analysis
npx vite-bundle-visualizer
```

## Common Issues

### Hydration Mismatch
- Ensure server and client render same content
- Use `useEffect` for client-only code
- Check for `typeof window` guards

### State Updates on Unmounted
- Use cleanup in useEffect
- Cancel async operations
- Use AbortController for fetch

### Performance
- Memoize expensive computations: `useMemo`
- Memoize callbacks: `useCallback`
- Virtualize long lists: `react-virtual`
- Lazy load components: `React.lazy`

## File Organization

```
src/
├── components/     # Reusable UI components
│   └── Button/
│       ├── Button.tsx
│       ├── Button.test.tsx
│       └── Button.module.css
├── hooks/          # Custom hooks
├── pages/          # Route components
├── features/       # Feature modules
├── lib/            # Utilities
├── types/          # TypeScript types
└── styles/         # Global styles
```
