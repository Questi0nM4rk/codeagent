---
name: dotnet
description: .NET and C# development expertise. Activates when working with .cs, .csproj, .sln files or discussing ASP.NET Core, Entity Framework, or .NET patterns.
---

# .NET Development Skill

Domain knowledge for .NET 8/9/10 and C# 12/13 development.

## The Iron Law

```
NULLABLE REFERENCE TYPES + PRIMARY CONSTRUCTORS + RESULT PATTERN
Enable nullable, use primary constructors for DI, return Result<T> not exceptions.
```

## Core Principle

> "Make invalid states unrepresentable. Let the compiler catch errors, not runtime."

## Stack

| Component   | Technology   |
| ----------- | ------------ |
| Runtime | .NET 8/9/10 |
| Language | C# 12/13 |
| Web | ASP.NET Core, Minimal APIs |
| ORM | Entity Framework Core |
| Testing | xUnit, FluentAssertions |
| DI | Microsoft.Extensions.DependencyInjection |

## Essential Commands

```bash
# Build
dotnet build --warnaserror

# Test with coverage
dotnet test --collect:"XPlat Code Coverage"

# Format
dotnet format --verify-no-changes

# EF Migrations
dotnet ef migrations add MigrationName
dotnet ef database update

# Security check
dotnet list package --vulnerable
```

## Patterns

### Primary Constructor DI (C# 12+)

### Good Example
```csharp
public class UserService(
    IUserRepository repository,
    ILogger<UserService> logger)
{
    public async Task<Result<User>> GetUserAsync(Guid id, CancellationToken ct = default)
    {
        logger.LogInformation("Getting user {UserId}", id);
        var user = await repository.GetByIdAsync(id, ct);
        return user is not null
            ? Result<User>.Success(user)
            : Result<User>.Failure("User not found");
    }
}
```
- Primary constructor for clean DI
- CancellationToken on async methods
- Result pattern for expected failures
- Structured logging with template

### Bad Example
```csharp
public class UserService
{
    private readonly IUserRepository _repository;

    public UserService(IUserRepository repository)
    {
        _repository = repository;
    }

    public async Task<User> GetUserAsync(Guid id)
    {
        var user = await _repository.GetByIdAsync(id);
        if (user == null)
            throw new NotFoundException("User not found");
        return user;
    }
}
```
- Verbose constructor boilerplate
- No CancellationToken
- Exception for expected failure (not found)
- No logging

### Result Pattern

```csharp
public readonly record struct Result<T>
{
    public T? Value { get; }
    public string? Error { get; }
    public bool IsSuccess => Error is null;

    private Result(T? value, string? error) => (Value, Error) = (value, error);

    public static Result<T> Success(T value) => new(value, null);
    public static Result<T> Failure(string error) => new(default, error);
}
```

### Minimal API Endpoints

```csharp
app.MapGet("/users/{id:guid}", async (Guid id, IUserService service, CancellationToken ct) =>
{
    var result = await service.GetUserAsync(id, ct);
    return result.IsSuccess
        ? Results.Ok(result.Value)
        : Results.NotFound(result.Error);
});
```

## Testing

### Good Example
```csharp
public class UserServiceTests
{
    private readonly Mock<IUserRepository> _repositoryMock = new();
    private readonly UserService _sut;

    public UserServiceTests()
    {
        _sut = new UserService(_repositoryMock.Object, NullLogger<UserService>.Instance);
    }

    [Fact]
    public async Task GetUserAsync_WhenExists_ReturnsSuccess()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var user = new User { Id = userId, Email = "test@example.com" };
        _repositoryMock.Setup(r => r.GetByIdAsync(userId, default))
            .ReturnsAsync(user);

        // Act
        var result = await _sut.GetUserAsync(userId);

        // Assert
        result.IsSuccess.Should().BeTrue();
        result.Value!.Email.Should().Be("test@example.com");
    }
}
```
- Clear Arrange/Act/Assert
- FluentAssertions for readability
- Tests behavior, not implementation

## Common Rationalizations

| Excuse   | Reality   |
| -------- | --------- |
| "Nullable is too strict" | It catches bugs at compile time. Enable it. |
| "Exceptions are easier" | Result pattern makes error handling explicit and testable. |
| "Primary constructors are new" | C# 12 is stable. Use modern features. |
| "I don't need CancellationToken" | Every HTTP request can be cancelled. Always pass it. |

## Red Flags - STOP

- `#nullable disable` in new code
- `throw new Exception()` for expected failures
- Missing CancellationToken on async methods
- `await` without ConfigureAwait in libraries
- EF queries without `.AsNoTracking()` for reads
- No structured logging (string interpolation in logs)

## Verification Checklist

- [ ] `<Nullable>enable</Nullable>` in csproj
- [ ] Primary constructors for DI
- [ ] CancellationToken on all async methods
- [ ] Result pattern for expected failures
- [ ] Tests use Arrange/Act/Assert
- [ ] `dotnet build --warnaserror` passes
- [ ] `dotnet list package --vulnerable` clean

## Review Tools

```bash
dotnet format --verify-no-changes          # Format check
dotnet build --warnaserror                  # Warnings as errors
dotnet build /p:EnforceCodeStyleInBuild=true  # Code analysis
dotnet list package --vulnerable            # Security audit
dotnet test --collect:"XPlat Code Coverage" # Coverage
```

## When Stuck

| Problem   | Solution   |
| --------- | ---------- |
| Nullable warnings everywhere | Enable nullable, fix errors file by file |
| EF migrations failing | Check connection string, ensure migrations project set |
| Test dependencies | Use Mock<T> for interfaces, TestContainers for integration |
| DI not resolving | Check service registration, constructor parameters |

## Related Skills

- `tdd` - Test-first development workflow
- `reviewer` - Uses dotnet build/test for validation
- `postgresql` - EF Core with PostgreSQL
