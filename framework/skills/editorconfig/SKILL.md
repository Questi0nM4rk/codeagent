---
name: editorconfig
description: EditorConfig cross-editor formatting baseline. Activates when discussing indentation, line endings, or editor settings.
---

# EditorConfig Skill

Universal formatting baseline. Every editor respects `.editorconfig`. Config owned by **ai-guardrails**.

## Defaults (all files)

- charset: utf-8
- line endings: LF
- final newline: yes
- trim trailing whitespace: yes
- indent: 4 spaces
- max line: 100

## Language Overrides

| Language | Indent | Max Line |
| -------- | ------ | -------- |
| Python | 4 spaces | 88 |
| C#/.NET | 4 spaces | 120 |
| C/C++ | 4 spaces | 100 |
| Rust | 4 spaces | 100 |
| TypeScript/JavaScript | 2 spaces | 100 |
| JSON/YAML/TOML | 2 spaces | - |
| Lua | 2 spaces | 120 |
| Shell | 2 spaces | 100 |
| Markdown | 2 spaces* | 80 |
| Go | tabs (4) | - |
| Makefile | tabs (4) | - |
| HTML/XML/CSS | 2 spaces | - |

*Markdown: `trim_trailing_whitespace = false` (preserves line breaks).

## C# Naming (via EditorConfig)

- Public members: PascalCase (error)
- Private fields: `_camelCase` with underscore prefix (error)
- System directives sorted first
- Separate import directive groups
