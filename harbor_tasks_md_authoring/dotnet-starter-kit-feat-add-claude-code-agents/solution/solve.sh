#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-starter-kit

# Idempotency guard
if grep -qF "description: Verify changes don't violate architecture rules. Run architecture t" ".claude/agents/architecture-guard.md" && grep -qF "description: Review code changes against FSH patterns and conventions. Use proac" ".claude/agents/code-reviewer.md" && grep -qF "description: Generate complete feature folders with Command, Handler, Validator," ".claude/agents/feature-scaffolder.md" && grep -qF "description: Handle EF Core migrations safely. Create, apply, and manage databas" ".claude/agents/migration-helper.md" && grep -qF "description: Create new modules (bounded contexts) with complete project structu" ".claude/agents/module-creator.md" && grep -qF "endpoints.MapGet(\"/\", async ([AsParameters] GetProductsQuery query, ...) => ...)" ".claude/rules/api-conventions.md" && grep -qF "Changes to BuildingBlocks affect ALL modules across the entire framework. These " ".claude/rules/buildingblocks-protection.md" && grep -qF "Architecture tests in `Architecture.Tests/` are mandatory and enforce:" ".claude/rules/testing-rules.md" && grep -qF "description: Create a domain entity with multi-tenancy, auditing, soft-delete, a" ".claude/skills/add-entity/SKILL.md" && grep -qF "description: Create a new API endpoint with Command, Handler, Validator, and End" ".claude/skills/add-feature/SKILL.md" && grep -qF "description: Create a new module (bounded context) with proper project structure" ".claude/skills/add-module/SKILL.md" && grep -qF "description: Mediator library patterns and interfaces for FSH. This project uses" ".claude/skills/mediator-reference/SKILL.md" && grep -qF "description: Query patterns including pagination, search, filtering, and specifi" ".claude/skills/query-patterns/SKILL.md" && grep -qF "description: Write unit tests, integration tests, and architecture tests for FSH" ".claude/skills/testing-guide/SKILL.md" && grep -qF "e.MapPost(\"/\", async (CreateUserCommand cmd, IMediator m, CancellationToken ct) " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/architecture-guard.md b/.claude/agents/architecture-guard.md
@@ -0,0 +1,123 @@
+---
+name: architecture-guard
+description: Verify changes don't violate architecture rules. Run architecture tests, check module boundaries, verify BuildingBlocks aren't modified. Use before commits or PRs.
+tools: Read, Grep, Glob, Bash
+disallowedTools: Write, Edit
+model: haiku
+permissionMode: plan
+---
+
+You are an architecture guardian for FullStackHero .NET Starter Kit. Your job is to verify architectural integrity.
+
+## Verification Steps
+
+### 1. Check for BuildingBlocks Modifications
+
+```bash
+git diff --name-only | grep -E "^src/BuildingBlocks/"
+```
+
+If any files listed: **STOP** - BuildingBlocks changes require explicit approval.
+
+### 2. Run Architecture Tests
+
+```bash
+dotnet test src/Tests/Architecture.Tests --no-build
+```
+
+All tests must pass.
+
+### 3. Verify Build Has 0 Warnings
+
+```bash
+dotnet build src/FSH.Framework.slnx 2>&1 | grep -E "warning|error"
+```
+
+Must show no warnings or errors.
+
+### 4. Check Module Boundaries
+
+Verify no cross-module internal dependencies:
+
+```bash
+# Check if any module references another module's internal types
+grep -r "using Modules\." src/Modules/ --include="*.cs" | grep -v "\.Contracts"
+```
+
+Should only show references to `.Contracts` namespaces.
+
+### 5. Verify Mediator Usage
+
+```bash
+# Check for MediatR usage (should be empty)
+grep -r "MediatR\|IRequest<\|IRequestHandler<" src/Modules/ --include="*.cs"
+```
+
+Must be empty - all should use Mediator interfaces.
+
+### 6. Check Validator Coverage
+
+For each command, verify a validator exists:
+
+```bash
+# List commands
+find src/Modules -name "*Command.cs" -type f
+
+# List validators
+find src/Modules -name "*Validator.cs" -type f
+```
+
+Every command needs a corresponding validator.
+
+### 7. Check Endpoint Authorization
+
+```bash
+# Find endpoints without authorization
+grep -r "\.Map\(Get\|Post\|Put\|Delete\)" src/Modules/ --include="*.cs" -A 5 | \
+grep -v "RequirePermission\|AllowAnonymous"
+```
+
+Every endpoint must have explicit authorization.
+
+## Output Format
+
+```
+## Architecture Verification Report
+
+### BuildingBlocks
+✅ No modifications | ⚠️ MODIFIED - Requires approval
+
+### Architecture Tests
+✅ All passed | ❌ {count} failed
+
+### Build Warnings
+✅ 0 warnings | ❌ {count} warnings
+
+### Module Boundaries
+✅ Clean | ❌ Cross-module dependencies found
+
+### Mediator Usage
+✅ Correct | ❌ MediatR interfaces detected
+
+### Validators
+✅ All commands have validators | ❌ Missing: {list}
+
+### Authorization
+✅ All endpoints authorized | ❌ Missing: {list}
+
+---
+**Overall:** ✅ PASS | ❌ FAIL - Fix issues before commit
+```
+
+## Quick Commands
+
+```bash
+# Full verification
+dotnet build src/FSH.Framework.slnx && dotnet test src/FSH.Framework.slnx
+
+# Architecture tests only
+dotnet test src/Tests/Architecture.Tests
+
+# Check for common issues
+git diff --name-only | xargs grep -l "IRequest<\|MediatR"
+```
diff --git a/.claude/agents/code-reviewer.md b/.claude/agents/code-reviewer.md
@@ -0,0 +1,84 @@
+---
+name: code-reviewer
+description: Review code changes against FSH patterns and conventions. Use proactively after any code modifications to catch violations before commit.
+tools: Read, Grep, Glob, Bash
+disallowedTools: Write, Edit
+model: sonnet
+---
+
+You are a code reviewer for the FullStackHero .NET Starter Kit. Your job is to review code changes and ensure they follow FSH patterns.
+
+## Review Process
+
+1. Run `git diff` to see recent changes
+2. Identify which files were modified
+3. Check each change against the rules below
+4. Report violations with specific file:line references
+
+## Critical Rules to Check
+
+### Architecture
+- [ ] Features are in `Modules/{Module}/Features/v1/{Name}/` structure
+- [ ] DTOs are in Contracts project, not internal
+- [ ] No cross-module dependencies (modules only use Contracts)
+- [ ] BuildingBlocks not modified without explicit approval
+
+### Mediator (NOT MediatR!)
+- [ ] Commands use `ICommand<T>` not `IRequest<T>`
+- [ ] Queries use `IQuery<T>` not `IRequest<T>`
+- [ ] Handlers use `ICommandHandler<T,R>` or `IQueryHandler<T,R>`
+- [ ] Handler methods return `ValueTask<T>` not `Task<T>`
+- [ ] Using `Mediator` namespace, not `MediatR`
+
+### Validation
+- [ ] Every command has a matching `AbstractValidator<TCommand>`
+- [ ] Validators use FluentValidation rules
+
+### Endpoints
+- [ ] Has `.RequirePermission()` or `.AllowAnonymous()`
+- [ ] Has `.WithName()` matching the command/query name
+- [ ] Has `.WithSummary()` with description
+- [ ] Returns TypedResults, not raw objects
+
+### Entities
+- [ ] Implements required interfaces (IHasTenant, IAuditableEntity, ISoftDeletable)
+- [ ] Has private constructor for EF Core
+- [ ] Uses factory method for creation
+- [ ] Properties have `private set`
+- [ ] Domain events raised for state changes
+
+### Naming
+- [ ] Commands: `{Action}{Entity}Command`
+- [ ] Queries: `Get{Entity}Query` or `Get{Entities}Query`
+- [ ] Handlers: `{CommandOrQuery}Handler`
+- [ ] Validators: `{Command}Validator`
+- [ ] DTOs: `{Entity}Dto`, `{Entity}Response`
+
+## Output Format
+
+```
+## Code Review Summary
+
+### ✅ Passed
+- [List what's correct]
+
+### ❌ Violations Found
+1. **{Rule}** - {file}:{line}
+   - Issue: {description}
+   - Fix: {how to fix}
+
+### ⚠️ Warnings
+- [Optional suggestions]
+
+### Build Verification
+Run: `dotnet build src/FSH.Framework.slnx`
+Expected: 0 warnings
+```
+
+## After Review
+
+Suggest running:
+```bash
+dotnet build src/FSH.Framework.slnx  # Verify 0 warnings
+dotnet test src/FSH.Framework.slnx   # Run tests
+```
diff --git a/.claude/agents/feature-scaffolder.md b/.claude/agents/feature-scaffolder.md
@@ -0,0 +1,110 @@
+---
+name: feature-scaffolder
+description: Generate complete feature folders with Command, Handler, Validator, and Endpoint files. Use when creating new API endpoints or features.
+tools: Read, Write, Glob, Grep, Bash
+model: inherit
+---
+
+You are a feature scaffolder for FullStackHero .NET Starter Kit. Your job is to generate complete vertical slice features.
+
+## Required Information
+
+Before generating, confirm:
+1. **Module name** - Which module? (e.g., Identity, Catalog)
+2. **Feature name** - What action? (e.g., CreateProduct, GetUser)
+3. **Entity name** - What entity? (e.g., Product, User)
+4. **Operation type** - Command (state change) or Query (read)?
+5. **Properties** - What fields does the command/query need?
+
+## Generation Process
+
+### Step 1: Create Feature Folder
+
+```
+src/Modules/{Module}/Features/v1/{FeatureName}/
+```
+
+### Step 2: Generate Files
+
+For **Commands** (POST/PUT/DELETE), create 4 files:
+1. `{Action}{Entity}Command.cs`
+2. `{Action}{Entity}Handler.cs`
+3. `{Action}{Entity}Validator.cs`
+4. `{Action}{Entity}Endpoint.cs`
+
+For **Queries** (GET), create 3 files:
+1. `Get{Entity}Query.cs` or `Get{Entities}Query.cs`
+2. `Get{Entity}Handler.cs`
+3. `Get{Entity}Endpoint.cs`
+
+### Step 3: Add DTOs to Contracts
+
+Create response/DTO types in:
+```
+src/Modules/{Module}/Modules.{Module}.Contracts/
+```
+
+### Step 4: Wire Endpoint
+
+Show where to add endpoint mapping in the module's `MapEndpoints` method.
+
+## Template: Command
+
+```csharp
+// {Action}{Entity}Command.cs
+public sealed record {Action}{Entity}Command(
+    {Properties}) : ICommand<{Action}{Entity}Response>;
+
+// {Action}{Entity}Handler.cs
+public sealed class {Action}{Entity}Handler(
+    IRepository<{Entity}> repository,
+    ICurrentUser currentUser) : ICommandHandler<{Action}{Entity}Command, {Action}{Entity}Response>
+{
+    public async ValueTask<{Action}{Entity}Response> Handle(
+        {Action}{Entity}Command command,
+        CancellationToken ct)
+    {
+        // Implementation
+    }
+}
+
+// {Action}{Entity}Validator.cs
+public sealed class {Action}{Entity}Validator : AbstractValidator<{Action}{Entity}Command>
+{
+    public {Action}{Entity}Validator()
+    {
+        // Validation rules
+    }
+}
+
+// {Action}{Entity}Endpoint.cs
+public static class {Action}{Entity}Endpoint
+{
+    public static RouteHandlerBuilder Map(this IEndpointRouteBuilder endpoints) =>
+        endpoints.Map{HttpMethod}("/", async (
+            {Action}{Entity}Command command,
+            IMediator mediator,
+            CancellationToken ct) => TypedResults.{Result}(await mediator.Send(command, ct)))
+        .WithName(nameof({Action}{Entity}Command))
+        .WithSummary("{Summary}")
+        .RequirePermission({Module}Permissions.{Entities}.{Action});
+}
+```
+
+## Checklist Before Completion
+
+- [ ] All files use `Mediator` interfaces (NOT MediatR)
+- [ ] Handler returns `ValueTask<T>`
+- [ ] Validator exists for commands
+- [ ] Endpoint has `.RequirePermission()` and `.WithName()` and `.WithSummary()`
+- [ ] DTOs in Contracts project
+- [ ] Shown where to wire endpoint in module
+
+## Verification
+
+After generation, run:
+```bash
+dotnet build src/FSH.Framework.slnx
+```
+
+Must show 0 warnings.
diff --git a/.claude/agents/migration-helper.md b/.claude/agents/migration-helper.md
@@ -0,0 +1,129 @@
+---
+name: migration-helper
+description: Handle EF Core migrations safely. Create, apply, and manage database migrations for FSH multi-tenant setup. Use when adding entities or changing database schema.
+tools: Read, Write, Grep, Glob, Bash
+model: inherit
+---
+
+You are a migration helper for FullStackHero .NET Starter Kit. Your job is to safely manage EF Core migrations.
+
+## Project Paths
+
+- **Migrations project:** `src/Playground/Migrations.PostgreSQL`
+- **Startup project:** `src/Playground/Playground.Api`
+- **DbContexts:** Each module has its own DbContext
+
+## Common Operations
+
+### Add Migration
+
+```bash
+dotnet ef migrations add {MigrationName} \
+  --project src/Playground/Migrations.PostgreSQL \
+  --startup-project src/Playground/Playground.Api \
+  --context {DbContextName}
+```
+
+**Context names:**
+- `IdentityDbContext` - Identity module
+- `MultitenancyDbContext` - Multitenancy module
+- `AuditingDbContext` - Auditing module
+- `{Module}DbContext` - Custom modules
+
+### Apply Migrations
+
+```bash
+dotnet ef database update \
+  --project src/Playground/Migrations.PostgreSQL \
+  --startup-project src/Playground/Playground.Api \
+  --context {DbContextName}
+```
+
+### List Migrations
+
+```bash
+dotnet ef migrations list \
+  --project src/Playground/Migrations.PostgreSQL \
+  --startup-project src/Playground/Playground.Api \
+  --context {DbContextName}
+```
+
+### Remove Last Migration
+
+```bash
+dotnet ef migrations remove \
+  --project src/Playground/Migrations.PostgreSQL \
+  --startup-project src/Playground/Playground.Api \
+  --context {DbContextName}
+```
+
+### Generate SQL Script
+
+```bash
+dotnet ef migrations script \
+  --project src/Playground/Migrations.PostgreSQL \
+  --startup-project src/Playground/Playground.Api \
+  --context {DbContextName} \
+  --output migrations.sql
+```
+
+## Multi-Tenant Considerations
+
+FSH uses per-tenant databases. Migrations apply to:
+1. **Host database** - Tenant registry, shared data
+2. **Tenant databases** - Tenant-specific data
+
+The framework handles tenant database migrations automatically on startup via `UseHeroMultiTenantDatabases()`.
+
+## Migration Naming Conventions
+
+Use descriptive names:
+- `Add{Entity}` - Adding new entity
+- `Add{Property}To{Entity}` - Adding column
+- `Remove{Property}From{Entity}` - Removing column
+- `Create{Index}Index` - Adding index
+- `Rename{Old}To{New}` - Renaming
+
+## Pre-Migration Checklist
+
+- [ ] Entity configuration exists (`IEntityTypeConfiguration<T>`)
+- [ ] Entity added to DbContext (`DbSet<T>`)
+- [ ] Build succeeds with 0 warnings
+- [ ] Backup database if production
+
+## Post-Migration Checklist
+
+- [ ] Review generated migration file
+- [ ] Check Up() and Down() methods are correct
+- [ ] Test migration on development database
+- [ ] Verify rollback works (Down method)
+
+## Troubleshooting
+
+### "No DbContext was found"
+Specify context explicitly with `--context {Name}DbContext`
+
+### "Build failed"
+Run `dotnet build src/FSH.Framework.slnx` first
+
+### "Pending migrations"
+Apply pending migrations or remove them if not needed
+
+### "Migration already applied"
+Check `__EFMigrationsHistory` table in database
+
+## Example: Adding a New Entity
+
+1. Create entity in `Domain/` folder
+2. Create configuration (`IEntityTypeConfiguration<T>`)
+3. Add `DbSet<T>` to DbContext
+4. Build: `dotnet build src/FSH.Framework.slnx`
+5. Add migration:
+   ```bash
+   dotnet ef migrations add Add{Entity} \
+     --project src/Playground/Migrations.PostgreSQL \
+     --startup-project src/Playground/Playground.Api \
+     --context {Module}DbContext
+   ```
+6. Review migration file
+7. Apply: `dotnet ef database update ...`
diff --git a/.claude/agents/module-creator.md b/.claude/agents/module-creator.md
@@ -0,0 +1,131 @@
+---
+name: module-creator
+description: Create new modules (bounded contexts) with complete project structure, DbContext, permissions, and registration. Use when adding a new business domain.
+tools: Read, Write, Glob, Grep, Bash
+model: inherit
+---
+
+You are a module creator for FullStackHero .NET Starter Kit. Your job is to scaffold complete new modules.
+
+## When to Create a New Module
+
+Ask these questions:
+- Does it have its own domain entities? → Yes = new module
+- Could it be deployed independently? → Yes = new module
+- Is it just a feature in an existing domain? → No = use existing module
+
+## Required Information
+
+Before generating, confirm:
+1. **Module name** - PascalCase (e.g., Catalog, Inventory, Billing)
+2. **Initial entities** - What domain entities?
+3. **Permissions** - What operations need permissions?
+
+## Generation Process
+
+### Step 1: Create Project Structure
+
+```
+src/Modules/{Name}/
+├── Modules.{Name}/
+│   ├── Modules.{Name}.csproj
+│   ├── {Name}Module.cs
+│   ├── {Name}PermissionConstants.cs
+│   ├── {Name}DbContext.cs
+│   ├── Domain/
+│   └── Features/v1/
+└── Modules.{Name}.Contracts/
+    ├── Modules.{Name}.Contracts.csproj
+    └── DTOs/
+```
+
+### Step 2: Generate Core Files
+
+**Modules.{Name}.csproj:**
+```xml
+<Project Sdk="Microsoft.NET.Sdk">
+  <PropertyGroup>
+    <TargetFramework>net10.0</TargetFramework>
+  </PropertyGroup>
+  <ItemGroup>
+    <ProjectReference Include="..\..\BuildingBlocks\Core\Core.csproj" />
+    <ProjectReference Include="..\..\BuildingBlocks\Persistence\Persistence.csproj" />
+    <ProjectReference Include="..\..\BuildingBlocks\Web\Web.csproj" />
+    <ProjectReference Include="..\Modules.{Name}.Contracts\Modules.{Name}.Contracts.csproj" />
+  </ItemGroup>
+</Project>
+```
+
+**{Name}Module.cs:**
+```csharp
+public sealed class {Name}Module : IModule
+{
+    public void ConfigureServices(IHostApplicationBuilder builder)
+    {
+        // DbContext, repositories, services
+    }
+
+    public void MapEndpoints(IEndpointRouteBuilder endpoints)
+    {
+        var group = endpoints.MapGroup("/api/v1/{name}");
+        // Map feature endpoints
+    }
+}
+```
+
+**{Name}PermissionConstants.cs:**
+```csharp
+public static class {Name}PermissionConstants
+{
+    // Permission groups per entity
+}
+```
+
+**{Name}DbContext.cs:**
+```csharp
+public sealed class {Name}DbContext : DbContext
+{
+    // Entity sets and configuration
+}
+```
+
+### Step 3: Create Contracts Project
+
+**Modules.{Name}.Contracts.csproj:**
+```xml
+<Project Sdk="Microsoft.NET.Sdk">
+  <PropertyGroup>
+    <TargetFramework>net10.0</TargetFramework>
+  </PropertyGroup>
+</Project>
+```
+
+### Step 4: Register Module
+
+Show changes needed in:
+1. `src/Playground/Playground.Api/Program.cs` - Add to moduleAssemblies
+2. `src/Playground/Playground.Api/Playground.Api.csproj` - Add ProjectReference
+3. Solution file - Add both projects
+
+### Step 5: Add to Solution
+
+```bash
+dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}/Modules.{Name}.csproj
+dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}.Contracts/Modules.{Name}.Contracts.csproj
+```
+
+## Checklist
+
+- [ ] Both projects created (main + contracts)
+- [ ] IModule implemented
+- [ ] Permission constants defined
+- [ ] DbContext created with schema
+- [ ] Registered in Program.cs
+- [ ] Added to solution
+- [ ] Referenced from Playground.Api
+
+## Verification
+
+```bash
+dotnet build src/FSH.Framework.slnx  # Must be 0 warnings
+```
diff --git a/.claude/rules/api-conventions.md b/.claude/rules/api-conventions.md
@@ -0,0 +1,65 @@
+---
+paths:
+  - "src/Modules/**/Features/**/*"
+  - "src/Modules/**/*Endpoint*.cs"
+---
+
+# API Conventions
+
+Rules for API endpoints in FSH.
+
+## Endpoint Requirements
+
+Every endpoint MUST have:
+
+```csharp
+endpoints.MapPost("/", handler)
+    .WithName(nameof(CommandOrQuery))      // Required: Unique name
+    .WithSummary("Description")             // Required: OpenAPI description
+    .RequirePermission(Permission)          // Required: Or .AllowAnonymous()
+```
+
+## HTTP Method Mapping
+
+| Operation | Method | Return |
+|-----------|--------|--------|
+| Create | `MapPost` | `TypedResults.Created(...)` |
+| Read single | `MapGet` | `TypedResults.Ok(...)` |
+| Read list | `MapGet` | `TypedResults.Ok(...)` |
+| Update | `MapPut` | `TypedResults.Ok(...)` or `NoContent()` |
+| Delete | `MapDelete` | `TypedResults.NoContent()` |
+
+## Route Patterns
+
+```
+/api/v1/{module}/{entities}           # Collection
+/api/v1/{module}/{entities}/{id}      # Single item
+/api/v1/{module}/{entities}/{id}/sub  # Sub-resource
+```
+
+## Response Types
+
+Always use `TypedResults`:
+- `TypedResults.Ok(data)`
+- `TypedResults.Created($"/path/{id}", data)`
+- `TypedResults.NoContent()`
+- `TypedResults.NotFound()`
+- `TypedResults.BadRequest(errors)`
+
+Never return raw objects or use `Results.Ok()`.
+
+## Permission Format
+
+```csharp
+.RequirePermission({Module}Permissions.{Entity}.{Action})
+```
+
+Actions: `View`, `Create`, `Update`, `Delete`
+
+## Query Parameters
+
+Use `[AsParameters]` for complex queries:
+
+```csharp
+endpoints.MapGet("/", async ([AsParameters] GetProductsQuery query, ...) => ...)
+```
diff --git a/.claude/rules/buildingblocks-protection.md b/.claude/rules/buildingblocks-protection.md
@@ -0,0 +1,36 @@
+---
+paths:
+  - "src/BuildingBlocks/**/*"
+---
+
+# ⚠️ BuildingBlocks Protection
+
+**STOP. You are modifying BuildingBlocks.**
+
+Changes to BuildingBlocks affect ALL modules across the entire framework. These are core abstractions that many projects depend on.
+
+## Before Proceeding
+
+1. **Confirm explicit approval** - Has the user specifically approved this change?
+2. **Consider alternatives** - Can this be done in the module instead?
+3. **Assess impact** - What modules will this affect?
+
+## If Approved
+
+- Make minimal, focused changes
+- Ensure backward compatibility
+- Update all affected modules
+- Run full test suite: `dotnet test src/FSH.Framework.slnx`
+- Document the change
+
+## Alternatives to Consider
+
+| Instead of... | Consider... |
+|---------------|-------------|
+| Modifying Core | Extension method in module |
+| Changing Persistence | Custom repository in module |
+| Updating Web | Module-specific middleware |
+
+## If Not Approved
+
+Do not proceed. Suggest alternatives that don't require BuildingBlocks modifications.
diff --git a/.claude/rules/testing-rules.md b/.claude/rules/testing-rules.md
@@ -0,0 +1,77 @@
+---
+paths:
+  - "src/Tests/**/*"
+---
+
+# Testing Rules
+
+Rules for tests in FSH.
+
+## Test Organization
+
+```
+src/Tests/
+├── Architecture.Tests/    # Layering enforcement (mandatory)
+├── {Module}.Tests/        # Module-specific tests
+└── Generic.Tests/         # Shared utilities
+```
+
+## Naming Conventions
+
+| Type | Pattern |
+|------|---------|
+| Test class | `{ClassUnderTest}Tests` |
+| Test method | `{Method}_{Scenario}_{ExpectedResult}` |
+| Test file | Same as class name |
+
+## Test Structure
+
+Always use Arrange-Act-Assert:
+
+```csharp
+[Fact]
+public async Task Handle_ValidCommand_ReturnsId()
+{
+    // Arrange
+    var command = new CreateProductCommand("Test", 10m);
+    
+    // Act
+    var result = await _handler.Handle(command, CancellationToken.None);
+    
+    // Assert
+    result.Id.Should().NotBeEmpty();
+}
+```
+
+## Required Tests
+
+### For Handlers
+- Happy path with valid input
+- Edge cases (empty, null, boundary values)
+- Repository interactions verified
+
+### For Validators
+- Each validation rule has a test
+- Valid input passes
+- Invalid input fails with correct property
+
+### For Entities
+- Factory method creates valid entity
+- Invalid input throws appropriate exception
+- Domain events raised correctly
+
+## Libraries
+
+- **xUnit** - Test framework
+- **FluentAssertions** - `.Should()` assertions
+- **Moq** - `Mock<T>` for dependencies
+
+## Architecture Tests
+
+Architecture tests in `Architecture.Tests/` are mandatory and enforce:
+- Module boundary isolation
+- No cross-module internal dependencies
+- Handlers/validators are sealed
+- Contracts don't depend on implementations
+
+These run on every build and PR.
diff --git a/.claude/skills/add-entity/SKILL.md b/.claude/skills/add-entity/SKILL.md
@@ -0,0 +1,164 @@
+---
+name: add-entity
+description: Create a domain entity with multi-tenancy, auditing, soft-delete, and domain events. Use when adding new database entities to a module.
+argument-hint: [ModuleName] [EntityName]
+---
+
+# Add Entity
+
+Create a domain entity following FSH patterns with full multi-tenancy support.
+
+## Entity Template
+
+```csharp
+public sealed class {Entity} : AggregateRoot<Guid>, IHasTenant, IAuditableEntity, ISoftDeletable
+{
+    // Domain properties
+    public string Name { get; private set; } = null!;
+    public decimal Price { get; private set; }
+    public string? Description { get; private set; }
+
+    // IHasTenant - automatic tenant isolation
+    public string TenantId { get; private set; } = null!;
+
+    // IAuditableEntity - automatic audit trails
+    public DateTimeOffset CreatedAt { get; set; }
+    public string? CreatedBy { get; set; }
+    public DateTimeOffset? LastModifiedAt { get; set; }
+    public string? LastModifiedBy { get; set; }
+
+    // ISoftDeletable - automatic soft deletes
+    public DateTimeOffset? DeletedAt { get; set; }
+    public string? DeletedBy { get; set; }
+
+    // Private constructor for EF Core
+    private {Entity}() { }
+
+    // Factory method - the only way to create
+    public static {Entity} Create(string name, decimal price, string tenantId)
+    {
+        ArgumentException.ThrowIfNullOrWhiteSpace(name);
+        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(price);
+
+        var entity = new {Entity}
+        {
+            Id = Guid.NewGuid(),
+            Name = name,
+            Price = price,
+            TenantId = tenantId
+        };
+
+        entity.AddDomainEvent(new {Entity}CreatedEvent(entity.Id));
+        return entity;
+    }
+
+    // Domain methods for state changes
+    public void UpdateDetails(string name, decimal price, string? description)
+    {
+        ArgumentException.ThrowIfNullOrWhiteSpace(name);
+        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(price);
+
+        Name = name;
+        Price = price;
+        Description = description;
+
+        AddDomainEvent(new {Entity}UpdatedEvent(Id));
+    }
+}
+```
+
+## Domain Events
+
+```csharp
+public sealed record {Entity}CreatedEvent(Guid {Entity}Id) : IDomainEvent;
+public sealed record {Entity}UpdatedEvent(Guid {Entity}Id) : IDomainEvent;
+public sealed record {Entity}DeletedEvent(Guid {Entity}Id) : IDomainEvent;
+```
+
+## EF Core Configuration
+
+```csharp
+public sealed class {Entity}Configuration : IEntityTypeConfiguration<{Entity}>
+{
+    public void Configure(EntityTypeBuilder<{Entity}> builder)
+    {
+        builder.ToTable("{entities}");
+
+        builder.HasKey(x => x.Id);
+
+        builder.Property(x => x.Name)
+            .IsRequired()
+            .HasMaxLength(200);
+
+        builder.Property(x => x.Price)
+            .HasPrecision(18, 2);
+
+        builder.Property(x => x.TenantId)
+            .IsRequired()
+            .HasMaxLength(64);
+
+        builder.HasIndex(x => x.TenantId);
+
+        // Global query filter for tenant isolation
+        builder.HasQueryFilter(x => x.DeletedAt == null);
+    }
+}
+```
+
+## Register in DbContext
+
+```csharp
+public sealed class {Module}DbContext : DbContext
+{
+    public DbSet<{Entity}> {Entities} => Set<{Entity}>();
+
+    protected override void OnModelCreating(ModelBuilder modelBuilder)
+    {
+        modelBuilder.HasDefaultSchema("{module}");
+        modelBuilder.ApplyConfigurationsFromAssembly(typeof({Module}DbContext).Assembly);
+    }
+}
+```
+
+## Add Migration
+
+```bash
+dotnet ef migrations add Add{Entity} \
+  --project src/Playground/Migrations.PostgreSQL \
+  --startup-project src/Playground/Playground.Api
+
+dotnet ef database update \
+  --project src/Playground/Migrations.PostgreSQL \
+  --startup-project src/Playground/Playground.Api
+```
+
+## Interfaces Reference
+
+| Interface | Purpose | Auto-Handled |
+|-----------|---------|--------------|
+| `IHasTenant` | Tenant isolation | Query filtering |
+| `IAuditableEntity` | Created/Modified tracking | SaveChanges interceptor |
+| `ISoftDeletable` | Soft delete support | Delete interceptor |
+| `AggregateRoot<T>` | Domain events support | Event dispatcher |
+
+## Key Rules
+
+1. **Private constructor** - EF Core needs it, but users use factory methods
+2. **Factory methods** - All creation goes through `Create()` static method
+3. **Domain methods** - State changes through methods, not property setters
+4. **Domain events** - Raise events for significant state changes
+5. **Validation in methods** - Validate in factory/domain methods, not entity
+6. **No public setters** - Properties are `private set`
+
+## Checklist
+
+- [ ] Implements `AggregateRoot<Guid>`
+- [ ] Implements `IHasTenant` for tenant isolation
+- [ ] Implements `IAuditableEntity` for audit trails
+- [ ] Implements `ISoftDeletable` for soft deletes
+- [ ] Has private constructor
+- [ ] Has static factory method
+- [ ] Domain events raised for state changes
+- [ ] EF configuration created
+- [ ] Added to DbContext
+- [ ] Migration created
diff --git a/.claude/skills/add-feature/SKILL.md b/.claude/skills/add-feature/SKILL.md
@@ -0,0 +1,116 @@
+---
+name: add-feature
+description: Create a new API endpoint with Command, Handler, Validator, and Endpoint following FSH vertical slice architecture. Use when adding any new feature, API endpoint, or business operation.
+argument-hint: [ModuleName] [FeatureName]
+---
+
+# Add Feature
+
+Create a complete vertical slice feature with all required files.
+
+## File Structure
+
+```
+src/Modules/{Module}/Features/v1/{FeatureName}/
+├── {Action}{Entity}Command.cs      # or Get{Entity}Query.cs
+├── {Action}{Entity}Handler.cs
+├── {Action}{Entity}Validator.cs    # Commands only
+└── {Action}{Entity}Endpoint.cs
+```
+
+## Step 1: Create Command or Query
+
+**For state changes (POST/PUT/DELETE):**
+```csharp
+public sealed record Create{Entity}Command(
+    string Name,
+    decimal Price) : ICommand<Create{Entity}Response>;
+```
+
+**For reads (GET):**
+```csharp
+public sealed record Get{Entity}Query(Guid Id) : IQuery<{Entity}Dto>;
+```
+
+## Step 2: Create Handler
+
+```csharp
+public sealed class Create{Entity}Handler(
+    IRepository<{Entity}> repository,
+    ICurrentUser currentUser) : ICommandHandler<Create{Entity}Command, Create{Entity}Response>
+{
+    public async ValueTask<Create{Entity}Response> Handle(
+        Create{Entity}Command command,
+        CancellationToken ct)
+    {
+        var entity = {Entity}.Create(command.Name, command.Price, currentUser.TenantId);
+        await repository.AddAsync(entity, ct);
+        return new Create{Entity}Response(entity.Id);
+    }
+}
+```
+
+## Step 3: Create Validator (Commands Only)
+
+```csharp
+public sealed class Create{Entity}Validator : AbstractValidator<Create{Entity}Command>
+{
+    public Create{Entity}Validator()
+    {
+        RuleFor(x => x.Name).NotEmpty().MaximumLength(200);
+        RuleFor(x => x.Price).GreaterThan(0);
+    }
+}
+```
+
+## Step 4: Create Endpoint
+
+```csharp
+public static class Create{Entity}Endpoint
+{
+    public static RouteHandlerBuilder Map(this IEndpointRouteBuilder endpoints) =>
+        endpoints.MapPost("/", async (
+            Create{Entity}Command command,
+            IMediator mediator,
+            CancellationToken ct) => TypedResults.Created(
+                $"/{entities}/{(await mediator.Send(command, ct)).Id}"))
+        .WithName(nameof(Create{Entity}Command))
+        .WithSummary("Create a new {entity}")
+        .RequirePermission({Module}Permissions.{Entities}.Create);
+}
+```
+
+## Step 5: Add DTOs to Contracts
+
+In `src/Modules/{Module}/Modules.{Module}.Contracts/`:
+
+```csharp
+public sealed record Create{Entity}Response(Guid Id);
+public sealed record {Entity}Dto(Guid Id, string Name, decimal Price);
+```
+
+## Step 6: Wire Endpoint in Module
+
+In `{Module}Module.cs` MapEndpoints method:
+
+```csharp
+var entities = endpoints.MapGroup("/{entities}").WithTags("{Entities}");
+entities.Map{Action}{Entity}Endpoint();
+```
+
+## Step 7: Verify
+
+```bash
+dotnet build src/FSH.Framework.slnx  # Must be 0 warnings
+dotnet test src/FSH.Framework.slnx
+```
+
+## Checklist
+
+- [ ] Command/Query uses `ICommand<T>` or `IQuery<T>` (NOT MediatR's IRequest)
+- [ ] Handler uses `ICommandHandler<T,R>` or `IQueryHandler<T,R>`
+- [ ] Validator exists for commands
+- [ ] Endpoint has `.RequirePermission()` or `.AllowAnonymous()`
+- [ ] Endpoint has `.WithName()` and `.WithSummary()`
+- [ ] DTOs in Contracts project, not internal
+- [ ] Build passes with 0 warnings
diff --git a/.claude/skills/add-module/SKILL.md b/.claude/skills/add-module/SKILL.md
@@ -0,0 +1,176 @@
+---
+name: add-module
+description: Create a new module (bounded context) with proper project structure, permissions, DbContext, and registration. Use when adding a new business domain that needs its own entities and endpoints.
+argument-hint: [ModuleName]
+---
+
+# Add Module
+
+Create a new bounded context with full project structure.
+
+## When to Create a New Module
+
+- Has its own domain entities
+- Could be deployed independently
+- Represents a distinct business domain
+
+If it's just a feature in an existing domain, use `add-feature` instead.
+
+## Project Structure
+
+```
+src/Modules/{Name}/
+├── Modules.{Name}/
+│   ├── Modules.{Name}.csproj
+│   ├── {Name}Module.cs
+│   ├── {Name}PermissionConstants.cs
+│   ├── {Name}DbContext.cs
+│   ├── Domain/
+│   │   └── {Entity}.cs
+│   └── Features/v1/
+│       └── {Feature}/
+└── Modules.{Name}.Contracts/
+    ├── Modules.{Name}.Contracts.csproj
+    └── DTOs/
+```
+
+## Step 1: Create Projects
+
+### Main Module Project
+`src/Modules/{Name}/Modules.{Name}/Modules.{Name}.csproj`:
+```xml
+<Project Sdk="Microsoft.NET.Sdk">
+  <PropertyGroup>
+    <TargetFramework>net10.0</TargetFramework>
+  </PropertyGroup>
+  <ItemGroup>
+    <ProjectReference Include="..\..\BuildingBlocks\Core\Core.csproj" />
+    <ProjectReference Include="..\..\BuildingBlocks\Persistence\Persistence.csproj" />
+    <ProjectReference Include="..\..\BuildingBlocks\Web\Web.csproj" />
+    <ProjectReference Include="..\Modules.{Name}.Contracts\Modules.{Name}.Contracts.csproj" />
+  </ItemGroup>
+</Project>
+```
+
+### Contracts Project
+`src/Modules/{Name}/Modules.{Name}.Contracts/Modules.{Name}.Contracts.csproj`:
+```xml
+<Project Sdk="Microsoft.NET.Sdk">
+  <PropertyGroup>
+    <TargetFramework>net10.0</TargetFramework>
+  </PropertyGroup>
+</Project>
+```
+
+## Step 2: Implement IModule
+
+```csharp
+public sealed class {Name}Module : IModule
+{
+    public void ConfigureServices(IHostApplicationBuilder builder)
+    {
+        // Register DbContext
+        builder.Services.AddDbContext<{Name}DbContext>((sp, options) =>
+        {
+            var dbOptions = sp.GetRequiredService<IOptions<DatabaseOptions>>().Value;
+            options.UseNpgsql(dbOptions.ConnectionString);
+        });
+
+        // Register repositories
+        builder.Services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
+        builder.Services.AddScoped(typeof(IReadRepository<>), typeof(Repository<>));
+    }
+
+    public void MapEndpoints(IEndpointRouteBuilder endpoints)
+    {
+        var group = endpoints.MapGroup("/api/v1/{name}");
+        // Map feature endpoints here
+    }
+}
+```
+
+## Step 3: Add Permission Constants
+
+```csharp
+public static class {Name}PermissionConstants
+{
+    public static class {Entities}
+    {
+        public const string View = "{Entities}.View";
+        public const string Create = "{Entities}.Create";
+        public const string Update = "{Entities}.Update";
+        public const string Delete = "{Entities}.Delete";
+    }
+}
+```
+
+## Step 4: Create DbContext
+
+```csharp
+public sealed class {Name}DbContext : DbContext
+{
+    public {Name}DbContext(DbContextOptions<{Name}DbContext> options) : base(options) { }
+
+    public DbSet<{Entity}> {Entities} => Set<{Entity}>();
+
+    protected override void OnModelCreating(ModelBuilder modelBuilder)
+    {
+        modelBuilder.HasDefaultSchema("{name}");
+        modelBuilder.ApplyConfigurationsFromAssembly(typeof({Name}DbContext).Assembly);
+    }
+}
+```
+
+## Step 5: Register in Program.cs
+
+```csharp
+// Add to moduleAssemblies array
+var moduleAssemblies = new Assembly[]
+{
+    typeof(IdentityModule).Assembly,
+    typeof(MultitenancyModule).Assembly,
+    typeof(AuditingModule).Assembly,
+    typeof({Name}Module).Assembly,  // Add here
+};
+
+// Add Mediator assemblies if module has commands/queries
+builder.Services.AddMediator(o =>
+{
+    o.Assemblies = [
+        // ... existing
+        typeof({Name}Module).Assembly,
+    ];
+});
+```
+
+## Step 6: Add to Solution
+
+```bash
+dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}/Modules.{Name}.csproj
+dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}.Contracts/Modules.{Name}.Contracts.csproj
+```
+
+## Step 7: Reference from API
+
+In `src/Playground/Playground.Api/Playground.Api.csproj`:
+```xml
+<ProjectReference Include="..\..\Modules\{Name}\Modules.{Name}\Modules.{Name}.csproj" />
+```
+
+## Step 8: Verify
+
+```bash
+dotnet build src/FSH.Framework.slnx  # Must be 0 warnings
+dotnet test src/FSH.Framework.slnx
+```
+
+## Checklist
+
+- [ ] Both projects created (main + contracts)
+- [ ] IModule implemented with ConfigureServices and MapEndpoints
+- [ ] Permission constants defined
+- [ ] DbContext created with proper schema
+- [ ] Registered in Program.cs moduleAssemblies
+- [ ] Added to solution file
+- [ ] Referenced from Playground.Api
+- [ ] Build passes with 0 warnings
diff --git a/.claude/skills/mediator-reference/SKILL.md b/.claude/skills/mediator-reference/SKILL.md
@@ -0,0 +1,132 @@
+---
+name: mediator-reference
+description: Mediator library patterns and interfaces for FSH. This project uses the Mediator source generator, NOT MediatR. Reference when implementing commands, queries, and handlers.
+user-invocable: false
+---
+
+# Mediator Reference
+
+⚠️ **FSH uses the `Mediator` source generator library, NOT `MediatR`.**
+
+These are different libraries with different interfaces. Using MediatR interfaces will cause build errors.
+
+## Interface Comparison
+
+| Purpose | ✅ Mediator (Use This) | ❌ MediatR (Don't Use) |
+|---------|------------------------|------------------------|
+| Command | `ICommand<TResponse>` | `IRequest<TResponse>` |
+| Query | `IQuery<TResponse>` | `IRequest<TResponse>` |
+| Command Handler | `ICommandHandler<TCommand, TResponse>` | `IRequestHandler<TRequest, TResponse>` |
+| Query Handler | `IQueryHandler<TQuery, TResponse>` | `IRequestHandler<TRequest, TResponse>` |
+| Notification | `INotification` | `INotification` |
+| Notification Handler | `INotificationHandler<T>` | `INotificationHandler<T>` |
+
+## Command Pattern
+
+```csharp
+// ✅ Correct - Mediator
+public sealed record CreateUserCommand(string Email, string Name) : ICommand<Guid>;
+
+public sealed class CreateUserHandler : ICommandHandler<CreateUserCommand, Guid>
+{
+    public async ValueTask<Guid> Handle(CreateUserCommand command, CancellationToken ct)
+    {
+        // Implementation
+    }
+}
+
+// ❌ Wrong - MediatR
+public sealed record CreateUserCommand(string Email, string Name) : IRequest<Guid>;
+
+public sealed class CreateUserHandler : IRequestHandler<CreateUserCommand, Guid>
+{
+    public async Task<Guid> Handle(CreateUserCommand request, CancellationToken ct)
+    {
+        // This won't work!
+    }
+}
+```
+
+## Query Pattern
+
+```csharp
+// ✅ Correct - Mediator
+public sealed record GetUserQuery(Guid Id) : IQuery<UserDto>;
+
+public sealed class GetUserHandler : IQueryHandler<GetUserQuery, UserDto>
+{
+    public async ValueTask<UserDto> Handle(GetUserQuery query, CancellationToken ct)
+    {
+        // Implementation
+    }
+}
+```
+
+## Key Differences
+
+| Aspect | Mediator | MediatR |
+|--------|----------|---------|
+| Return type | `ValueTask<T>` | `Task<T>` |
+| Parameter name | `command` / `query` | `request` |
+| Registration | Source generated | Runtime reflection |
+| Performance | Faster (compile-time) | Slower (runtime) |
+
+## Sending Commands/Queries
+
+```csharp
+// In endpoint or controller
+public class MyEndpoint
+{
+    public static async Task<IResult> Handle(
+        CreateUserCommand command,
+        IMediator mediator,  // Same interface name
+        CancellationToken ct)
+    {
+        var result = await mediator.Send(command, ct);
+        return TypedResults.Created($"/users/{result}");
+    }
+}
+```
+
+## Registration
+
+```csharp
+// In Program.cs
+builder.Services.AddMediator(options =>
+{
+    options.Assemblies =
+    [
+        typeof(IdentityModule).Assembly,
+        typeof(MultitenancyModule).Assembly,
+        // Add your module assemblies here
+    ];
+});
+```
+
+## Common Errors
+
+### Error: `IRequest<T>` not found
+**Cause:** Using MediatR interface
+**Fix:** Change to `ICommand<T>` or `IQuery<T>`
+
+### Error: `IRequestHandler<T,R>` not found
+**Cause:** Using MediatR interface
+**Fix:** Change to `ICommandHandler<T,R>` or `IQueryHandler<T,R>`
+
+### Error: Handler not found at runtime
+**Cause:** Assembly not registered in AddMediator
+**Fix:** Add assembly to `options.Assemblies` array
+
+### Error: `Task<T>` vs `ValueTask<T>`
+**Cause:** Using MediatR return type
+**Fix:** Change handler return type to `ValueTask<T>`
+
+## Namespaces
+
+```csharp
+// ✅ Correct
+using Mediator;
+
+// ❌ Wrong
+using MediatR;
+```
diff --git a/.claude/skills/query-patterns/SKILL.md b/.claude/skills/query-patterns/SKILL.md
@@ -0,0 +1,187 @@
+---
+name: query-patterns
+description: Query patterns including pagination, search, filtering, and specifications for FSH. Use when implementing GET endpoints that return lists or need filtering.
+---
+
+# Query Patterns
+
+Reference for implementing queries with pagination, search, and filtering.
+
+## Basic Paginated Query
+
+```csharp
+// Query
+public sealed record Get{Entities}Query(
+    string? Search,
+    int PageNumber = 1,
+    int PageSize = 10) : IQuery<PagedList<{Entity}Dto>>;
+
+// Handler
+public sealed class Get{Entities}Handler(
+    IReadRepository<{Entity}> repository) : IQueryHandler<Get{Entities}Query, PagedList<{Entity}Dto>>
+{
+    public async ValueTask<PagedList<{Entity}Dto>> Handle(
+        Get{Entities}Query query,
+        CancellationToken ct)
+    {
+        var spec = new {Entity}SearchSpec(query.Search, query.PageNumber, query.PageSize);
+        return await repository.PaginatedListAsync(spec, ct);
+    }
+}
+```
+
+## Specification Pattern
+
+```csharp
+public sealed class {Entity}SearchSpec : EntitiesByPaginationFilterSpec<{Entity}, {Entity}Dto>
+{
+    public {Entity}SearchSpec(string? search, int pageNumber, int pageSize)
+        : base(new PaginationFilter(pageNumber, pageSize))
+    {
+        Query
+            .OrderByDescending(x => x.CreatedAt)
+            .Where(x => string.IsNullOrEmpty(search) ||
+                        x.Name.Contains(search) ||
+                        x.Description!.Contains(search));
+    }
+}
+```
+
+## Get Single Entity
+
+```csharp
+// Query
+public sealed record Get{Entity}Query(Guid Id) : IQuery<{Entity}Dto>;
+
+// Handler
+public sealed class Get{Entity}Handler(
+    IReadRepository<{Entity}> repository) : IQueryHandler<Get{Entity}Query, {Entity}Dto>
+{
+    public async ValueTask<{Entity}Dto> Handle(Get{Entity}Query query, CancellationToken ct)
+    {
+        var spec = new {Entity}ByIdSpec(query.Id);
+        var entity = await repository.FirstOrDefaultAsync(spec, ct);
+
+        return entity ?? throw new NotFoundException($"{Entity} {query.Id} not found");
+    }
+}
+
+// Specification
+public sealed class {Entity}ByIdSpec : Specification<{Entity}, {Entity}Dto>, ISingleResultSpecification<{Entity}>
+{
+    public {Entity}ByIdSpec(Guid id)
+    {
+        Query.Where(x => x.Id == id);
+    }
+}
+```
+
+## Advanced Filtering
+
+```csharp
+public sealed record Get{Entities}Query(
+    string? Search,
+    Guid? CategoryId,
+    decimal? MinPrice,
+    decimal? MaxPrice,
+    DateTimeOffset? CreatedAfter,
+    bool? IsActive,
+    string? SortBy,
+    bool SortDescending = false,
+    int PageNumber = 1,
+    int PageSize = 10) : IQuery<PagedList<{Entity}Dto>>;
+
+public sealed class {Entity}FilterSpec : EntitiesByPaginationFilterSpec<{Entity}, {Entity}Dto>
+{
+    public {Entity}FilterSpec(Get{Entities}Query query)
+        : base(new PaginationFilter(query.PageNumber, query.PageSize))
+    {
+        Query
+            // Search
+            .Where(x => string.IsNullOrEmpty(query.Search) ||
+                        x.Name.Contains(query.Search))
+
+            // Filters
+            .Where(x => !query.CategoryId.HasValue ||
+                        x.CategoryId == query.CategoryId)
+            .Where(x => !query.MinPrice.HasValue ||
+                        x.Price >= query.MinPrice)
+            .Where(x => !query.MaxPrice.HasValue ||
+                        x.Price <= query.MaxPrice)
+            .Where(x => !query.CreatedAfter.HasValue ||
+                        x.CreatedAt >= query.CreatedAfter)
+            .Where(x => !query.IsActive.HasValue ||
+                        x.IsActive == query.IsActive);
+
+        // Dynamic sorting
+        ApplySorting(query.SortBy, query.SortDescending);
+    }
+
+    private void ApplySorting(string? sortBy, bool descending)
+    {
+        switch (sortBy?.ToLowerInvariant())
+        {
+            case "name":
+                if (descending) Query.OrderByDescending(x => x.Name);
+                else Query.OrderBy(x => x.Name);
+                break;
+            case "price":
+                if (descending) Query.OrderByDescending(x => x.Price);
+                else Query.OrderBy(x => x.Price);
+                break;
+            default:
+                Query.OrderByDescending(x => x.CreatedAt);
+                break;
+        }
+    }
+}
+```
+
+## Endpoint Patterns
+
+### List Endpoint
+```csharp
+public static RouteHandlerBuilder MapGet{Entities}Endpoint(this IEndpointRouteBuilder endpoints) =>
+    endpoints.MapGet("/", async (
+        [AsParameters] Get{Entities}Query query,
+        IMediator mediator,
+        CancellationToken ct) => TypedResults.Ok(await mediator.Send(query, ct)))
+    .WithName(nameof(Get{Entities}Query))
+    .WithSummary("Get paginated list of {entities}")
+    .RequirePermission({Module}Permissions.{Entities}.View);
+```
+
+### Single Entity Endpoint
+```csharp
+public static RouteHandlerBuilder MapGet{Entity}Endpoint(this IEndpointRouteBuilder endpoints) =>
+    endpoints.MapGet("/{id:guid}", async (
+        Guid id,
+        IMediator mediator,
+        CancellationToken ct) => TypedResults.Ok(await mediator.Send(new Get{Entity}Query(id), ct)))
+    .WithName(nameof(Get{Entity}Query))
+    .WithSummary("Get {entity} by ID")
+    .RequirePermission({Module}Permissions.{Entities}.View);
+```
+
+## Response Types
+
+```csharp
+// In Contracts project
+public sealed record {Entity}Dto(
+    Guid Id,
+    string Name,
+    decimal Price,
+    string? Description,
+    DateTimeOffset CreatedAt);
+
+// PagedList<T> is from BuildingBlocks
+// Returns: Items, PageNumber, PageSize, TotalCount, TotalPages
+```
+
+## Key Points
+
+1. **Use specifications** - Don't write raw LINQ in handlers
+2. **Tenant filtering is automatic** - Framework handles `IHasTenant`
+3. **Soft delete filtering is automatic** - DeletedAt != null filtered out
+4. **Use `[AsParameters]`** - For query parameters in endpoints
+5. **Project to DTOs** - Never return entities directly
diff --git a/.claude/skills/testing-guide/SKILL.md b/.claude/skills/testing-guide/SKILL.md
@@ -0,0 +1,223 @@
+---
+name: testing-guide
+description: Write unit tests, integration tests, and architecture tests for FSH features. Use when adding tests or understanding the testing strategy.
+---
+
+# Testing Guide
+
+FSH uses a layered testing strategy with architecture tests as guardrails.
+
+## Test Project Structure
+
+```
+src/Tests/
+├── Architecture.Tests/    # Enforces layering rules
+├── Generic.Tests/         # Shared test utilities
+├── Identity.Tests/        # Identity module tests
+├── Multitenancy.Tests/    # Multitenancy module tests
+└── Auditing.Tests/        # Auditing module tests
+```
+
+## Architecture Tests
+
+Architecture tests enforce module boundaries and layering. They run on every build.
+
+```csharp
+public class ArchitectureTests
+{
+    [Fact]
+    public void Modules_ShouldNot_DependOnOtherModules()
+    {
+        var result = Types.InAssembly(typeof(IdentityModule).Assembly)
+            .ShouldNot()
+            .HaveDependencyOn("Modules.Multitenancy")
+            .GetResult();
+
+        result.IsSuccessful.Should().BeTrue();
+    }
+
+    [Fact]
+    public void Contracts_ShouldNot_DependOnImplementation()
+    {
+        var result = Types.InAssembly(typeof(UserDto).Assembly)
+            .ShouldNot()
+            .HaveDependencyOn("Modules.Identity")
+            .GetResult();
+
+        result.IsSuccessful.Should().BeTrue();
+    }
+
+    [Fact]
+    public void Handlers_ShouldBe_Sealed()
+    {
+        var result = Types.InAssembly(typeof(IdentityModule).Assembly)
+            .That()
+            .ImplementInterface(typeof(ICommandHandler<,>))
+            .Or()
+            .ImplementInterface(typeof(IQueryHandler<,>))
+            .Should()
+            .BeSealed()
+            .GetResult();
+
+        result.IsSuccessful.Should().BeTrue();
+    }
+}
+```
+
+## Unit Test Patterns
+
+### Handler Tests
+
+```csharp
+public class Create{Entity}HandlerTests
+{
+    private readonly Mock<IRepository<{Entity}>> _repositoryMock;
+    private readonly Mock<ICurrentUser> _currentUserMock;
+    private readonly Create{Entity}Handler _handler;
+
+    public Create{Entity}HandlerTests()
+    {
+        _repositoryMock = new Mock<IRepository<{Entity}>>();
+        _currentUserMock = new Mock<ICurrentUser>();
+        _currentUserMock.Setup(x => x.TenantId).Returns("test-tenant");
+
+        _handler = new Create{Entity}Handler(
+            _repositoryMock.Object,
+            _currentUserMock.Object);
+    }
+
+    [Fact]
+    public async Task Handle_ValidCommand_Returns{Entity}Id()
+    {
+        // Arrange
+        var command = new Create{Entity}Command("Test", 99.99m);
+        _repositoryMock
+            .Setup(x => x.AddAsync(It.IsAny<{Entity}>(), It.IsAny<CancellationToken>()))
+            .Returns(Task.CompletedTask);
+
+        // Act
+        var result = await _handler.Handle(command, CancellationToken.None);
+
+        // Assert
+        result.Id.Should().NotBeEmpty();
+        _repositoryMock.Verify(x => x.AddAsync(
+            It.Is<{Entity}>(e => e.Name == "Test" && e.Price == 99.99m),
+            It.IsAny<CancellationToken>()), Times.Once);
+    }
+}
+```
+
+### Validator Tests
+
+```csharp
+public class Create{Entity}ValidatorTests
+{
+    private readonly Create{Entity}Validator _validator = new();
+
+    [Fact]
+    public void Validate_EmptyName_Fails()
+    {
+        var command = new Create{Entity}Command("", 99.99m);
+        var result = _validator.Validate(command);
+
+        result.IsValid.Should().BeFalse();
+        result.Errors.Should().Contain(e => e.PropertyName == "Name");
+    }
+
+    [Fact]
+    public void Validate_NegativePrice_Fails()
+    {
+        var command = new Create{Entity}Command("Test", -1m);
+        var result = _validator.Validate(command);
+
+        result.IsValid.Should().BeFalse();
+        result.Errors.Should().Contain(e => e.PropertyName == "Price");
+    }
+
+    [Theory]
+    [InlineData("Valid Name", 10)]
+    [InlineData("Another", 0.01)]
+    public void Validate_ValidCommand_Passes(string name, decimal price)
+    {
+        var command = new Create{Entity}Command(name, price);
+        var result = _validator.Validate(command);
+
+        result.IsValid.Should().BeTrue();
+    }
+}
+```
+
+### Entity Tests
+
+```csharp
+public class {Entity}Tests
+{
+    [Fact]
+    public void Create_ValidInput_Creates{Entity}WithEvent()
+    {
+        var entity = {Entity}.Create("Test", 99.99m, "tenant-1");
+
+        entity.Id.Should().NotBeEmpty();
+        entity.Name.Should().Be("Test");
+        entity.Price.Should().Be(99.99m);
+        entity.TenantId.Should().Be("tenant-1");
+        entity.DomainEvents.Should().ContainSingle(e => e is {Entity}CreatedEvent);
+    }
+
+    [Fact]
+    public void Create_EmptyName_ThrowsArgumentException()
+    {
+        var act = () => {Entity}.Create("", 99.99m, "tenant-1");
+
+        act.Should().Throw<ArgumentException>();
+    }
+
+    [Fact]
+    public void UpdateDetails_ValidInput_UpdatesAndRaisesEvent()
+    {
+        var entity = {Entity}.Create("Original", 50m, "tenant-1");
+        entity.ClearDomainEvents();
+
+        entity.UpdateDetails("Updated", 75m, "New description");
+
+        entity.Name.Should().Be("Updated");
+        entity.Price.Should().Be(75m);
+        entity.Description.Should().Be("New description");
+        entity.DomainEvents.Should().ContainSingle(e => e is {Entity}UpdatedEvent);
+    }
+}
+```
+
+## Running Tests
+
+```bash
+# Run all tests
+dotnet test src/FSH.Framework.slnx
+
+# Run specific test project
+dotnet test src/Tests/Architecture.Tests
+
+# Run with coverage
+dotnet test src/FSH.Framework.slnx --collect:"XPlat Code Coverage"
+
+# Run specific test
+dotnet test --filter "FullyQualifiedName~Create{Entity}HandlerTests"
+```
+
+## Test Conventions
+
+| Convention | Example |
+|------------|---------|
+| Test class name | `{ClassUnderTest}Tests` |
+| Test method name | `{Method}_{Scenario}_{ExpectedResult}` |
+| Arrange-Act-Assert | Always use this structure |
+| One assertion concept | Multiple asserts OK if same concept |
+
+## Key Rules
+
+1. **Architecture tests are mandatory** - They enforce module boundaries
+2. **Validators need tests** - Cover edge cases
+3. **Handlers need tests** - Mock dependencies
+4. **Entities need tests** - Test factory methods and domain logic
+5. **Use FluentAssertions** - `.Should()` syntax
+6. **Use Moq for mocking** - `Mock<T>` pattern
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,239 +1,114 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+> FullStackHero .NET Starter Kit — AI Assistant Guidelines
 
-## Build & Run Commands
+## Quick Reference
 
 ```bash
-# Restore and build
-dotnet restore src/FSH.Framework.slnx
-dotnet build src/FSH.Framework.slnx
-
-# Run with Aspire (spins up Postgres + Redis via Docker)
-dotnet run --project src/Playground/FSH.Playground.AppHost
-
-# Run API standalone (requires DB/Redis/JWT config in appsettings)
-dotnet run --project src/Playground/Playground.Api
-
-# Run all tests
-dotnet test src/FSH.Framework.slnx
-
-# Run single test project
-dotnet test src/Tests/Architecture.Tests
-
-# Run specific test
-dotnet test src/Tests/Architecture.Tests --filter "FullyQualifiedName~TestMethodName"
-
-# Generate C# API client from OpenAPI spec (requires API running)
-./scripts/openapi/generate-api-clients.ps1 -SpecUrl "https://localhost:7030/openapi/v1.json"
-
-# Check for OpenAPI drift (CI validation)
-./scripts/openapi/check-openapi-drift.ps1 -SpecUrl "<spec-url>"
+dotnet build src/FSH.Framework.slnx     # Build (0 warnings required)
+dotnet test src/FSH.Framework.slnx      # Test
+dotnet run --project src/Playground/FSH.Playground.AppHost  # Run with Aspire
 ```
 
-## Architecture
-
-FullStackHero .NET 10 Starter Kit - multi-tenant SaaS framework using vertical slice architecture.
-
-### Repository Structure
+## Project Structure
 
-- **src/BuildingBlocks/** - Reusable framework components (packaged as NuGets): Core (DDD primitives), Persistence (EF Core + specifications), Caching (Redis), Mailing, Jobs (Hangfire), Storage, Web (host wiring), Eventing
-- **src/Modules/** - Feature modules (packaged as NuGets): Identity (JWT auth, users, roles), Multitenancy (Finbuckle), Auditing
-- **src/Playground/** - Reference implementation using direct project references for development; includes Aspire AppHost, API, Blazor UI, PostgreSQL migrations
-- **src/Tests/** - Architecture tests using NetArchTest.Rules, xUnit, Shouldly
-- **scripts/openapi/** - NSwag-based C# client generation from OpenAPI spec; outputs to `Playground.Blazor/ApiClient/Generated.cs`
-- **terraform/** - AWS infrastructure as code (modular)
-  - `modules/` - Reusable: network, ecs_cluster, ecs_service, rds_postgres, elasticache_redis, alb, s3_bucket
-  - `apps/playground/` - Playground deployment stack with `envs/{dev,staging,prod}/{region}/`
-  - `bootstrap/` - Initial AWS setup (S3 backend, etc.)
+```
+src/
+├── BuildingBlocks/     # Framework core (⚠️ don't modify without approval)
+├── Modules/            # Business modules — add features here
+│   ├── Identity/       # Auth, users, roles, permissions
+│   ├── Multitenancy/   # Tenant management
+│   └── Auditing/       # Audit logging
+├── Playground/         # Reference application
+└── Tests/              # Architecture + unit tests
+```
 
-### Module Pattern
+## The Pattern
 
-Each module implements `IModule` with:
-- `ConfigureServices(IHostApplicationBuilder)` - DI registration
-- `MapEndpoints(IEndpointRouteBuilder)` - Minimal API endpoint mapping
+Every feature = vertical slice in one folder:
 
-Feature structure within modules:
 ```
-Features/v1/{Feature}/
-├── {Feature}Command.cs (or Query)
-├── {Feature}Handler.cs
-├── {Feature}Validator.cs (FluentValidation)
-└── {Feature}Endpoint.cs (static extension method on IEndpointRouteBuilder)
+Modules/{Module}/Features/v1/{Feature}/
+├── {Action}{Entity}Command.cs      # ICommand<T> (NOT IRequest!)
+├── {Action}{Entity}Handler.cs      # ICommandHandler<T,R> returns ValueTask
+├── {Action}{Entity}Validator.cs    # AbstractValidator<T>
+└── {Action}{Entity}Endpoint.cs     # MapPost/Get/Put/Delete
 ```
 
-Contracts projects (`Modules.{Name}.Contracts/`) contain public DTOs shareable with clients.
-
-### Endpoint Pattern
-
-Endpoints are static extension methods returning `RouteHandlerBuilder`:
+## Critical Rules
+
+| Rule | Why |
+|------|-----|
+| Use `Mediator` not `MediatR` | Different library, different interfaces |
+| `ICommand<T>` / `IQuery<T>` | NOT `IRequest<T>` |
+| `ValueTask<T>` return type | NOT `Task<T>` |
+| DTOs in Contracts project | Keep internals internal |
+| Every command needs validator | No unvalidated input |
+| `.RequirePermission()` on endpoints | Explicit authorization |
+| Zero build warnings | CI enforces this |
+
+## Available Skills
+
+| Skill | When to Use |
+|-------|-------------|
+| `/add-feature` | Creating new API endpoints |
+| `/add-module` | Creating new bounded contexts |
+| `/add-entity` | Adding domain entities |
+| `/query-patterns` | Implementing GET with pagination/filtering |
+| `/testing-guide` | Writing tests |
+
+## Available Agents
+
+| Agent | Purpose |
+|-------|---------|
+| `code-reviewer` | Review changes against FSH patterns |
+| `feature-scaffolder` | Generate complete feature files |
+| `module-creator` | Scaffold new modules |
+| `architecture-guard` | Verify architectural integrity |
+| `migration-helper` | Handle EF Core migrations |
+
+## Quick Patterns
+
+### Command + Handler
 ```csharp
-public static RouteHandlerBuilder MapXxxEndpoint(this IEndpointRouteBuilder endpoint)
+public sealed record CreateUserCommand(string Email) : ICommand<Guid>;
+
+public sealed class CreateUserHandler(IRepository<User> repo) 
+    : ICommandHandler<CreateUserCommand, Guid>
 {
-    return endpoint.MapPost("/path", async (..., IMediator mediator, CancellationToken ct) =>
+    public async ValueTask<Guid> Handle(CreateUserCommand cmd, CancellationToken ct)
     {
-        var result = await mediator.Send(command, ct);
-        return TypedResults.Ok(result);
-    });
+        var user = User.Create(cmd.Email);
+        await repo.AddAsync(user, ct);
+        return user.Id;
+    }
 }
 ```
 
-### Platform Wiring
-
-In `Program.cs`:
-1. Register Mediator with command/query assemblies
-2. Call `builder.AddHeroPlatform(...)` - enables auth, OpenAPI, caching, mailing, jobs, health, OTel
-3. Call `builder.AddModules(moduleAssemblies)` to load modules
-4. Call `app.UseHeroMultiTenantDatabases()` for tenant DB migrations
-5. Call `app.UseHeroPlatform(p => p.MapModules = true)` to wire endpoints
-
-## Configuration
-
-Key settings (appsettings or env vars):
-- `DatabaseOptions:Provider` - postgres or mssql
-- `DatabaseOptions:ConnectionString` - Primary database
-- `CachingOptions:Redis` - Redis connection
-- `JwtOptions:SigningKey` - Required in production
-
-## Code Standards
-
-- .NET 10, C# latest, nullable enabled
-- SonarAnalyzer.CSharp with code style enforced in build
-- API versioning in URL path (`/api/v1/...`)
-- Mediator library (not MediatR) for commands/queries
-- FluentValidation for request validation
-- **Zero warnings policy**: After making any code changes, always verify the build produces no warnings. Run `dotnet build src/FSH.Framework.slnx` and ensure "0 Warning(s)" in output. Fix any warnings before considering work complete.
-
-## Blazor UI Components
-
-The framework provides reusable Blazor components in `BuildingBlocks/Blazor.UI/Components/` with consistent styling.
-
-### FshPageHeader Component
-
-Use `FshPageHeader` for consistent page headers across Playground.Blazor:
-
-```razor
-@using FSH.Framework.Blazor.UI.Components.Page
-
-<FshPageHeader Title="Page Title"
-               Description="Optional description text">
-    <ActionContent>
-        <!-- Optional action buttons/controls -->
-        <MudButton>Action</MudButton>
-    </ActionContent>
-</FshPageHeader>
+### Endpoint
+```csharp
+public static RouteHandlerBuilder Map(this IEndpointRouteBuilder e) =>
+    e.MapPost("/", async (CreateUserCommand cmd, IMediator m, CancellationToken ct) =>
+        TypedResults.Created($"/users/{await m.Send(cmd, ct)}"))
+    .WithName(nameof(CreateUserCommand))
+    .WithSummary("Create a new user")
+    .RequirePermission(IdentityPermissions.Users.Create);
 ```
 
-**Parameters:**
-- `Title` (required): Main page title
-- `Description` (optional): Description text below title
-- `DescriptionContent` (optional): RenderFragment for complex descriptions
-- `ActionContent` (optional): RenderFragment for action buttons on the right
-- `TitleTypo` (optional): Typography style (default: Typo.h5)
-- `Class` (optional): Additional CSS classes
-- `PageTitleSuffix` (optional): Suffix for browser tab title
-
-**Features:**
-- Modern card design with MudPaper Elevation="2"
-- Subtle gradient background with primary color accent
-- Left border accent in primary color
-- Dark mode support
-
-### FshUserProfile Component
-
-Modern user profile dropdown for app bars/navbars with avatar, user info, and menu:
-
-```razor
-@using FSH.Framework.Blazor.UI.Components.User
-
-<FshUserProfile UserName="@userName"
-                UserEmail="@userEmail"
-                UserRole="@userRole"
-                AvatarUrl="@avatarUrl"
-                OnProfileClick="NavigateToProfile"
-                OnSettingsClick="NavigateToSettings"
-                OnLogoutClick="LogoutAsync" />
+### Validator
+```csharp
+public sealed class CreateUserValidator : AbstractValidator<CreateUserCommand>
+{
+    public CreateUserValidator()
+    {
+        RuleFor(x => x.Email).NotEmpty().EmailAddress();
+    }
+}
 ```
 
-**Parameters:**
-- `UserName` (required): User's display name
-- `UserEmail` (optional): User's email address
-- `UserRole` (optional): User's role or title
-- `AvatarUrl` (optional): URL to user's avatar (shows initials if not provided)
-- `ShowUserName` (optional): Show username next to avatar (default: true, hidden on mobile)
-- `ShowUserInfo` (optional): Show user info in menu header (default: true)
-- `MenuItems` (optional): Custom RenderFragment for menu items (uses default Profile/Settings/Logout if not provided)
-- `OnProfileClick` (optional): Callback for Profile menu item
-- `OnSettingsClick` (optional): Callback for Settings menu item
-- `OnLogoutClick` (optional): Callback for Logout menu item
-
-**Features:**
-- Responsive design (hides username on mobile)
-- Avatar with initials fallback
-- Smooth hover animations and transitions
-- Gradient menu header with user info
-- Customizable menu items via RenderFragment
-- Scoped CSS for isolated styling
-
-### FshStatCard Component
-
-Statistics card for displaying metrics with icon, value, label, and optional badge:
-
-```razor
-@using FSH.Framework.Blazor.UI.Components.Cards
-
-<FshStatCard Icon="@Icons.Material.Filled.People"
-             IconColor="Color.Primary"
-             Value="42"
-             Label="Total Users"
-             Badge="Active"
-             BadgeColor="Color.Success" />
-```
+## Before Committing
 
-**Parameters:**
-- `Icon` (required): MudBlazor icon to display
-- `IconColor` (optional): Color theme for icon and accent (default: Primary)
-- `Value` (required): Main metric value to display
-- `Label` (required): Description of the metric
-- `Badge` (optional): Small badge text below label
-- `BadgeColor` (optional): Color for the badge (default: Primary)
-
-**Features:**
-- Hover animation with lift effect (`translateY(-4px)`) and enhanced shadow
-- Uses MudCard with Elevation="2" for consistent Material Design styling
-- Scoped CSS with `::deep` for proper Blazor CSS isolation
-- Consistent structure matching the original stats-card pattern used throughout the app
-
-### FSH Design Tokens
-
-The framework uses CSS custom properties for consistent styling across all components. These are defined in `fsh-theme.css`:
-
-```css
-:root {
-  /* Border Radius */
-  --fsh-radius: 10px;
-  --fsh-radius-sm: 8px;
-  --fsh-radius-lg: 16px;
-  --fsh-radius-xl: 20px;
-  --fsh-radius-full: 9999px;
-
-  /* Shadows */
-  --fsh-shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
-  --fsh-shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
-  --fsh-shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.1);
-
-  /* Card Styling */
-  --fsh-card-bg: #ffffff;
-  --fsh-card-border: rgba(0, 0, 0, 0.08);
-  --fsh-card-shadow: var(--fsh-shadow-md);
-
-  /* Text Colors */
-  --fsh-text-primary: #1a1a2e;
-  --fsh-text-secondary: #64748b;
-
-  /* Transitions */
-  --fsh-transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
-}
+```bash
+dotnet build src/FSH.Framework.slnx  # Must be 0 warnings
+dotnet test src/FSH.Framework.slnx   # All tests pass
 ```
-
-Dark mode overrides are automatically applied when `.mud-theme-dark` is present. Use these tokens in custom components to ensure consistent styling.
PATCH

echo "Gold patch applied."
