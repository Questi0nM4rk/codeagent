---
name: cpp
description: C and C++ development expertise. Activates when working with .c, .cpp, .h, .hpp files or discussing memory management, pointers, CMake, or systems programming.
---

# C/C++ Development Skill

Domain knowledge for C and C++23 systems programming.

## Stack

- **Standard**: C++23, C17
- **Build**: CMake, Make, Ninja
- **Compiler**: GCC, Clang
- **Testing**: GoogleTest, Catch2
- **Analysis**: clang-tidy, cppcheck, valgrind
- **Formatting**: clang-format

## Commands

### Build with CMake

```bash
# Configure
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake -B build -G Ninja

# Build
cmake --build build
cmake --build build --parallel
cmake --build build --target target_name

# Clean
cmake --build build --target clean
rm -rf build

# Install
cmake --install build --prefix /usr/local
```

### Build with Make

```bash
make
make -j$(nproc)
make clean
make install
```

### Testing

```bash
# CTest
ctest --test-dir build
ctest --test-dir build -R test_name
ctest --test-dir build --output-on-failure
ctest --test-dir build -j$(nproc)

# GoogleTest direct
./build/tests/unit_tests
./build/tests/unit_tests --gtest_filter=TestSuite.TestName

# With coverage
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DCODE_COVERAGE=ON
cmake --build build
ctest --test-dir build
gcovr --root . --html coverage.html
```

### Static Analysis

```bash
# clang-tidy
clang-tidy src/*.cpp -- -Iinclude
clang-tidy -p build src/*.cpp

# cppcheck
cppcheck --enable=all --inconclusive src/
cppcheck --enable=all --xml 2>report.xml src/

# clang static analyzer
scan-build cmake --build build
```

### Memory Analysis

```bash
# Valgrind memcheck
valgrind --leak-check=full ./build/program
valgrind --leak-check=full --show-leak-kinds=all ./build/program

# AddressSanitizer (compile with -fsanitize=address)
cmake -B build -DCMAKE_CXX_FLAGS="-fsanitize=address -g"
cmake --build build
./build/program

# ThreadSanitizer
cmake -B build -DCMAKE_CXX_FLAGS="-fsanitize=thread -g"
```

### Formatting

```bash
# Format files
clang-format -i src/*.cpp include/*.h
clang-format -i --style=file src/**/*.cpp

# Check format
clang-format --dry-run --Werror src/*.cpp
```

## Patterns

### RAII and Smart Pointers

```cpp
// Prefer smart pointers over raw pointers
auto ptr = std::make_unique<Resource>();
auto shared = std::make_shared<Resource>();

// RAII for resource management
class FileHandle {
public:
    explicit FileHandle(const std::string& path)
        : handle_(std::fopen(path.c_str(), "r")) {
        if (!handle_) throw std::runtime_error("Failed to open file");
    }

    ~FileHandle() {
        if (handle_) std::fclose(handle_);
    }

    // Delete copy, allow move
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& other) noexcept : handle_(std::exchange(other.handle_, nullptr)) {}

private:
    FILE* handle_;
};
```

### Modern C++ Features

```cpp
// Concepts (C++20)
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
T add(T a, T b) { return a + b; }

// std::expected (C++23)
std::expected<int, std::string> parse(const std::string& s) {
    try {
        return std::stoi(s);
    } catch (...) {
        return std::unexpected("Invalid number");
    }
}

// Ranges
auto result = numbers
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::transform([](int n) { return n * 2; });
```

### Error Handling

```cpp
// Use std::expected or custom Result type
template<typename T, typename E = std::string>
class Result {
public:
    static Result Ok(T value) { return Result(std::move(value)); }
    static Result Err(E error) { return Result(std::unexpected(std::move(error))); }

    bool is_ok() const { return value_.has_value(); }
    const T& value() const { return *value_; }
    const E& error() const { return value_.error(); }

private:
    std::expected<T, E> value_;
};
```

## Testing Patterns

### GoogleTest

```cpp
#include <gtest/gtest.h>

class CalculatorTest : public ::testing::Test {
protected:
    void SetUp() override {
        calc_ = std::make_unique<Calculator>();
    }

    std::unique_ptr<Calculator> calc_;
};

TEST_F(CalculatorTest, AddReturnsSum) {
    EXPECT_EQ(calc_->add(2, 3), 5);
}

TEST_F(CalculatorTest, DivideByZeroThrows) {
    EXPECT_THROW(calc_->divide(1, 0), std::invalid_argument);
}
```

### Catch2

```cpp
#include <catch2/catch_test_macros.hpp>

TEST_CASE("Calculator", "[math]") {
    Calculator calc;

    SECTION("addition") {
        REQUIRE(calc.add(2, 3) == 5);
    }

    SECTION("division by zero") {
        REQUIRE_THROWS_AS(calc.divide(1, 0), std::invalid_argument);
    }
}
```

## Review Tools

```bash
# Static analysis
cppcheck --enable=all --error-exitcode=1 src/
clang-tidy -p build src/*.cpp

# Memory check
valgrind --leak-check=full --error-exitcode=1 ./build/tests

# Format check
clang-format --dry-run --Werror src/*.cpp include/*.h

# Compiler warnings
g++ -Wall -Wextra -Wpedantic -Werror src/*.cpp
```

## File Organization

```
project/
├── CMakeLists.txt
├── include/
│   └── project/
│       ├── public_header.h
│       └── types.h
├── src/
│   ├── CMakeLists.txt
│   ├── main.cpp
│   └── module.cpp
├── tests/
│   ├── CMakeLists.txt
│   └── test_module.cpp
└── cmake/
    └── modules/
```

## Common Conventions

- Use `#pragma once` for include guards
- Prefer `std::string_view` for string parameters
- Use `[[nodiscard]]` for functions with important return values
- Mark single-arg constructors `explicit`
- Prefer `enum class` over plain `enum`
- Use `constexpr` where possible
- Avoid raw `new`/`delete` - use smart pointers
