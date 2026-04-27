# Add APIs to remove a previously registered provider extension and DbContext

The repo at `/workspace/efcore/` is checked out at the parent of dotnet/efcore PR #37891. Your job is to add three new public APIs to Entity Framework Core so that consumers (typically integration-test code) can *undo* a prior provider configuration.

## Background

Since .NET 9, `DbContextOptions<TContext>` is no longer mutated in place. Configuration is composed via `IDbContextOptionsConfiguration<TContext>` instances registered in DI, and the per-extension state on `DbContextOptions` is stored in an *immutable* extensions map (each extension carries an ordinal that determines iteration order).

There is currently no public way to:

1. Remove an extension that was previously added through `IDbContextOptionsBuilderInfrastructure.AddOrUpdateExtension<TExtension>(...)`.
2. Produce a new `DbContextOptions` that is the same as a given one but with a particular extension stripped.
3. Remove all DI registrations for a given `DbContext` (so it can be re-registered against a different provider — a common need in integration tests that swap SqlServer for InMemory).

Add the three APIs described below. Implementations belong in the EF Core core source tree. Do not modify any files under `test/`.

## API 1 — `IDbContextOptionsBuilderInfrastructure.RemoveExtension<TExtension>()`

Add a new method to the public interface `IDbContextOptionsBuilderInfrastructure` (in `Microsoft.EntityFrameworkCore.Infrastructure`):

```csharp
void RemoveExtension<TExtension>()
    where TExtension : class, IDbContextOptionsExtension;
```

Behavior:

- After `AddOrUpdateExtension(extension)` followed by `RemoveExtension<TThatExtension>()`, the builder's `Options.FindExtension<TThatExtension>()` must return `null` and the extension type must not appear in `Options.Extensions`.
- Calling `RemoveExtension<TExtension>()` for a type that was never added is a **no-op** — other extensions on the builder are preserved untouched.

The default implementation on the existing `DbContextOptionsBuilder` class should delegate to the new immutable counterpart on `DbContextOptions` described in API 2.

## API 2 — `DbContextOptions.WithoutExtension<TExtension>()`

Add the immutable counterpart to the existing `WithExtension` on the abstract base `DbContextOptions` and override it in the generic `DbContextOptions<TContext>`:

```csharp
public abstract DbContextOptions WithoutExtension<TExtension>()
    where TExtension : class, IDbContextOptionsExtension;
```

Behavior:

- If the requested extension type is **not** present in the options, return the *same instance* (`this`). Callers rely on reference equality to detect "no change". This is similar in spirit to how `IImmutableDictionary.Remove` returns the same instance for a no-op.
- Otherwise, return a new `DbContextOptions<TContext>` whose extensions map is the original map with the requested extension removed.
- The new options' `Extensions` enumeration must preserve the **insertion order of the remaining extensions** — extensions that came before the removed one must still come before extensions that came after it. Furthermore, after a `WithoutExtension`-then-`WithExtension` sequence the iteration order must remain contiguous, with the freshly added extension appearing *last*. Concretely, if you add three extensions A, B, C (in that order), call `WithoutExtension<B>()`, and then add a fresh extension D, the resulting `Options.Extensions` enumeration must yield exactly `[A, C, D]` in that order.

## API 3 — `IServiceCollection.RemoveDbContext<TContext>(bool removeConfigurationOnly = false)`

Add a new public extension method on `IServiceCollection`, alongside the existing `AddDbContext` / `ConfigureDbContext` extension methods in EF Core:

```csharp
public static IServiceCollection RemoveDbContext<TContext>(
    this IServiceCollection serviceCollection,
    bool removeConfigurationOnly = false)
    where TContext : DbContext;
```

Behavior:

- When `removeConfigurationOnly` is `false` (default), remove **all** of the following service-type registrations whose generic argument is `TContext`:
  - `TContext`
  - `DbContextOptions<TContext>`
  - `IDbContextOptionsConfiguration<TContext>`
  - `IDbContextFactorySource<TContext>`
  - `IDbContextFactory<TContext>`
  - `IDbContextPool<TContext>`
  - `IScopedDbContextLease<TContext>`
- When `removeConfigurationOnly` is `true`, only registrations of `IDbContextOptionsConfiguration<TContext>` are removed; `TContext` and `DbContextOptions<TContext>` stay registered.
- Registrations belonging to a *different* `DbContext` type must not be affected.
- The non-generic `DbContextOptions` forwarding registration must **not** be removed (it may be shared with a different context).
- The method must validate its argument with the project's standard `Check.NotNull(serviceCollection)` helper.
- The method returns the same `IServiceCollection` so calls can be chained.

After `serviceCollection.RemoveDbContext<MyContext>()` is called, calling `serviceCollection.AddDbContext<MyContext>(options => options.UseInMemoryDatabase("X"))` and then resolving `MyContext` from the built provider must produce a context that uses the new configuration (`InMemoryDatabase("X")`), not the original one.

## Code Style Requirements

This codebase has explicit style rules in `.github/copilot-instructions.md` that apply to your implementation:

- All newly created C# source files must begin with the MIT license header:

  ```csharp
  // Licensed to the .NET Foundation under one or more agreements.
  // The .NET Foundation licenses this file to you under the MIT license.
  ```

- All new public APIs require XML documentation (`<summary>`, `<typeparam>`, `<param>`, `<returns>`). When adding doc links, use the `https://aka.ms/efcore-docs-*` redirect form rather than hardcoded `learn.microsoft.com` URLs.
- Use file-scoped namespace declarations and `var` for local variables.
- Use `Check.NotNull` for non-null preconditions on public-API parameters (no manual `if (x == null) throw …`).
- Do not break or modify existing public APIs. Only *add* new members.
- Use 4-space indentation; no UTF-8 BOM unless the file contains non-ASCII characters.
- Comments inside method bodies should be sparing and only explain non-obvious *why*, not *what*.

The full conventions live at `.github/copilot-instructions.md` in the repo root.

## How to verify

Build with:

```
dotnet build /workspace/efcore/test/EFCore.Tests/EFCore.Tests.csproj
```

If the build fails the verifier cannot run, so make sure the project compiles before you finish. The verifier exercises the new APIs through the public surface only.
