#!/bin/bash
# ============================================
# CodeAgent Pre-Commit Hook
# Runs before any git commit
# ============================================

set -e

echo "Running pre-commit checks..."

# Detect language and run appropriate checks
run_dotnet_checks() {
  if command -v dotnet &>/dev/null; then
    echo "  .NET: Running tests..."
    dotnet test --no-build --verbosity quiet 2>/dev/null || {
      echo "  .NET tests failed!"
      return 1
    }
    echo "  .NET tests passed"
  fi
}

run_rust_checks() {
  if command -v cargo &>/dev/null && [ -f "Cargo.toml" ]; then
    echo "  Rust: Running tests..."
    cargo test --quiet 2>/dev/null || {
      echo "  Rust tests failed!"
      return 1
    }
    echo "  Rust tests passed"
  fi
}

run_cpp_checks() {
  if [ -d "build" ] && command -v ctest &>/dev/null; then
    echo "  C/C++: Running tests..."
    ctest --test-dir build --output-on-failure --quiet 2>/dev/null || {
      echo "  C/C++ tests failed!"
      return 1
    }
    echo "  C/C++ tests passed"
  fi
}

run_lua_checks() {
  if command -v busted &>/dev/null && { [ -d "spec" ] || [ -f "*.rockspec" ]; }; then
    echo "  Lua: Running tests..."
    busted --quiet 2>/dev/null || {
      echo "  Lua tests failed!"
      return 1
    }
    echo "  Lua tests passed"
  fi
}

# Detect project type and run checks
if ls *.csproj 1>/dev/null 2>&1 || ls *.sln 1>/dev/null 2>&1; then
  run_dotnet_checks
fi

if [ -f "Cargo.toml" ]; then
  run_rust_checks
fi

if [ -f "CMakeLists.txt" ] || [ -f "Makefile" ]; then
  run_cpp_checks
fi

if ls *.rockspec 1>/dev/null 2>&1 || [ -d "spec" ]; then
  run_lua_checks
fi

echo "Pre-commit checks passed"
exit 0
