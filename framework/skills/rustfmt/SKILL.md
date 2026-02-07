---
name: rustfmt
description: Rust formatting via rustfmt. Activates when working with .rs files or rustfmt.toml.
---

# Rustfmt Skill

Standard Rust formatter. Config owned by **ai-guardrails**.

## Config Location

`rustfmt.toml` in project root.

## Key Settings

| Setting | Value |
| ------- | ----- |
| edition | 2021 |
| max_width | 100 |
| indent | 4 spaces |
| line endings | Unix (LF) |

## Imports

- `imports_granularity = "Module"` - group by module
- `group_imports = "StdExternalCrate"` - std → external → crate
- Auto-reordered

## Formatting Style

- Brace style: same line with `where` clause
- No single-line functions (`fn_single_line = false`)
- Tall function params (one per line when too wide)
- Wrap + normalize comments at 80 chars
- Format code in doc comments

## Match Arms

- Trailing comma on match arms
- Leading pipes: never
- Match arm blocks allowed

## Commands

```bash
# Format check (CI)
cargo fmt -- --check

# Format (write)
cargo fmt

# Format single file
rustfmt src/main.rs
```

## Nightly Features (commented out)

The config has unstable features ready but commented out:
- `blank_lines_upper_bound` / `lower_bound`
- `hex_literal_case = "Upper"`
- `reorder_impl_items`

Enable with `unstable_features = true` and nightly toolchain.
