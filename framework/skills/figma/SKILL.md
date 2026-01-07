---
name: figma
description: Figma design-to-code expertise. Activates when discussing Figma designs, design systems, component extraction, or converting designs to code.
---

# Figma Design-to-Code Skill

Domain knowledge for converting Figma designs to production code.

## MCP Integration

Use the Figma MCP for accessing design data:

```
# Get file data
mcp__figma__get_file: file_key="<figma-file-key>"

# Get specific node
mcp__figma__get_file_nodes: file_key="<key>", ids=["node-id"]

# Get images
mcp__figma__get_images: file_key="<key>", ids=["node-id"], format="svg"

# Get styles
mcp__figma__get_file_styles: file_key="<key>"

# Get components
mcp__figma__get_file_components: file_key="<key>"
```

## Workflow

### 1. Analyze Design Structure

```
1. Get file overview with get_file
2. Identify component hierarchy
3. Extract design tokens (colors, typography, spacing)
4. Identify reusable components vs one-off elements
```

### 2. Extract Design Tokens

From Figma styles, create:

```typescript
// tokens/colors.ts
export const colors = {
  primary: {
    50: '#EEF2FF',
    100: '#E0E7FF',
    500: '#6366F1',
    600: '#4F46E5',
    900: '#312E81',
  },
  neutral: {
    0: '#FFFFFF',
    50: '#F9FAFB',
    100: '#F3F4F6',
    900: '#111827',
  },
};

// tokens/typography.ts
export const typography = {
  fontFamily: {
    sans: ['Inter', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],
    sm: ['0.875rem', { lineHeight: '1.25rem' }],
    base: ['1rem', { lineHeight: '1.5rem' }],
    lg: ['1.125rem', { lineHeight: '1.75rem' }],
    xl: ['1.25rem', { lineHeight: '1.75rem' }],
  },
};

// tokens/spacing.ts
export const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
};
```

### 3. Component Mapping

| Figma Element | React Component |
|---------------|-----------------|
| Frame | `div` or semantic element |
| Auto Layout | Flexbox/Grid container |
| Component | React component |
| Instance | Component with props |
| Text | `p`, `span`, `h1-h6` |
| Rectangle | `div` with styles |
| Image | `img` or `Image` |
| Vector | SVG or icon component |

### 4. Layout Translation

**Auto Layout → Flexbox:**

```tsx
// Figma: Auto Layout, Horizontal, Gap 16, Padding 24
<div className="flex flex-row gap-4 p-6">
  {children}
</div>

// Figma: Auto Layout, Vertical, Space Between
<div className="flex flex-col justify-between">
  {children}
</div>

// Figma: Auto Layout, Fill Container
<div className="flex-1">
  {children}
</div>
```

**Constraints → CSS:**

| Figma Constraint | CSS |
|------------------|-----|
| Left | `left: Xpx` or `ml-X` |
| Right | `right: Xpx` or `mr-X` |
| Left & Right | `left: X; right: Y` or `mx-auto` |
| Center | `margin: 0 auto` or `mx-auto` |
| Scale | `width: X%` |

### 5. Component Structure

```tsx
// Button from Figma component
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  leftIcon,
  rightIcon,
  disabled,
  onClick,
}: ButtonProps) {
  return (
    <button
      className={cn(
        // Base styles
        'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
        // Size variants
        {
          'h-8 px-3 text-sm': size === 'sm',
          'h-10 px-4 text-base': size === 'md',
          'h-12 px-6 text-lg': size === 'lg',
        },
        // Color variants
        {
          'bg-primary-600 text-white hover:bg-primary-700': variant === 'primary',
          'bg-neutral-100 text-neutral-900 hover:bg-neutral-200': variant === 'secondary',
          'bg-transparent text-neutral-600 hover:bg-neutral-100': variant === 'ghost',
        },
        // Disabled
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      disabled={disabled}
      onClick={onClick}
    >
      {leftIcon && <span className="mr-2">{leftIcon}</span>}
      {children}
      {rightIcon && <span className="ml-2">{rightIcon}</span>}
    </button>
  );
}
```

## Patterns

### Responsive Design

```tsx
// Figma breakpoints → Tailwind
// Mobile: 375px
// Tablet: 768px
// Desktop: 1440px

<div className="
  flex flex-col gap-4
  md:flex-row md:gap-6
  lg:gap-8
">
  <div className="w-full md:w-1/2 lg:w-1/3">
    {/* Content */}
  </div>
</div>
```

### Icon Extraction

```tsx
// Export from Figma as SVG, convert to component
export function IconArrowRight({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M5 12H19M19 12L12 5M19 12L12 19"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
```

### Design System Documentation

```tsx
// Storybook stories for each component
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
};
```

## Output Format

When converting a Figma design:

```markdown
## Component: [Name]

### Figma Reference
- File: [file key]
- Node: [node id]
- Link: [Figma URL]

### Design Tokens Used
- Colors: primary-600, neutral-100
- Typography: text-base, font-medium
- Spacing: p-4, gap-2

### Props Identified
| Prop | Type | Default | From Figma |
|------|------|---------|------------|
| variant | enum | primary | Component variants |
| size | enum | md | Size variants |

### Implementation
```tsx
[component code]
```

### Notes
- [Any deviations from design]
- [Accessibility considerations]
```

## Common Conventions

- Extract colors as design tokens, not hardcoded values
- Use CSS variables or Tailwind for theming
- Maintain 1:1 mapping between Figma variants and component props
- Export icons as SVG components
- Document deviations from design
- Ensure accessibility (focus states, ARIA labels)
- Test responsive behavior across breakpoints
