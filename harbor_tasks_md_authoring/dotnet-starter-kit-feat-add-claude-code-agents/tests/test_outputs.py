"""Behavioral checks for dotnet-starter-kit-feat-add-claude-code-agents (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-starter-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/architecture-guard.md')
    assert "description: Verify changes don't violate architecture rules. Run architecture tests, check module boundaries, verify BuildingBlocks aren't modified. Use before commits or PRs." in text, "expected to find: " + "description: Verify changes don't violate architecture rules. Run architecture tests, check module boundaries, verify BuildingBlocks aren't modified. Use before commits or PRs."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/architecture-guard.md')
    assert 'You are an architecture guardian for FullStackHero .NET Starter Kit. Your job is to verify architectural integrity.' in text, "expected to find: " + 'You are an architecture guardian for FullStackHero .NET Starter Kit. Your job is to verify architectural integrity.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/architecture-guard.md')
    assert 'If any files listed: **STOP** - BuildingBlocks changes require explicit approval.' in text, "expected to find: " + 'If any files listed: **STOP** - BuildingBlocks changes require explicit approval.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-reviewer.md')
    assert 'description: Review code changes against FSH patterns and conventions. Use proactively after any code modifications to catch violations before commit.' in text, "expected to find: " + 'description: Review code changes against FSH patterns and conventions. Use proactively after any code modifications to catch violations before commit.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-reviewer.md')
    assert 'You are a code reviewer for the FullStackHero .NET Starter Kit. Your job is to review code changes and ensure they follow FSH patterns.' in text, "expected to find: " + 'You are a code reviewer for the FullStackHero .NET Starter Kit. Your job is to review code changes and ensure they follow FSH patterns.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/code-reviewer.md')
    assert '- [ ] Implements required interfaces (IHasTenant, IAuditableEntity, ISoftDeletable)' in text, "expected to find: " + '- [ ] Implements required interfaces (IHasTenant, IAuditableEntity, ISoftDeletable)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/feature-scaffolder.md')
    assert 'description: Generate complete feature folders with Command, Handler, Validator, and Endpoint files. Use when creating new API endpoints or features.' in text, "expected to find: " + 'description: Generate complete feature folders with Command, Handler, Validator, and Endpoint files. Use when creating new API endpoints or features.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/feature-scaffolder.md')
    assert 'You are a feature scaffolder for FullStackHero .NET Starter Kit. Your job is to generate complete vertical slice features.' in text, "expected to find: " + 'You are a feature scaffolder for FullStackHero .NET Starter Kit. Your job is to generate complete vertical slice features.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/feature-scaffolder.md')
    assert 'ICurrentUser currentUser) : ICommandHandler<{Action}{Entity}Command, {Action}{Entity}Response>' in text, "expected to find: " + 'ICurrentUser currentUser) : ICommandHandler<{Action}{Entity}Command, {Action}{Entity}Response>'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/migration-helper.md')
    assert 'description: Handle EF Core migrations safely. Create, apply, and manage database migrations for FSH multi-tenant setup. Use when adding entities or changing database schema.' in text, "expected to find: " + 'description: Handle EF Core migrations safely. Create, apply, and manage database migrations for FSH multi-tenant setup. Use when adding entities or changing database schema.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/migration-helper.md')
    assert 'You are a migration helper for FullStackHero .NET Starter Kit. Your job is to safely manage EF Core migrations.' in text, "expected to find: " + 'You are a migration helper for FullStackHero .NET Starter Kit. Your job is to safely manage EF Core migrations.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/migration-helper.md')
    assert 'The framework handles tenant database migrations automatically on startup via `UseHeroMultiTenantDatabases()`.' in text, "expected to find: " + 'The framework handles tenant database migrations automatically on startup via `UseHeroMultiTenantDatabases()`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/module-creator.md')
    assert 'description: Create new modules (bounded contexts) with complete project structure, DbContext, permissions, and registration. Use when adding a new business domain.' in text, "expected to find: " + 'description: Create new modules (bounded contexts) with complete project structure, DbContext, permissions, and registration. Use when adding a new business domain.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/module-creator.md')
    assert 'dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}.Contracts/Modules.{Name}.Contracts.csproj' in text, "expected to find: " + 'dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}.Contracts/Modules.{Name}.Contracts.csproj'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/module-creator.md')
    assert 'You are a module creator for FullStackHero .NET Starter Kit. Your job is to scaffold complete new modules.' in text, "expected to find: " + 'You are a module creator for FullStackHero .NET Starter Kit. Your job is to scaffold complete new modules.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/api-conventions.md')
    assert 'endpoints.MapGet("/", async ([AsParameters] GetProductsQuery query, ...) => ...)' in text, "expected to find: " + 'endpoints.MapGet("/", async ([AsParameters] GetProductsQuery query, ...) => ...)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/api-conventions.md')
    assert '.RequirePermission(Permission)          // Required: Or .AllowAnonymous()' in text, "expected to find: " + '.RequirePermission(Permission)          // Required: Or .AllowAnonymous()'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/api-conventions.md')
    assert '.WithSummary("Description")             // Required: OpenAPI description' in text, "expected to find: " + '.WithSummary("Description")             // Required: OpenAPI description'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/buildingblocks-protection.md')
    assert 'Changes to BuildingBlocks affect ALL modules across the entire framework. These are core abstractions that many projects depend on.' in text, "expected to find: " + 'Changes to BuildingBlocks affect ALL modules across the entire framework. These are core abstractions that many projects depend on.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/buildingblocks-protection.md')
    assert "Do not proceed. Suggest alternatives that don't require BuildingBlocks modifications." in text, "expected to find: " + "Do not proceed. Suggest alternatives that don't require BuildingBlocks modifications."[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/buildingblocks-protection.md')
    assert '1. **Confirm explicit approval** - Has the user specifically approved this change?' in text, "expected to find: " + '1. **Confirm explicit approval** - Has the user specifically approved this change?'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing-rules.md')
    assert 'Architecture tests in `Architecture.Tests/` are mandatory and enforce:' in text, "expected to find: " + 'Architecture tests in `Architecture.Tests/` are mandatory and enforce:'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing-rules.md')
    assert 'var result = await _handler.Handle(command, CancellationToken.None);' in text, "expected to find: " + 'var result = await _handler.Handle(command, CancellationToken.None);'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing-rules.md')
    assert '├── Architecture.Tests/    # Layering enforcement (mandatory)' in text, "expected to find: " + '├── Architecture.Tests/    # Layering enforcement (mandatory)'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-entity/SKILL.md')
    assert 'description: Create a domain entity with multi-tenancy, auditing, soft-delete, and domain events. Use when adding new database entities to a module.' in text, "expected to find: " + 'description: Create a domain entity with multi-tenancy, auditing, soft-delete, and domain events. Use when adding new database entities to a module.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-entity/SKILL.md')
    assert 'public sealed class {Entity} : AggregateRoot<Guid>, IHasTenant, IAuditableEntity, ISoftDeletable' in text, "expected to find: " + 'public sealed class {Entity} : AggregateRoot<Guid>, IHasTenant, IAuditableEntity, ISoftDeletable'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-entity/SKILL.md')
    assert 'modelBuilder.ApplyConfigurationsFromAssembly(typeof({Module}DbContext).Assembly);' in text, "expected to find: " + 'modelBuilder.ApplyConfigurationsFromAssembly(typeof({Module}DbContext).Assembly);'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-feature/SKILL.md')
    assert 'description: Create a new API endpoint with Command, Handler, Validator, and Endpoint following FSH vertical slice architecture. Use when adding any new feature, API endpoint, or business operation.' in text, "expected to find: " + 'description: Create a new API endpoint with Command, Handler, Validator, and Endpoint following FSH vertical slice architecture. Use when adding any new feature, API endpoint, or business operation.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-feature/SKILL.md')
    assert 'ICurrentUser currentUser) : ICommandHandler<Create{Entity}Command, Create{Entity}Response>' in text, "expected to find: " + 'ICurrentUser currentUser) : ICommandHandler<Create{Entity}Command, Create{Entity}Response>'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-feature/SKILL.md')
    assert 'public sealed class Create{Entity}Validator : AbstractValidator<Create{Entity}Command>' in text, "expected to find: " + 'public sealed class Create{Entity}Validator : AbstractValidator<Create{Entity}Command>'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-module/SKILL.md')
    assert 'description: Create a new module (bounded context) with proper project structure, permissions, DbContext, and registration. Use when adding a new business domain that needs its own entities and endpoi' in text, "expected to find: " + 'description: Create a new module (bounded context) with proper project structure, permissions, DbContext, and registration. Use when adding a new business domain that needs its own entities and endpoi'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-module/SKILL.md')
    assert 'dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}.Contracts/Modules.{Name}.Contracts.csproj' in text, "expected to find: " + 'dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}.Contracts/Modules.{Name}.Contracts.csproj'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-module/SKILL.md')
    assert 'dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}/Modules.{Name}.csproj' in text, "expected to find: " + 'dotnet sln src/FSH.Framework.slnx add src/Modules/{Name}/Modules.{Name}/Modules.{Name}.csproj'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/mediator-reference/SKILL.md')
    assert 'description: Mediator library patterns and interfaces for FSH. This project uses the Mediator source generator, NOT MediatR. Reference when implementing commands, queries, and handlers.' in text, "expected to find: " + 'description: Mediator library patterns and interfaces for FSH. This project uses the Mediator source generator, NOT MediatR. Reference when implementing commands, queries, and handlers.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/mediator-reference/SKILL.md')
    assert 'These are different libraries with different interfaces. Using MediatR interfaces will cause build errors.' in text, "expected to find: " + 'These are different libraries with different interfaces. Using MediatR interfaces will cause build errors.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/mediator-reference/SKILL.md')
    assert '| Command Handler | `ICommandHandler<TCommand, TResponse>` | `IRequestHandler<TRequest, TResponse>` |' in text, "expected to find: " + '| Command Handler | `ICommandHandler<TCommand, TResponse>` | `IRequestHandler<TRequest, TResponse>` |'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/query-patterns/SKILL.md')
    assert 'description: Query patterns including pagination, search, filtering, and specifications for FSH. Use when implementing GET endpoints that return lists or need filtering.' in text, "expected to find: " + 'description: Query patterns including pagination, search, filtering, and specifications for FSH. Use when implementing GET endpoints that return lists or need filtering.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/query-patterns/SKILL.md')
    assert 'public sealed class {Entity}ByIdSpec : Specification<{Entity}, {Entity}Dto>, ISingleResultSpecification<{Entity}>' in text, "expected to find: " + 'public sealed class {Entity}ByIdSpec : Specification<{Entity}, {Entity}Dto>, ISingleResultSpecification<{Entity}>'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/query-patterns/SKILL.md')
    assert 'public static RouteHandlerBuilder MapGet{Entities}Endpoint(this IEndpointRouteBuilder endpoints) =>' in text, "expected to find: " + 'public static RouteHandlerBuilder MapGet{Entities}Endpoint(this IEndpointRouteBuilder endpoints) =>'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-guide/SKILL.md')
    assert 'description: Write unit tests, integration tests, and architecture tests for FSH features. Use when adding tests or understanding the testing strategy.' in text, "expected to find: " + 'description: Write unit tests, integration tests, and architecture tests for FSH features. Use when adding tests or understanding the testing strategy.'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-guide/SKILL.md')
    assert 'Architecture tests enforce module boundaries and layering. They run on every build.' in text, "expected to find: " + 'Architecture tests enforce module boundaries and layering. They run on every build.'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/testing-guide/SKILL.md')
    assert '.Setup(x => x.AddAsync(It.IsAny<{Entity}>(), It.IsAny<CancellationToken>()))' in text, "expected to find: " + '.Setup(x => x.AddAsync(It.IsAny<{Entity}>(), It.IsAny<CancellationToken>()))'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'e.MapPost("/", async (CreateUserCommand cmd, IMediator m, CancellationToken ct) =>' in text, "expected to find: " + 'e.MapPost("/", async (CreateUserCommand cmd, IMediator m, CancellationToken ct) =>'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'public async ValueTask<Guid> Handle(CreateUserCommand cmd, CancellationToken ct)' in text, "expected to find: " + 'public async ValueTask<Guid> Handle(CreateUserCommand cmd, CancellationToken ct)'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'public sealed class CreateUserValidator : AbstractValidator<CreateUserCommand>' in text, "expected to find: " + 'public sealed class CreateUserValidator : AbstractValidator<CreateUserCommand>'[:80]

