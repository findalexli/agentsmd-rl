#!/usr/bin/env bash
set -euo pipefail

cd /workspace/efcore

# Idempotency guard
if grep -qF ".agents/skills/analyzers/SKILL.md" ".agents/skills/analyzers/SKILL.md" && grep -qF ".agents/skills/bulk-operations/SKILL.md" ".agents/skills/bulk-operations/SKILL.md" && grep -qF ".agents/skills/cosmos-provider/SKILL.md" ".agents/skills/cosmos-provider/SKILL.md" && grep -qF ".agents/skills/dbcontext-and-services/SKILL.md" ".agents/skills/dbcontext-and-services/SKILL.md" && grep -qF "| `user-invocable` | No | Show in agents dropdown (default: true) |" ".agents/skills/make-custom-agent/SKILL.md" && grep -qF "- [ ] Can determine if the skill should be user-invocable or background knowledg" ".agents/skills/make-skill/SKILL.md" && grep -qF "- Model snapshots use `typeof(Dictionary<string, object>)` (property bag format)" ".agents/skills/migrations/SKILL.md" && grep -qF "description: 'Implementation details for EF Core LINQ query translation, SQL gen" ".agents/skills/query-pipeline/SKILL.md" && grep -qF "PRs targeting `release/*` branches require a specific description format and sho" ".agents/skills/servicing-pr/SKILL.md" && grep -qF "2. **Provider overrides**: Override in **every** provider functional test class " ".agents/skills/testing/SKILL.md" && grep -qF "NuGet package `Microsoft.EntityFrameworkCore.Tasks` provides build/publish-time " ".agents/skills/tooling/SKILL.md" && grep -qF "\u2192 `ModificationCommand` per table row, composed of `ColumnModification` per colu" ".agents/skills/update-pipeline/SKILL.md" && grep -qF "Skill files in `.agents/skills/` provide domain-specific knowledge so that agent" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/analyzers/SKILL.md b/.agents/skills/analyzers/SKILL.md
@@ -1,5 +0,0 @@
----
-name: analyzers
-description: 'Implementation details for EF Core Roslyn analyzers. Use when changing analyzers, fix providers, or diagnostic suppressors.'
-user-invocable: false
----
\ No newline at end of file
diff --git a/.agents/skills/bulk-operations/SKILL.md b/.agents/skills/bulk-operations/SKILL.md
@@ -1,5 +0,0 @@
----
-name: bulk-operations
-description: 'Implementation details for EF Core ExecuteUpdate/ExecuteDelete bulk operations. Use when changing UpdateExpression/DeleteExpression LINQ translation or the corresponding SQL AST nodes.'
-user-invocable: false
----
diff --git a/.agents/skills/cosmos-provider/SKILL.md b/.agents/skills/cosmos-provider/SKILL.md
@@ -8,11 +8,6 @@ user-invocable: false
 
 Non-relational provider with its own parallel query pipeline. Uses JSON for document materialization.
 
-## When to Use
-
-- Working on Cosmos SQL generation
-- Working on document storage, partition key configuration, or `CosmosClientWrapper`
-
 ## Key Differences from Relational
 
 - No migrations — use `EnsureCreated()`
diff --git a/.agents/skills/dbcontext-and-services/SKILL.md b/.agents/skills/dbcontext-and-services/SKILL.md
@@ -1,20 +0,0 @@
----
-name: dbcontext-and-services
-description: 'Implementation details for EF Core DbContext and the DI service infrastructure. Use when changing context configuration, service registration, service lifetimes, DbContext pooling, or the Dependencies pattern.'
-user-invocable: false
----
-
-# DbContext & Services
-
-EF Core's internal DI container, service registration, and context lifecycle management.
-
-## Service Registration
-
-`EntityFrameworkServicesBuilder` maintains a `CoreServices` dictionary mapping service types to `ServiceCharacteristics` (lifetime + multi-registration flag).
-
-## Dependencies Pattern
-
-Services receive dependencies via sealed records (not constructor injection of individual services):
-```csharp
-public sealed record MyServiceDependencies(IDep1 Dep1, IDep2 Dep2);
-```
diff --git a/.agents/skills/make-custom-agent/SKILL.md b/.agents/skills/make-custom-agent/SKILL.md
@@ -75,7 +75,7 @@ Supported frontmatter fields:
 | `target` | No | Target environment: `vscode` or `github-copilot` (defaults to both) |
 | `tools` | No | List of allowed tools/tool sets |
 | `model` | No | LLM name or prioritized array of models |
