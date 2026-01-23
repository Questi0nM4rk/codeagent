---
name: rust
description: Rust development expertise. Activates when working with .rs files, Cargo.toml, or discussing ownership, borrowing, lifetimes, or Rust-specific patterns.
---

# Rust Development Skill

Domain knowledge for Rust systems programming with memory safety.

## The Iron Law

```text
NO UNWRAP IN LIBRARY CODE - HANDLE EVERY ERROR WITH ? OR RESULT
Panics are for bugs, not user errors. Use thiserror for library errors.
```

## Core Principle

> "If it compiles, it works. Let the borrow checker catch bugs at compile time."

## Stack

| Component  | Technology          |
| ---------- | ------------------- |
| Toolchain  | rustup, cargo       |
| Edition    | 2021                |
| Testing    | Built-in + proptest |
| Linting    | clippy              |
| Formatting | rustfmt             |
| Async      | tokio               |

## Essential Commands

```bash
# Build
cargo build --release

# Test
cargo test

# Lint (strict)
cargo clippy -- -D warnings -W clippy::pedantic

# Format
cargo fmt --check

# Security
cargo audit
cargo deny check
```

## Patterns

### Error Handling with thiserror

### Good Example

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Not found: {0}")]
    NotFound(String),
    #[error("Invalid input: {0}")]
    InvalidInput(String),
    #[error(transparent)]
    Io(#[from] std::io::Error),
}

pub type Result<T> = std::result::Result<T, AppError>;

pub fn read_config(path: &str) -> Result<Config> {
    let content = std::fs::read_to_string(path)?; // ? propagates io::Error
    parse_config(&content).ok_or_else(|| AppError::InvalidInput("Invalid config".into()))
}
```

- Custom error type with thiserror
- `#[from]` for automatic conversion
- `?` operator for propagation
- No unwrap/expect

### Bad Example

```rust
pub fn read_config(path: &str) -> Config {
    let content = std::fs::read_to_string(path).unwrap();
    parse_config(&content).unwrap()
}
```

- Panics on error
- No error handling
- Caller can't recover

### Builder Pattern

```rust
#[derive(Default)]
pub struct RequestBuilder {
    url: Option<String>,
    timeout: Option<Duration>,
}

impl RequestBuilder {
    pub fn url(mut self, url: impl Into<String>) -> Self {
        self.url = Some(url.into());
        self
    }

    pub fn build(self) -> Result<Request> {
        Ok(Request {
            url: self.url.ok_or(AppError::InvalidInput("url required".into()))?,
            timeout: self.timeout.unwrap_or(Duration::from_secs(30)),
        })
    }
}
```

### Async with Tokio

#### Good Example

```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() -> Result<()> {
    let (tx, mut rx) = mpsc::channel(32);

    tokio::spawn(async move {
        if let Err(e) = tx.send("message").await {
            eprintln!("Send failed: {}", e);
        }
    });

    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }

    Ok(())
}
```

- Proper error handling in spawn
- Channel for communication
- Returns Result

## Testing

### Good Example

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builder_creates_request_with_defaults() {
        let request = RequestBuilder::default()
            .url("https://example.com")
            .build()
            .unwrap(); // OK in tests

        assert_eq!(request.url, "https://example.com");
        assert_eq!(request.timeout, Duration::from_secs(30));
    }

    #[test]
    fn builder_fails_without_url() {
        let result = RequestBuilder::default().build();
        assert!(matches!(result, Err(AppError::InvalidInput(_))));
    }
}
```

- `unwrap()` OK in tests (expected to pass)
- `matches!` for error variants
- Test both success and failure

### Property-Based Testing

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn parse_roundtrip(s in "[a-z]+") {
        let parsed = parse(&s)?;
        let serialized = serialize(&parsed);
        prop_assert_eq!(s, serialized);
    }
}
```

## Common Rationalizations

| Excuse                  | Reality                                                 |
| ----------------------- | ------------------------------------------------------- |
| "unwrap is fine here"   | Use `expect("reason")`. Better: handle error.           |
| "Lifetimes are too hard"| Start owned. Add lifetimes when profiling shows need.   |
| "clippy is too strict"  | Catches real bugs. Allow specific lints with reason.    |
| "Add error handling"    | Later never comes. Use `?` from the start.              |

## Red Flags - STOP

- `unwrap()` or `expect()` in library code
- `panic!()` for recoverable errors
- Ignoring clippy warnings
- `unsafe` without clear justification and comment
- Missing `#[must_use]` on functions with important returns
- Clone everywhere instead of references

## Verification Checklist

- [ ] `cargo clippy -- -D warnings` passes
- [ ] `cargo fmt --check` passes
- [ ] `cargo test` passes
- [ ] `cargo audit` clean
- [ ] No `unwrap()` in library code (grep for it)
- [ ] All public items documented with `///`
- [ ] Error types derive `Error` and `Debug`

## Review Tools

```bash
cargo clippy -- -D warnings -W clippy::pedantic  # Strict lint
cargo fmt --check                                  # Format check
cargo audit                                        # Security vulnerabilities
cargo deny check advisories                        # License + security
cargo +nightly udeps                               # Unused dependencies
cargo +nightly miri test                           # Memory safety (UB detector)
```

## When Stuck

| Problem            | Solution                                             |
| ------------------ | ---------------------------------------------------- |
| Borrow error       | Draw diagram. Consider `Rc`/`Arc` or restructure.    |
| Lifetime error     | Start `'static`. Add lifetimes, loosen later.        |
| Trait bound error  | Check traits. Consider `dyn Trait` or generics.      |
| Async borrow       | Use `Arc` for shared state, channels for comms.      |

## Related Skills

- `tdd` - Test-first development workflow
- `reviewer` - Uses cargo clippy/audit for validation
- `cpp` - Similar systems programming concepts
