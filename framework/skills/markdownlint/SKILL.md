---
name: markdownlint
description: Markdownlint for markdown files. Activates when writing or editing .md files.
---

# Markdownlint Skill

Lints markdown files via `markdownlint-cli2` pre-commit hook. Config in `.markdownlint.jsonc`.

## Philosophy

Only enforce rules that catch real structural issues. Cosmetic rules that formatters can't autofix are disabled - markdown is primarily AI-consumed.

## Disabled Rules (time-wasters)

| Rule | Why Disabled |
| ---- | ------------ |
| MD009 | Trailing spaces - handled by trailing-whitespace hook |
| MD010 | Hard tabs - handled by editorconfig |
| MD013 | Line length - soft wraps are fine |
| MD014 | Dollar signs in commands - cosmetic |
| MD022 | Blank lines around headings - formatter can't fix |
| MD031 | Blank lines around fenced code blocks - too pedantic |
| MD032 | Blank lines around lists - too pedantic |
| MD033 | Inline HTML - sometimes needed |
| MD036 | Emphasis as heading - false positives |
| MD040 | Language on code blocks - plain text blocks exist |
| MD041 | First line heading - partials/includes don't need it |
| MD047 | Final newline - handled by end-of-file-fixer |
| MD049 | Emphasis style - cosmetic, can't autofix |
| MD050 | Strong style - cosmetic, can't autofix |
| MD060 | Table column spacing - cosmetic, can't autofix |

## Enabled Rules (actually useful)

- **MD001**: Heading levels increment by one (no skipping h2 to h4)
- **MD003**: ATX headings only (`#` style)
- **MD004**: Dashes for unordered lists
- **MD011**: Reversed link syntax detection
- **MD012**: Max 2 consecutive blank lines
- **MD024**: No duplicate sibling headings
- **MD025**: Single H1 per file
- **MD034**: No bare URLs
- **MD042**: No empty links
- **MD046**: Fenced code blocks (not indented)
- **MD051**: Valid link fragments

## Autofix

`markdownlint-cli2 --fix` is run by the `format-and-stage` hook locally. It can fix some issues but not all - that's why cosmetic-only rules are disabled.

## Commands

```bash
# Check
npx markdownlint-cli2 "**/*.md"

# Check specific file
npx markdownlint-cli2 docs/README.md

# Fix what's fixable
npx markdownlint-cli2 --fix "**/*.md"
```
