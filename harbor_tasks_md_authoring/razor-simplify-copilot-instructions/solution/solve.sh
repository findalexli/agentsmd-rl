#!/usr/bin/env bash
set -euo pipefail

cd /workspace/razor

# Idempotency guard
if grep -qF "- **RazorCodeDocument**: Immutable \u2014 every `With*` method creates a new instance" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,102 +1,49 @@
-﻿# GitHub Copilot Instructions for ASP.NET Core Razor
+# GitHub Copilot Instructions for ASP.NET Core Razor
 
-This repository contains the **ASP.NET Core Razor** compiler and tooling implementation. It provides the Razor language experience across Visual Studio, Visual Studio Code, and other development environments.
+## Critical Rules
 
-## Repository Overview
+- **Build**: Use `build.cmd` (Windows) or `./build.sh` (Linux/Mac). NEVER use `dotnet build` directly.
+- **Test**: Use `build.cmd -test` or target a specific project with `dotnet test path/to/Project.csproj`. NEVER run `dotnet test` at the repo root — it includes Playwright integration tests that require VS Code and waste significant time.
+- **Processes**: NEVER kill dotnet processes by name (`Stop-Process -Name`, `taskkill /IM`). Other work may be running on the machine.
+- **Bug fixes**: Look for existing code that already handles the scenario before adding new code. The bug is more likely in existing logic than a missing feature.
+- **Helpers**: Review existing helpers (`UsingDirectiveHelper`, `AddUsingsHelper`, etc.) before writing new utility methods. Don't duplicate.
 
-This repository implements:
+## File Types
 
-- **Razor Compiler**: The core Razor compilation engine and source generators
-- **Language Server**: LSP-based language services for cross-platform editor support
-- **Visual Studio Integration**: Rich editing experience and tooling for Visual Studio
-- **Visual Studio Code Extension**: Rich editing experience and tooling for Visual Studio
-- **IDE Tools**: Debugging, IntelliSense, formatting, and other developer productivity features
+- `.razor` — Blazor components. `.cshtml` — Razor views/pages (referred to as "Legacy" in the codebase).
 
-## Razor Language Concepts
+## Code Patterns
 
-When working with this codebase, understand these core Razor concepts:
+- **Collections**: Use `ListPool<T>.GetPooledObject(out var list)` and `PooledArrayBuilder<T>` instead of allocating new collections. Prefer immutable collection types.
+- **Positions**: Use `GetRequiredAbsoluteIndex` for converting positions to absolute indexes.
+- **LSP conversions**: `sourceText.GetTextChange(textEdit)` converts LSP `TextEdit` → Roslyn `TextChange`. Reverse: `sourceText.GetTextEdit(change)`. Both in `LspExtensions_SourceText.cs`.
+- **RazorCodeDocument**: Immutable — every `With*` method creates a new instance passing ALL fields through the constructor. When adding a new field, thread it through every existing `With*` method. Prefer computing derived data via extension methods (e.g., `GetUnusedDirectives()`) rather than storing computed results as fields.
+- **Razor documents in Roslyn**: Stored as additional documents. Resolve via `solution.GetDocumentIdsWithFilePath(filePath)` → `solution.GetAdditionalDocument(documentId)`.
+- **Remote services**: Place the public stub method (calling `RunServiceAsync`) directly above its private implementation method.
 
-### File Types and Extensions
-- `.razor` - Blazor components (client-side and server-side)
-- `.cshtml` - Razor views and pages (ASP.NET Core MVC/Pages) also referred to as "Legacy" in the codebase
+## Testing
 
-### Language Kinds
-Razor documents contain multiple languages:
-- **Razor syntax** - `@` expressions, directives, code blocks
-- **C# code** - Server-side logic embedded in Razor
-- **HTML markup** - Static HTML and dynamic content
-- **JavaScript/CSS** - Client-side code within Razor files
+- Place `[WorkItem("url")]` on tests that track a specific issue (GitHub or DevOps URL).
+- Use `TestCode` with `[|...|]` span markers for before/after test scenarios. Access `input.Text` (cleaned) and `input.Span` (marked range).
+- Prefer raw string literals (`"""..."""`) over verbatim strings (`@"..."`).
+- Test end-user scenarios, not implementation details.
+- Verify/helper methods go at the bottom of test files. New test methods go above them.
+- New tooling tests go in `src\Razor\test\Microsoft.VisualStudioCode.RazorExtension.Test` (Cohosting architecture).
+- Integration tests using `AdditionalSyntaxTrees` for tag helper discovery must set `UseTwoPhaseCompilation => true` (see `ComponentDiscoveryIntegrationTest`).
 
-## Development Guidelines
+## Adding OOP Remote Services
 
-### Coding Patterns
+When adding a new `IRemote*Service` and `Remote*Service`:
 