-| `user-invokable` | No | Show in agents dropdown (default: true) |
+| `user-invocable` | No | Show in agents dropdown (default: true) |
 | `disable-model-invocation` | No | Prevent subagent invocation (default: false) |
 | `mcp-servers` | No | MCP server configs for GitHub Copilot target |
 | `metadata` | No | Key-value mapping for additional arbitrary metadata. |
diff --git a/.agents/skills/make-skill/SKILL.md b/.agents/skills/make-skill/SKILL.md
@@ -31,7 +31,7 @@ After investigating, verify:
 - [ ] Can identify common pitfalls or misconceptions about the topic
 - [ ] Can outline a step-by-step skill workflow with clear validation steps
 - [ ] Have search queries for deeper topics
-- [ ] Can determine if the skill should be user-invokable or background knowledge only
+- [ ] Can determine if the skill should be user-invocable or background knowledge only
 
 If there are any ambiguities, gaps in understanding, or multiple valid approaches, ask the user for clarification before proceeding to skill creation.
 Also, evaluate whether the task might be better handled by a custom agent, agentic workflow, an existing skill or multiple narrower skills, and discuss this with the user if relevant.
diff --git a/.agents/skills/migrations/SKILL.md b/.agents/skills/migrations/SKILL.md
@@ -12,6 +12,11 @@ user-invocable: false
 
 **Apply migration**: `Migrator.MigrateAsync()` → reads `__EFMigrationsHistory` → per pending: `MigrationsSqlGenerator.Generate(operations)` → `MigrationCommandExecutor` executes
 
+## Model Snapshot
+
+- Model snapshots use `typeof(Dictionary<string, object>)` (property bag format), not the actual CLR type. When examining the `ClrType` in a snapshot, don't assume it matches the real entity type.
+- `SnapshotModelProcessor.Process()` is used at design-time to fixup older model snapshots for backward compatibility.
+
 ## Testing
 
 Migration operation tests: `test/EFCore.Relational.Tests/Migrations/`. Functional tests: `test/EFCore.{Provider}.FunctionalTests/Migrations/`. Model differ tests: `test/EFCore.Relational.Tests/Migrations/Internal/MigrationsModelDifferTest*.cs`.
\ No newline at end of file
diff --git a/.agents/skills/query-pipeline/SKILL.md b/.agents/skills/query-pipeline/SKILL.md
@@ -1,20 +1,18 @@
 ---
 name: query-pipeline
-description: 'Implementation details for EF Core LINQ query translation and SQL generation. Use when changing expression visitors, SqlExpressions, QuerySqlGenerator, ShaperProcessingExpressionVisitor, or related classes.'
+description: 'Implementation details for EF Core LINQ query translation, SQL generation, and bulk operations (ExecuteUpdate/ExecuteDelete). Use when changing expression visitors, SqlExpressions, QuerySqlGenerator, ShaperProcessingExpressionVisitor, UpdateExpression, DeleteExpression, or related classes.'
 user-invocable: false
 ---
 
 # Query Pipeline
 
-Translates LINQ expressions into database queries and materializes results.
-
 ## Stages
 
