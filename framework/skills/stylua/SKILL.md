---
name: stylua
description: Lua formatting via StyLua. Activates when working with .lua files or stylua.toml.
---

# StyLua Skill

Lua formatter. Config owned by **ai-guardrails**.

## Config Location

`stylua.toml` in project root.

## Settings

| Setting | Value |
| ------- | ----- |
| column_width | 120 |
| indent | 2 spaces |
| line endings | Unix (LF) |
| quotes | double (auto-prefer) |
| call_parentheses | always |
| collapse_simple_statement | never |
| sort_requires | enabled |

## Commands

```bash
# Format check (CI)
stylua --check .

# Format (write)
stylua .

# Format single file
stylua src/init.lua
```
