---
name: cpp
description: C and C++ development expertise. Activates when working with .c, .cpp, .h, .hpp files or discussing memory management, pointers, CMake, or systems programming.
---

# C/C++ Development Skill

Domain knowledge for C++23 and C17 systems programming with modern practices.

## The Iron Law

```
NO RAW NEW/DELETE - USE SMART POINTERS AND RAII
Memory is managed by constructors/destructors, not manual allocation.
```

## Core Principle

> "Resource Acquisition Is Initialization. If you type `new`, you're probably wrong."

## Stack

| Component | Technology |
|-----------|------------|
| Standard | C++23, C17 |
| Build | CMake, Ninja |
| Compiler | GCC 13+, Clang 17+ |
| Testing | GoogleTest, Catch2 |
| Analysis | clang-tidy, cppcheck, valgrind |
| Formatting | clang-format |

## Essential Commands

```bash
# Build
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel

# Test
ctest --test-dir build --output-on-failure

# Static analysis
clang-tidy -p build src/*.cpp
cppcheck --enable=all src/

# Memory check
valgrind --leak-check=full ./build/program

# Format
clang-format --dry-run --Werror src/*.cpp
```

## Patterns

### RAII and Smart Pointers

<Good>
```cpp
class Connection {
public:
    explicit Connection(std::string host)
        : socket_(std::make_unique<Socket>(std::move(host))) {
        if (!socket_->connect()) {
            throw std::runtime_error("Connection failed");
        }
    }

    // Destructor automatically closes socket via unique_ptr
    ~Connection() = default;

    // Rule of 5: delete copy, default move
    Connection(const Connection&) = delete;
    Connection& operator=(const Connection&) = delete;
    Connection(Connection&&) noexcept = default;
    Connection& operator=(Connection&&) noexcept = default;

    void send(std::string_view data) {
        socket_->write(data);
    }

private:
    std::unique_ptr<Socket> socket_;
};
```
- unique_ptr manages lifetime
- Explicit constructor prevents implicit conversion
- Rule of 5 properly implemented
- string_view for read-only strings
</Good>

<Bad>
```cpp
class Connection {
public:
    Connection(const char* host) {
        socket_ = new Socket(host);
        socket_->connect();
    }

    ~Connection() {
        delete socket_;
    }

    void send(std::string data) {
        socket_->write(data.c_str());
    }

private:
    Socket* socket_;
};
```
- Raw pointer with manual delete
- Missing copy/move operations (Rule of 5 violation)
- Implicit conversion from const char*
- Unnecessary string copy
</Bad>

### Modern C++ Features (C++20/23)

```cpp
// Concepts (C++20)
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
T add(T a, T b) { return a + b; }

// std::expected (C++23)
std::expected<int, std::string> parse(std::string_view s) {
    try {
        return std::stoi(std::string(s));
    } catch (...) {
        return std::unexpected("Invalid number");
    }
}

// Ranges
auto evens = numbers
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::transform([](int n) { return n * 2; });
```

### Error Handling

<Good>
```cpp
// Use std::expected (C++23) or custom Result
template<typename T, typename E = std::string>
class Result {
public:
    static Result Ok(T value) { return Result{std::move(value)}; }
    static Result Err(E error) { return Result{std::unexpected(std::move(error))}; }

    [[nodiscard]] bool is_ok() const { return value_.has_value(); }
    [[nodiscard]] const T& value() const { return *value_; }
    [[nodiscard]] const E& error() const { return value_.error(); }

private:
    explicit Result(std::expected<T, E> v) : value_(std::move(v)) {}
    std::expected<T, E> value_;
};
```
</Good>

## Testing

<Good>
```cpp
#include <gtest/gtest.h>

class CalculatorTest : public ::testing::Test {
protected:
    void SetUp() override {
        calc_ = std::make_unique<Calculator>();
    }

    std::unique_ptr<Calculator> calc_;
};

TEST_F(CalculatorTest, AddReturnsSumOfTwoNumbers) {
    EXPECT_EQ(calc_->add(2, 3), 5);
}

TEST_F(CalculatorTest, DivideByZeroThrowsInvalidArgument) {
    EXPECT_THROW(calc_->divide(1, 0), std::invalid_argument);
}
```
- Fixture with SetUp for common state
- Descriptive test names
- EXPECT vs ASSERT (continue vs stop)
</Good>

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Raw pointers are faster" | Smart pointers have zero overhead. Use them. |
| "My code doesn't leak" | Valgrind/ASan will prove otherwise. Run them. |
| "C++23 is too new" | GCC 13 and Clang 17 support it. Use it. |
| "RAII is overkill" | Manual resource management is bug-prone. RAII always. |

## Red Flags - STOP

- `new` without corresponding smart pointer
- Raw pointer member without clear ownership semantics
- Missing virtual destructor in base class
- `using namespace std;` in headers
- C-style casts instead of `static_cast`/`dynamic_cast`
- Missing `[[nodiscard]]` on functions returning important values
- Non-explicit single-argument constructors

## Verification Checklist

- [ ] No raw `new`/`delete` (grep for them)
- [ ] All classes follow Rule of 5 (or Rule of 0)
- [ ] `clang-tidy` passes with no warnings
- [ ] `valgrind --leak-check=full` shows no leaks
- [ ] `cppcheck --enable=all` clean
- [ ] Compiled with `-Wall -Wextra -Wpedantic -Werror`
- [ ] Single-arg constructors are `explicit`

## Review Tools

```bash
# Static analysis
cppcheck --enable=all --error-exitcode=1 src/
clang-tidy -p build src/*.cpp

# Memory
valgrind --leak-check=full --error-exitcode=1 ./build/tests
# Or with sanitizers:
cmake -B build -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -g"

# Format
clang-format --dry-run --Werror src/*.cpp include/*.h

# Compile warnings
g++ -Wall -Wextra -Wpedantic -Werror src/*.cpp
```

## When Stuck

| Problem | Solution |
|---------|----------|
| Memory leak | Run valgrind. Use RAII. Check all code paths. |
| Segfault | Run with ASan. Check pointer validity before use. |
| Linker errors | Check include guards. Ensure definitions exist. |
| CMake issues | Clean build dir. Check target_link_libraries. |

## Related Skills

- `tdd` - Test-first development workflow
- `reviewer` - Uses cppcheck/valgrind for validation
- `rust` - Similar systems programming, safer by default