-1. **Preprocessing** — `QueryTranslationPreprocessor`: `NavigationExpandingExpressionVisitor` (Include, navigations, auto-includes), `QueryOptimizingExpressionVisitor`
-2. **Translation** — `QueryableMethodTranslatingExpressionVisitor`: LINQ methods → `ShapedQueryExpression` (= `QueryExpression` + `ShaperExpression`). Relational: `RelationalSqlTranslatingExpressionVisitor`, `SelectExpression`
-3. **Postprocessing** — `QueryTranslationPostprocessor`: `SqlNullabilityProcessor`, `SqlTreePruner`, `SqlAliasManager`, `RelationalParameterBasedSqlProcessor`, `SelectExpressionProjectionApplyingExpressionVisitor`, `SqlExpressionSimplifyingExpressionVisitor`, `RelationalValueConverterCompensatingExpressionVisitor`
-4. **Compilation** — `ShapedQueryCompilingExpressionVisitor` → executable delegate. Relational: `ShaperProcessingExpressionVisitor` builds shaper and materialization code
-5. **SQL Generation** — `QuerySqlGenerator`
+1. **Preprocessing**
+2. **Translation**
+3. **Postprocessing**
+4. **Compilation**
+5. **SQL Generation**
 
 ## Validation
 
diff --git a/.agents/skills/servicing-pr/SKILL.md b/.agents/skills/servicing-pr/SKILL.md
@@ -5,7 +5,7 @@ description: 'Create EF Core PRs targeting servicing release branches (release/*
 
 # Servicing PRs
 
-PRs targeting `release/*` branches require a specific description format and should include a quirk (AppContext switch) when applicable.
+PRs targeting `release/*` branches require a specific description format and should include a quirk (AppContext switch) when applicable. When updating progress on a servicing PR, ensure that the description still follows the template.
 
 ## Backport Target Branch
 
diff --git a/.agents/skills/testing/SKILL.md b/.agents/skills/testing/SKILL.md
@@ -6,8 +6,6 @@ user-invocable: false
 
 # Testing
 
-EF Core test infrastructure, patterns, and workflows for unit, specification, and functional tests.
-
 ## Test Categories
 
 ### Unit Tests (`test/EFCore.Tests/`, `test/EFCore.Relational.Tests/`, `test/EFCore.{Provider}.Tests/`)
