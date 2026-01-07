---
name: dotnet
description: .NET and C# development expertise. Activates when working with .cs, .csproj, .sln files or discussing ASP.NET Core, Entity Framework, or .NET patterns.
---

# .NET Development Skill

Domain knowledge for .NET 8/9/10 and C# development.

## Stack

- **Runtime**: .NET 8/9/10
- **Language**: C# 12/13
- **Web**: ASP.NET Core, Minimal APIs
- **ORM**: Entity Framework Core
- **Testing**: xUnit, NUnit, FluentAssertions
- **DI**: Built-in Microsoft.Extensions.DependencyInjection

## Commands

### Development

```bash
# Build
dotnet build
dotnet build --configuration Release
dotnet build --warnaserror

# Run
dotnet run --project src/Api
dotnet watch --project src/Api

# Test
dotnet test
dotnet test --verbosity normal
dotnet test --filter "FullyQualifiedName~ClassName.MethodName"
dotnet test --filter "Category=Unit"
dotnet test --collect:"XPlat Code Coverage"

# Format
dotnet format
dotnet format --verify-no-changes

# Clean
dotnet clean
```

### Database (EF Core)

```bash
# Migrations
dotnet ef migrations add MigrationName
dotnet ef migrations add MigrationName --project src/Infrastructure --startup-project src/Api

# Update database
dotnet ef database update
dotnet ef database update --connection "ConnectionString"

# Generate SQL script
dotnet ef migrations script

# Revert migration
dotnet ef database update PreviousMigration
dotnet ef migrations remove
```

### Packages

```bash
# Add package
dotnet add package PackageName
dotnet add package PackageName --version 1.0.0

# List packages
dotnet list package
dotnet list package --outdated

# Restore
dotnet restore
```

## Patterns

### Primary Constructor DI (C# 12+)

```csharp
public class UserService(
    IUserRepository repository,
    ILogger<UserService> logger)
{
    public async Task<User?> GetUserAsync(Guid id)
    {
        logger.LogInformation("Getting user {UserId}", id);
        return await repository.GetByIdAsync(id);
    }
}
```

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
app.MapGet("/users/{id:guid}", async (Guid id, IUserService service) =>
{
    var result = await service.GetUserAsync(id);
    return result.IsSuccess
        ? Results.Ok(result.Value)
        : Results.NotFound(result.Error);
});
```

### Repository Pattern

```csharp
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    void Update(T entity);
    void Remove(T entity);
}
```

### Entity Configuration (EF Core)

```csharp
public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.HasKey(u => u.Id);
        builder.Property(u => u.Email).HasMaxLength(256).IsRequired();
        builder.HasIndex(u => u.Email).IsUnique();
    }
}
```

## Testing Patterns

### xUnit with FluentAssertions

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
    public async Task GetUserAsync_WhenExists_ReturnsUser()
    {
        // Arrange
        var userId = Guid.NewGuid();
        var user = new User { Id = userId, Email = "test@example.com" };
        _repositoryMock.Setup(r => r.GetByIdAsync(userId, default))
            .ReturnsAsync(user);

        // Act
        var result = await _sut.GetUserAsync(userId);

        // Assert
        result.Should().NotBeNull();
        result!.Email.Should().Be("test@example.com");
    }
}
```

### Integration Tests with TestContainers

```csharp
public class ApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public ApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetUser_ReturnsOk()
    {
        var response = await _client.GetAsync("/users/123");
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }
}
```

## Review Tools

```bash
# Format check
dotnet format --verify-no-changes

# Build warnings as errors
dotnet build --warnaserror

# Security audit
dotnet list package --vulnerable

# Code analysis
dotnet build /p:EnforceCodeStyleInBuild=true
```

## File Organization

```
src/
├── Domain/           # Entities, value objects, domain events
├── Application/      # Use cases, DTOs, interfaces
├── Infrastructure/   # EF Core, external services
└── Api/              # Controllers, endpoints, middleware

tests/
├── Domain.Tests/
├── Application.Tests/
├── Infrastructure.Tests/
└── Api.Tests/
```

## Common Conventions

- Nullable reference types enabled
- File-scoped namespaces
- Primary constructors for DI
- Records for DTOs
- Result pattern over exceptions for expected failures
- CancellationToken on all async methods
