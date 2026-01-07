---
name: rust
description: Rust development expertise. Activates when working with .rs files, Cargo.toml, or discussing ownership, borrowing, lifetimes, or Rust-specific patterns.
---

# Rust Development Skill

Domain knowledge for Rust systems programming.

## Stack

- **Toolchain**: rustup, cargo
- **Edition**: 2021
- **Testing**: Built-in test framework
- **Linting**: clippy
- **Formatting**: rustfmt
- **Docs**: rustdoc

## Commands

### Development

```bash
# Build
cargo build
cargo build --release
cargo build --all-features

# Run
cargo run
cargo run --release
cargo run -- args

# Check (faster than build)
cargo check
cargo check --all-targets

# Test
cargo test
cargo test test_name
cargo test --lib
cargo test --doc
cargo test -- --nocapture
cargo test -- --test-threads=1

# Lint
cargo clippy
cargo clippy -- -D warnings
cargo clippy --all-targets --all-features

# Format
cargo fmt
cargo fmt --check

# Documentation
cargo doc
cargo doc --open
cargo doc --no-deps
```

### Dependency Management

```bash
# Add dependency
cargo add serde
cargo add serde --features derive
cargo add tokio --features full

# Update dependencies
cargo update
cargo update -p package_name

# Check outdated
cargo outdated

# Security audit
cargo audit
cargo deny check
```

### Release

```bash
# Build optimized
cargo build --release

# Strip symbols
cargo build --release && strip target/release/binary

# Cross-compile
cargo build --target x86_64-unknown-linux-musl
```

## Patterns

### Error Handling

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
```

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

    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.timeout = Some(timeout);
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

```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() -> Result<()> {
    let (tx, mut rx) = mpsc::channel(32);

    tokio::spawn(async move {
        tx.send("message").await.unwrap();
    });

    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }

    Ok(())
}
```

### Traits and Generics

```rust
pub trait Repository<T> {
    async fn get(&self, id: &str) -> Result<Option<T>>;
    async fn save(&self, entity: &T) -> Result<()>;
    async fn delete(&self, id: &str) -> Result<()>;
}

impl<T: Serialize + DeserializeOwned> Repository<T> for RedisRepository {
    async fn get(&self, id: &str) -> Result<Option<T>> {
        // implementation
    }
}
```

## Testing Patterns

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_builder_creates_request() {
        let request = RequestBuilder::default()
            .url("https://example.com")
            .build()
            .unwrap();

        assert_eq!(request.url, "https://example.com");
    }

    #[test]
    fn test_builder_fails_without_url() {
        let result = RequestBuilder::default().build();
        assert!(result.is_err());
    }
}
```

### Async Tests

```rust
#[tokio::test]
async fn test_async_operation() {
    let result = fetch_data().await;
    assert!(result.is_ok());
}
```

### Property-Based Testing

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_parse_roundtrip(s in "[a-z]+") {
        let parsed = parse(&s).unwrap();
        let serialized = serialize(&parsed);
        assert_eq!(s, serialized);
    }
}
```

## Review Tools

```bash
# Lint with all warnings
cargo clippy -- -D warnings -W clippy::pedantic

# Format check
cargo fmt --check

# Security audit
cargo audit
cargo deny check advisories

# Unused dependencies
cargo +nightly udeps

# Memory safety (miri)
cargo +nightly miri test
```

## File Organization

```
src/
├── main.rs           # Binary entry point
├── lib.rs            # Library root
├── error.rs          # Error types
├── config.rs         # Configuration
├── domain/           # Domain types
├── repository/       # Data access
└── service/          # Business logic

tests/
├── integration/      # Integration tests
└── common/           # Test utilities
```

## Common Conventions

- Use `Result` and `?` for error handling
- Prefer `&str` over `String` in function parameters
- Use `impl Trait` for return types when possible
- Document public APIs with `///` comments
- Use `#[must_use]` for functions with important return values
- Avoid `unwrap()` in library code