@@ -67,14 +65,16 @@ Each test gets a fresh model/store. Call `InitializeAsync<TContext>(onModelCreat
 ## Workflow: Adding New Tests
 
 1. **Specification test**: Add to `EFCore.Specification.Tests` (core) or `EFCore.Relational.Specification.Tests` (relational)
-2. **Provider override**: Override in `EFCore.{Provider}.FunctionalTests` with `AssertSql()`
+2. **Provider overrides**: Override in **every** provider functional test class (`EFCore.{Provider}.FunctionalTests`) that inherits the base with provider-appropriate assertions.
 3. **Unit test**: Add to `EFCore.{Provider}.Tests`
 4. Run with `EF_TEST_REWRITE_BASELINES=1` to capture initial baselines
-5. When testing cross-platform code (e.g., file paths, path separators), verify the fix works on both Windows and Linux/macOS
+5. Run tests with project rebuilding enabled (don't use `--no-build`) to ensure code changes are picked up
+6. When testing cross-platform code (e.g., file paths, path separators), verify the fix works on both Windows and Linux/macOS
 
 ## Common Pitfalls
 
 | Pitfall | Solution |
 |---------|----------|
-| SQL or Compiled model baseline mismatch | Set `EF_TEST_REWRITE_BASELINES=1` and re-run |
-| `Check_all_tests_overridden` fails | Override new base test in provider test class |
+| Baseline mismatch (SQL or compiled model) | Re-run with `EF_TEST_REWRITE_BASELINES=1` |
+| `Check_all_tests_overridden` fails | Override the new test in every inheriting provider class |
+| SQL Server feature missing at lower compat level | Gate with `[SqlServerCondition(...)]`|
diff --git a/.agents/skills/tooling/SKILL.md b/.agents/skills/tooling/SKILL.md
@@ -10,23 +10,15 @@ The `dotnet ef` CLI and Visual Studio Package Manager Console commands for migra
 
 ## dotnet-ef CLI (`src/dotnet-ef/`)
 
-`RootCommand` parses global options (`--project`, `--startup-project`, `--framework`, `--configuration`, `--runtime`, `--no-build`). Subcommands implemented in `src/ef/Commands/` (`Microsoft.EntityFrameworkCore.Tools.Commands`): `DatabaseCommand`, `DbContextCommand`, `MigrationsCommand`. Each invokes MSBuild to build, then shells out via `dotnet exec ef.dll`, which hosts `OperationExecutor`.
+`RootCommand` parses global options. Subcommands implemented in `src/ef/Commands/`. Each invokes MSBuild to build, then shells out via `dotnet exec ef.dll`, which hosts `OperationExecutor`.
 
 ## PMC (`src/EFCore.Tools/`)
 
-PowerShell module: `Add-Migration`, `Update-Database`, `Scaffold-DbContext`, `Optimize-DbContext`, etc. Routes to `OperationExecutor`.
+PowerShell module: `Add-Migration`, `Update-Database`, `Scaffold-DbContext`, `Optimize-DbContext`, etc.
 
 ## MSBuild Tasks (`src/EFCore.Tasks/`)
 
-NuGet package `Microsoft.EntityFrameworkCore.Tasks` provides build/publish-time compiled model and precompiled query generation.
-
-### Build Integration Flow
-
-Targets in `buildTransitive/Microsoft.EntityFrameworkCore.Tasks.targets`:
-- **Build flow**: `_EFGenerateFilesAfterBuild` triggers after compilation when `EFOptimizeContext=true` and stage is `build`. Invokes `OptimizeDbContext` task, writes generated file list, re-triggers `Build` to compile new files.
-- **Publish flow**: `_EFGenerateFilesBeforePublish` runs before `GeneratePublishDependencyFile`. Auto-activates for `PublishAOT=true`. `_EFPrepareDependenciesForPublishAOT` cascades to project references.
-- **Incremental**: `_EFProcessGeneratedFiles` reads tracking files and adds `.g.cs` to `@(Compile)`. Stale files removed by `_EFPrepareForCompile`.
-- **Clean**: `_EFCleanGeneratedFiles` deletes generated and tracking files.
+NuGet package `Microsoft.EntityFrameworkCore.Tasks` provides build/publish-time compiled model and precompiled query generation. Targets in `buildTransitive/Microsoft.EntityFrameworkCore.Tasks.targets`.
 
 ## Testing
 
diff --git a/.agents/skills/update-pipeline/SKILL.md b/.agents/skills/update-pipeline/SKILL.md
@@ -13,16 +13,14 @@ Converts tracked entity changes into database INSERT/UPDATE/DELETE commands duri
 `SaveChanges()` → `DetectChanges()` → `IDatabase.SaveChanges()`
   → `UpdateAdapter` creates `IUpdateEntry` list
   → `CommandBatchPreparer.BatchCommands()`
-    → `ModificationCommand` per entity (maps to table row), composed of `ColumnModification` (maps to column value)
+    → `ModificationCommand` per table row, composed of `ColumnModification` per column
+      → `SharedTableEntryMap` is used to track entries mapped to the same row
     → Topological sort via Multigraph (FK dependency ordering)
     → Groups into `ModificationCommandBatch` (respects max batch size)
   → `UpdateSqlGenerator` generates SQL per batch
   → `BatchExecutor` executes all batches in a transaction
   → `StateManager.AcceptAllChanges()`
 
-Other Key Files:
-- `src/EFCore.Relational/Update/Internal/SharedTableEntryMap.cs` — manages entries mapped to the same row
-
 ## Concurrency
 
 Concurrency tokens → WHERE conditions on UPDATE/DELETE. `AffectedCountModificationCommandBatch` checks affected rows. Throws `DbUpdateConcurrencyException` on mismatch.
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,179 +1,40 @@
 # Entity Framework Core - GitHub Copilot Instructions
 
-This document provides guidance for GitHub Copilot when generating code for the Entity Framework Core project. Follow these guidelines to ensure that generated code aligns with the project's coding standards and architectural principles.
+This document provides guidance for working with code in the Entity Framework Core project.
 
-If you are not sure, do not guess, just tell that you don't know or ask clarifying questions. Don't copy code that follows the same pattern in a different context. Don't rely just on names, evaluate the code based on the implementation and usage. Verify that the generated code is correct and compilable.
+If you are not sure, do not guess, just tell that you don't know or ask clarifying questions.
+Don't just copy code that follows the same pattern in a different context.
+Don't rely just on names to guess its function, evaluate the code based on the implementation and usage.
 
 ## Code Style
 
-### General Guidelines
-
 - Follow the [.NET coding guidelines](https://github.com/dotnet/runtime/blob/main/docs/coding-guidelines/coding-style.md) unless explicitly overridden below
 - Use the rules defined in the .editorconfig file in the root of the repository for any ambiguous cases
 - Write code that is clean, maintainable, and easy to understand
 - Favor readability over brevity, but keep methods focused and concise
-- **Prefer minimal comments** - The code should be self-explanatory. Add comments sparingly and only to explain *why* a non-intuitive solution was necessary, not *what* the code does. Comments are appropriate for complex logic, public APIs, or domain-specific implementations where context would otherwise be unclear
-- Add license header to all files:
-```
-    // Licensed to the .NET Foundation under one or more agreements.
-    // The .NET Foundation licenses this file to you under the MIT license.
-```
-- Don't add the UTF-8 BOM to files unless they have non-ASCII characters
-- Avoid breaking public APIs. If you need to break a public API, add a new API instead and mark the old one as obsolete. Use `ObsoleteAttribute` with the message pointing to the new API
-- All types should be public by default
-- Types in `.Internal` namespaces or annotated with `[EntityFrameworkInternal]` require this XML doc comment on ALL members:
-```csharp
-/// <summary>
-///     This is an internal API that supports the Entity Framework Core infrastructure and not subject to
-///     the same compatibility standards as public APIs. It may be changed or removed without notice in
-///     any release. You should only use it directly in your code with extreme caution and knowing that
-///     doing so can result in application failures when updating to a new Entity Framework Core release.
-/// </summary>
-```
-
-### Formatting
-
-- Use spaces for indentation (4 spaces)
-- Use braces for all blocks including single-line blocks
-- Place braces on new lines
-- Limit line length to 140 characters
-- Trim trailing whitespace
-- All declarations must begin on a new line
-- Use a single blank line to separate logical sections of code when appropriate
-- Insert a final newline at the end of files
-
-### C# Specific Guidelines
-
-- File scoped namespace declarations
-- Use `var` for local variables
-- Use expression-bodied members where appropriate
-- Prefer using collection expressions when possible
-- Use `is` pattern matching instead of `as` followed by null checks (e.g., `if (obj is SomeType typed)` instead of `var typed = obj as SomeType; if (typed != null)`)
-- Prefer `switch` expressions over `switch` statements when appropriate
-- Prefer pattern matching with `when` clauses in switch expressions for conditional logic
-- Prefer field-backed property declarations using field contextual keyword instead of an explicit field.
-- Prefer range and index from end operators for indexer access
-- The projects use implicit namespaces, so do not add `using` directives for namespaces that are already imported by the project
-- When verifying that a file doesn't produce compiler errors rebuild the whole project
-
-### Naming Conventions
-
-- Use PascalCase for:
-  - Classes, structs, enums, properties, methods, events, namespaces, delegates
-  - Public fields
-  - Static private fields
-  - Constants
-- Use camelCase for:
-  - Parameters
-  - Local variables
-- Use `_camelCase` for instance private fields
-- Prefix interfaces with `I`
-- Prefix type parameters with `T`
-- Use meaningful and descriptive names
-
-### Nullability
-
-- Use nullable reference types
-- Use proper null-checking patterns
-- Use the null-conditional operator (`?.`) and null-coalescing operator (`??`) when appropriate
-- Don't disable nullability with a preprocessor directive (`#nullable disable`)
+- **Prefer minimal comments** - The code should be self-explanatory. Add comments sparingly and only to explain *why* a non-intuitive solution was necessary, not *what* the code does. Comments are appropriate for complex logic, public APIs, or domain-specific implementations where context would otherwise be unclear. Use `Check.DebugAssert` instead of a comment if possible.
 
