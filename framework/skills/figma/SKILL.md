---
name: figma
description: Figma design-to-code expertise. Activates when discussing Figma designs, design systems, component extraction, or converting designs to code.
---

# Figma Design-to-Code Skill

Domain knowledge for converting Figma designs to production-ready code.

## The Iron Law

```
DESIGN TOKENS FIRST + COMPONENT MAPPING + ACCESSIBILITY ALWAYS
Extract tokens before components. Map Figma variants to props. Every interactive element is accessible.
```

## Core Principle

> "The design is the spec. Extract the system, not just the pixels."

## When to Use

**Always:**
- Converting Figma designs to React/Vue/Svelte components
- Building design systems from Figma
- Extracting design tokens (colors, typography, spacing)
- Creating component variants from Figma variants

**Exceptions (ask human partner):**
- Highly animated/interactive designs (may need motion design expertise)
- Complex data visualizations (may need D3/charting library knowledge)

## Workflow

### Step 1: Analyze Design Structure

```
1. Get file overview with get_file
2. Identify component hierarchy
3. Extract design tokens (colors, typography, spacing)
4. Identify reusable components vs one-off elements
```

### Step 2: Extract Design Tokens

From Figma styles, create token files:

```typescript
// tokens/colors.ts
export const colors = {
  primary: {
    50: '#EEF2FF',
    500: '#6366F1',
    600: '#4F46E5',
  },
};

// tokens/typography.ts
export const typography = {
  fontFamily: {
    sans: ['Inter', 'sans-serif'],
  },
  fontSize: {
    base: ['1rem', { lineHeight: '1.5rem' }],
  },
};

// tokens/spacing.ts
export const spacing = {
  4: '1rem',   // 16px
  6: '1.5rem', // 24px
};
```

### Step 3: Map Components

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

### Step 4: Build Components

Create components with variant props matching Figma variants.

### Step 5: Document

Document deviations and accessibility considerations.

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

## Examples

### Design Token Extraction

<Good>
```typescript
// tokens/colors.ts - extracted from Figma styles
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
} as const;

// Usage in component
<button className="bg-primary-600 hover:bg-primary-700">
```
- Tokens extracted from Figma styles
- Semantic naming (primary, neutral)
- Scale follows design system (50-900)
- `as const` for type inference
</Good>

<Bad>
```typescript
// Hardcoded colors everywhere
<button style={{ backgroundColor: '#4F46E5' }}>
<div className="bg-[#6366F1]">
```
- Hardcoded hex values
- No token system
- Impossible to maintain or theme
- Inconsistent with design system
</Bad>

### Component with Variants

<Good>
```tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  leftIcon?: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  leftIcon,
  disabled,
  onClick,
}: ButtonProps) {
  return (
    <button
      className={cn(
        // Base styles
        'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500',
        // Size variants (from Figma)
        {
          'h-8 px-3 text-sm': size === 'sm',
          'h-10 px-4 text-base': size === 'md',
          'h-12 px-6 text-lg': size === 'lg',
        },
        // Color variants (from Figma)
        {
          'bg-primary-600 text-white hover:bg-primary-700': variant === 'primary',
          'bg-neutral-100 text-neutral-900 hover:bg-neutral-200': variant === 'secondary',
          'bg-transparent text-neutral-600 hover:bg-neutral-100': variant === 'ghost',
        },
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      disabled={disabled}
      onClick={onClick}
      aria-disabled={disabled}
    >
      {leftIcon && <span className="mr-2" aria-hidden="true">{leftIcon}</span>}
      {children}
    </button>
  );
}
```
- Props match Figma variants exactly
- Focus states for accessibility
- `aria-disabled` for screen readers
- `aria-hidden` on decorative icons
- Uses design tokens, not hardcoded values
</Good>

<Bad>
```tsx
function Button({ type, onClick, children }) {
  return (
    <div
      onClick={onClick}
      style={{
        padding: '10px 20px',
        background: type === 'blue' ? 'blue' : 'gray'
      }}
    >
      {children}
    </div>
  );
}
```
- `div` instead of `button` (not accessible)
- Hardcoded pixels, not from design system
- Generic color names, not semantic
- No focus state
- No disabled handling
- Not keyboard accessible
</Bad>

