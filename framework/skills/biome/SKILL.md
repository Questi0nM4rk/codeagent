---
name: biome
description: Biome v2 linter+formatter for TypeScript, JavaScript, JSON, CSS. Activates when working with .ts, .tsx, .js, .jsx, .json, .css files or biome.json config.
---

# Biome Skill

Biome v2.3+ replaces ESLint + Prettier. Single tool for lint + format.

## Config Location

`biome.json` in project root. Owned by **ai-guardrails** - don't edit directly.

Schema: `https://biomejs.dev/schemas/2.3.12/schema.json`

## Key Rules

### No `any` - ever

```typescript
// BAD
const data: any = fetchData();

// GOOD
const data: unknown = fetchData();
if (isUser(data)) { /* narrowed */ }
```

`noExplicitAny: "error"` + `noImplicitAnyLet: "error"`

### No default exports

```typescript
// BAD
export default class UserService {}

// GOOD
export class UserService {}
```

`noDefaultExport: "error"` - Exception: config files (`*.config.ts`, `vite.config.*`, etc.) get an override.

### No `console.log`

`noConsole: "error"` - Use a proper logger.

### No `var`

`noVar: "error"` - Use `const` (preferred) or `let`.

### Named exports with `type` keyword

```typescript
// BAD
import { User } from "./types";
export { User };

// GOOD
import type { User } from "./types";
export type { User };
```

`useImportType: "error"` + `useExportType: "error"`

### Array syntax: generic form

```typescript
// BAD
const items: string[] = [];

// GOOD
const items: Array<string> = [];
```

`useConsistentArrayType: "error"` with `syntax: "generic"`

## Naming Conventions

| Kind | Format | Example |
| ---- | ------ | ------- |
| variable | camelCase, CONSTANT_CASE | `userName`, `MAX_RETRIES` |
| function | camelCase | `getUserById` |
| type/class/interface/enum | PascalCase | `UserService`, `ApiResponse` |
| enumMember | PascalCase, CONSTANT_CASE | `Active`, `PENDING` |
| private class property | camelCase with `_` prefix | `_internalState` |
| file | kebab-case | `user-service.ts` |

## Formatting

- Indent: 2 spaces
- Line width: 100
- Quotes: double (`"`)
- Semicolons: always
- Trailing commas: all
- Arrow parens: always
- Line endings: LF

## Complexity

`noExcessiveCognitiveComplexity: 10` - Same as ruff's mccabe limit.

## Performance Rules

- `noAccumulatingSpread` - Don't spread in loops
- `noBarrelFile` - No `index.ts` re-export barrels
- `noDelete` - Use `Map` instead of `delete obj.key`
- `noReExportAll` - No `export * from`

## Overrides

Config files (`*.config.ts/js/mjs/cjs`, `vite.config.*`, etc.) allow default exports.
Test fixtures (`**/tests/fixtures/**`) skip lint + format entirely.

## Commands

```bash
# Check (lint + format, no write)
biome check .

# Fix everything
biome check --write .

# Format only
biome format --write .

# Lint only
biome lint .
```

## Biome v2 Notes

- Uses `"includes"` (plural) not `"include"` - this is correct for v2
- `"includes"` supports negation with `!` prefix (replaces old `"ignore"`)
- `$schema` should point to v2+ schema URL
- `"assist"` section replaces old `"organizeImports"`