-- Always build and test with `build.sh -test` before submitting PRs, without specifying a project or test filter
-- Write clear, concise, and maintainable code
-- When fixing a bug, look for existing code that already attempts to handle the scenario before adding new code. The bug is more likely in that existing logic than a missing feature.
-- Always place `[WorkItem]` attributes on tests for tracking
-- Prefer immutable collection types and pooled collections where possible
-- Use `using` statements for disposable resources
-- Ensure proper async/await patterns, avoid `Task.Wait()`
-- Use GetRequiredAbsoluteIndex for converting positions to absolute indexes
-- In remote services, the public stub method (calling `RunServiceAsync`) should be placed directly above its private implementation method
+1. Interface → `src\Razor\src\Microsoft.CodeAnalysis.Razor.Workspaces\Remote\`
+2. Implementation → `src\Razor\src\Microsoft.CodeAnalysis.Remote.Razor\`
+3. Register in `RazorServices.cs` (add to `MessagePackServices` or `JsonServices`)
+4. **Add entry to `eng\targets\Services.props`**: `Include="Microsoft.VisualStudio.Razor.{ShortName}"` with `ClassName="{FullTypeName}+Factory"`
+5. Validate: `dotnet test src\Razor\test\Microsoft.CodeAnalysis.Remote.Razor.Test --filter "FullyQualifiedName~RazorServicesTest"`
 
-### Testing Patterns
+## VS Code Validation
 
-- Add appropriate test coverage for new features
-- Prefer `TestCode` over plain strings for before/after test scenarios
-- Prefer raw string literals over verbatim strings
-- Ideally we test the end user scenario, not implementation details
-- Consider cross-platform compatibility by testing path handling and case sensitivity where applicable
-- For tooling, "Cohosting" is the new architecture we're moving towards, so always create tests in the src\Razor\test\Microsoft.VisualStudioCode.RazorExtension.Test project
-- Verify/helper methods go at the bottom of test files. New test methods should always be added above verify methods.
-- Integration tests that add components via `AdditionalSyntaxTrees` and expect them discovered as tag helpers must use `UseTwoPhaseCompilation => true`. `ComponentDiscoveryIntegrationTest` has this; `ComponentDirectiveIntegrationTest` does not.
-
-### Architecture Considerations
-
-- **Performance**: Razor compilation happens on every keystroke - optimize for speed
-- **Cross-platform**: Code should work on Windows, macOS, and Linux
-- **Editor integration**: Consider both Visual Studio and VS Code experiences
-- **Backwards compatibility**: Maintain compatibility with existing Razor syntax
-- Razor documents are stored as **additional documents** in Roslyn. To resolve one from a file path, use `solution.GetDocumentIdsWithFilePath(filePath)` then `solution.GetAdditionalDocument(documentId)`
-- `RazorCodeDocument` is an immutable record-like class. Every `With*` method creates a new instance passing ALL fields through the constructor. When adding a new field, you must thread it through every existing `With*` method.
-- Before writing new utility methods, review existing helpers (e.g., `UsingDirectiveHelper`, `AddUsingsHelper`). Consolidate shared functionality rather than duplicating logic.
-- Prefer computing derived data via extension methods on `RazorCodeDocument` (e.g., `GetUnusedDirectives()`) rather than storing computed results as fields. Store only the source data on the code document.
-- `sourceText.GetTextChange(textEdit)` converts LSP `TextEdit` to Roslyn `TextChange`. The reverse is `sourceText.GetTextEdit(change)`. Both are in `LspExtensions_SourceText.cs`.
-- The codebase pools lists via `ListPool<T>.Default.Get()` and `.Return()`, and uses `PooledArrayBuilder<T>` for building immutable arrays. Follow these patterns rather than allocating new collections.
-
-### Adding OOP (Out-of-Process) Remote Services
-
-When adding a new OOP brokered service (i.e., a new `IRemote*Service` interface and its `Remote*Service` implementation):
-
-1. Add the service interface to `src\Razor\src\Microsoft.CodeAnalysis.Razor.Workspaces\Remote\`
-2. Add the implementation to `src\Razor\src\Microsoft.CodeAnalysis.Remote.Razor\`
-3. Register the service in `RazorServices.cs`
-4. **Add an entry to `eng\targets\Services.props`** — this is required for ServiceHub registration. The `Include` must follow the pattern `Microsoft.VisualStudio.Razor.{ShortName}` and the `ClassName` must be `{FullServiceTypeName}+Factory`.
-5. Run `RazorServicesTest` in `Microsoft.CodeAnalysis.Remote.Razor.Test` to validate the registration is correct: `dotnet test src\Razor\test\Microsoft.CodeAnalysis.Remote.Razor.Test --filter "FullyQualifiedName~RazorServicesTest"`
-
-## Build and Development
-
-### Prerequisites
-- .NET 9.0+ SDK (latest version specified in `global.json`)
-- Visual Studio 2026 (Windows) or VS Code with C# extension (Windows, macOS or Linux)
-- PowerShell (for Windows build scripts)
-
-### Building
-- `./restore.sh` - Restore dependencies
-- `./build.sh` - Full build
-- DO NOT USE `dotnet build` directly
-
-### Testing
-- `./build.sh -test` - Build and run tests
-- DO NOT USE `dotnet test` directly — running it at the repo root will include integration tests (e.g., Playwright-based VS Code tests) that require external dependencies and waste significant time. Use `build.cmd -test` (or `build.sh -test`) instead, or target a specific test project with `dotnet test path/to/Project.csproj`.
-- Never kill dotnet processes by name (e.g., `Stop-Process -Name` or `taskkill /IM`) to get unblocked — other work may be running on the machine.
-
-## VS Code Local Validation
-
-When making changes to Razor tooling for VS Code, you can validate your changes in a real VS Code environment.
-
-For automated validation, run the Playwright-based E2E tests. These tests are an exception to the "DO NOT USE `dotnet test`" rule above, as they require VS Code to be installed and are not run as part of the standard build:
+Run Playwright E2E tests (exception to the "no `dotnet test` at root" rule):
 ```powershell
 cd src\Razor\test\Microsoft.VisualStudioCode.Razor.IntegrationTests
 dotnet test
PATCH

echo "Gold patch applied."