### Auto Layout to Flexbox

<Good>
```tsx
// Figma: Auto Layout, Horizontal, Gap 16, Padding 24
<div className="flex flex-row gap-4 p-6">
  {children}
</div>

// Figma: Auto Layout, Vertical, Space Between
<div className="flex flex-col justify-between h-full">
  {children}
</div>

// Figma: Auto Layout, Fill Container
<div className="flex-1 min-w-0">
  {children}
</div>
```
- Direct translation from Figma auto layout
- Uses Tailwind spacing scale
- `min-w-0` prevents flex overflow
</Good>

<Bad>
```tsx
<div style={{ display: 'flex', gap: '16px', padding: '24px' }}>
```
- Inline styles, not reusable
- Hardcoded pixels
- No responsive consideration
</Bad>

### Icon Extraction

<Good>
```tsx
// Exported from Figma as SVG, converted to component
interface IconProps {
  className?: string;
  'aria-label'?: string;
}

export function IconArrowRight({ className, 'aria-label': ariaLabel }: IconProps) {
  return (
    <svg
      className={className}
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden={!ariaLabel}
      aria-label={ariaLabel}
      role={ariaLabel ? 'img' : undefined}
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
- `currentColor` for theming
- `aria-hidden` when decorative
- `aria-label` when meaningful
- Typed props interface
</Good>

<Bad>
```tsx
<img src="/arrow.png" width="24" height="24" />
```
- Raster image, not scalable
- Can't change color
- Extra HTTP request
- No accessibility
</Bad>

### Responsive Design

<Good>
```tsx
// Figma breakpoints → Tailwind
// Mobile: 375px (default)
// Tablet: 768px (md:)
// Desktop: 1440px (lg:)

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
- Mobile-first approach
- Breakpoints match Figma frames
- Progressive enhancement
</Good>

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "I'll extract tokens later" | You'll hardcode everything. Extract first. |
| "It's pixel perfect" | Pixels don't scale. Use design tokens. |
| "Accessibility takes too long" | Lawsuits take longer. Do it now. |
| "The design doesn't have variants" | Create them. Components need states. |
| "I'll just use the Figma export" | Figma exports code, not components. Build properly. |

## Red Flags - STOP and Start Over

These indicate problems with the implementation:

- Hardcoded hex colors instead of tokens
- `div` used for interactive elements (use `button`, `a`)
- Missing focus states on interactive elements
- No `aria-label` on icon-only buttons
- Inline styles instead of design system classes
- Fixed pixel widths that break on mobile
- No variant props for component states
- Images without alt text

If you see these, stop and fix before continuing.

## Verification Checklist

Before considering the task complete:

- [ ] Design tokens extracted (colors, typography, spacing)
- [ ] All Figma variants mapped to component props
- [ ] Interactive elements use semantic HTML (`button`, `a`, etc.)
- [ ] Focus states visible on all interactive elements
- [ ] Icon-only buttons have `aria-label`
- [ ] Images have meaningful `alt` text
- [ ] Responsive behavior matches Figma frames
- [ ] Components documented in Storybook or equivalent
- [ ] Deviations from design documented

## Output Format

When converting a Figma design, document:

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
[component code]

### Accessibility Notes
- [Focus states added]
- [ARIA labels for icons]

### Deviations
- [Any differences from design and why]
```

## When Stuck

| Problem | Solution |
|---------|----------|
| Figma file too complex | Start with one component, extract tokens first |
| No design tokens in Figma | Create tokens from repeated values in designs |
| Variants don't match code needs | Map Figma variants to props, add missing states |
| Responsive behavior unclear | Check all Figma frames (mobile/tablet/desktop) |
| Icons look blurry | Export as SVG, convert to component |
| Colors inconsistent | Extract all colors, create semantic token mapping |

## Related Skills

- `typescript` - For typed component props
- `react` - For component implementation
- `tailwind` - For utility-first styling
- `reviewer` - For accessibility validation
- `tdd` - For component testing with Storybook