-## Architecture and Design Patterns
-
-### Dependency Injection
-
-- Design services to be registered and resolved through the DI container for functionality that could be replaced or extended by users, providers or plug-ins
-- Create sealed records with names ending in `Dependencies` containing the service dependencies
-
-### Testing
-
-- Follow the existing test patterns in the corresponding test projects
-- Run tests with project rebuilding enabled (don't use `--no-build`) to ensure code changes are picked up
-- After changing public APIs, run `build.cmd` / `build.sh` to refresh the checked-in `*.baseline.json` files
-
-#### API baselining
-- Public API surface is tracked in checked-in `*.baseline.json` files under `src/`
-- Normal dev loop: make the API change, run EFCore.ApiBaseline.Tests, review the diff, and check in the updated baseline if the change is intentional
-- On CI these tests fail on baseline mismatches
-- API stages (`Stable`, `Experimental`, `Obsolete`) are part of the baseline
-- Pubternal APIs marked with `.Internal` / `[EntityFrameworkInternal]` are not treated as public API
-- When a PR with API changes is merged, a workflow labels the PR with `api-review`, generates ApiChief diffs between the old and new baselines, and posts them as PR comments for review
-
-#### Environment Setup
+## Environment Setup
 - **ALWAYS** run `restore.cmd` (Windows) or `. ./restore.sh` (Linux/Mac) first to restore dependencies
 - **ALWAYS** run `. .\activate.ps1` (PowerShell) or `. ./activate.sh` (Bash) to set up the development environment with correct SDK versions before building or running the tests
-- These scripts set `DOTNET_ROOT`, `DOTNET_MULTILEVEL_LOOKUP`, and PATH for the project's specific .NET SDK version
-
-## Documentation
-
-- Include XML documentation for all public APIs
-- Add proper `<remarks>` tags with links to relevant documentation where helpful
-- For keywords like `null`, `true` or `false` use `<see langword="*" />` tags
-- Use `<see href="https://aka.ms/efcore-docs-*">` redirects for doc links instead of hardcoded `https://learn.microsoft.com/` links
-- Include code examples in documentation where appropriate
-- Overriding members should inherit the XML documentation from the base type via `/// <inheritdoc />`
-
-## Error Handling
-
-- Use appropriate exception types. 
-- **ALL** user-facing error messages must use string resources from the `.resx` (and the generated `.Designer.cs`) file corresponding to the project
-- Avoid catching exceptions without rethrowing them
 
 ## Dependency and Version Management
 
 - **NEVER** hardcode package versions in `.csproj` files
-- Check `eng/Versions.props` for existing version properties (e.g., `$(SQLitePCLRawVersion)`) before adding or updating package references
-- Use `Directory.Packages.props` for NuGet package version management with Central Package Management (CPM)
-- Packages listed in `eng/Version.Details.xml` are managed by Maestro dependency flow and should not be updated manually or by Dependabot
-
-## Asynchronous Programming
-
-- Provide both synchronous and asynchronous versions of methods where appropriate
-- Use the `Async` suffix for asynchronous methods
-- Return `Task` or `ValueTask` from asynchronous methods
-- Use `CancellationToken` parameters to support cancellation
-- Avoid async void methods except for event handlers
-- Call `ConfigureAwait(false)` on awaited calls to avoid deadlocks
-
-## Performance Considerations
-
-- Be mindful of performance implications, especially for database operations
-- Avoid unnecessary allocations
-- Consider using more efficient code that is expected to be on the hot path, even if it is less readable
+- Use `eng/Versions.props` and `Directory.Packages.props` for NuGet package version management
 
 ## Implementation Guidelines
 
 - Write code that is secure by default. Avoid exposing potentially private or sensitive data
 - Make code NativeAOT compatible when possible. This means avoiding dynamic code generation, reflection, and other features that are not compatible with NativeAOT. If not possible, mark the code with an appropriate annotation or throw an exception
 - After implementing a fix, review the surrounding code for similar patterns that might need the same change
-
-### Entity Framework Core Specific guidelines
-
-- Use the logging infrastructure for diagnostics and interception
-- Prefer using `Check.DebugAssert` instead of `Debug.Assert` or comments
-- Use `Check.NotNull` and `Check.NotEmpty` for preconditions in public APIs
-  - The methods in `Check` class use `[CallerArgumentExpression]` to automatically capture parameter names
+- Be mindful of performance implications, especially for database operations
+- Avoid breaking public APIs. If you need to break a public API, add a new API instead and mark the old one as obsolete. Use `ObsoleteAttribute` with the message pointing to the new API
+- If a public API is changed, run EFCore.ApiBaseline.Tests
+- All types should be public by default, but types in `.Internal` namespaces or annotated with `[EntityFrameworkInternal]` require a specific XML doc comment on ALL members.
+- **ALL** user-facing error messages must use string resources from the `.resx` (and the generated `.Designer.cs`) file corresponding to the project
+- Call `ConfigureAwait(false)` on awaited asynchronous calls to avoid deadlocks
 
 ## Agent Skills
 
-Skill files in `.agents/skills/` provide domain-specific knowledge for Copilot agents. When you spend significant time investigating the codebase to understand an implementation during a session (e.g., tracing through code paths, discovering key files, understanding non-obvious patterns), update the relevant skill's `SKILL.md` with your findings so future tasks can be completed more efficiently. Only add information that is broadly useful and not specific to a single task. Keep additions concise and stable, avoid speculation or information that can be easily found by reading a single file.
-
-## Repository Structure
-
-- src/: Main product source code, including providers, tools, and analyzers
-- test/: All test projects, including unit, functional, and specification tests for different providers
-- benchmark/: Performance and benchmarking projects for EFCore
-- tools/: Utility scripts and resources for development
-- eng/: Build and test infrastructure files related to [Arcade SDK](https://github.com/dotnet/arcade/blob/main/Documentation/ArcadeSdk.md) used for building the project, and running the tests
-- docs/: Documentation files for contributors and users. Full documentation is available at [EF Core | Learn](https://learn.microsoft.com/ef/core/)
-- .github/: GitHub-specific files, workflows, and Copilot instructions
-- .config/: AzDo pipelines configuration files
-
-## Pull Request Guidelines
-
-- **ALWAYS** target the `main` branch for new PRs unless explicitly instructed otherwise
-- For servicing PRs (fixes targeting release branches), use the `servicing-pr` skill
-
-## Overview of Entity Framework Core
-
-Entity Framework Core (EF Core) is an object-database mapper for .NET. It manages entity objects via `DbContext`, translates LINQ queries into database queries, tracks entity changes, and persists them via `SaveChanges()`. The model defines entities, properties, keys, relationships, and mappings — built via conventions, data annotations, and the fluent API. EF Core is database-agnostic; providers implement translation, type mapping, and database-specific behaviors. See the skills in `.agents/skills/` for detailed architecture of each subsystem.
+Skill files in `.agents/skills/` provide domain-specific knowledge so that agents don't need repetitive instructions from the user. Keep skills updated: when you discover non-obvious patterns, key files, or recurring review feedback during a session, distill the insight into the relevant `SKILL.md`. Additions must be concise, broadly useful, and stable — avoid task-specific details, speculation, and statements that contradict existing content. Remove or correct stale information rather than appending conflicting rules.
PATCH

echo "Gold patch applied."
