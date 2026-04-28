#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mudblazor

# Idempotency guard
if grep -qF "8. **Forgetting to run `dotnet format`** - MUST run `dotnet format src/MudBlazor" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -17,9 +17,9 @@ The project follows Material Design guidelines and provides a complete set of UI
 - Check your version: `dotnet --version`
 - The solution targets .NET 8.0, .NET 9.0, and .NET 10.0
 
-## Dev Environment Tips
+## Core Commands and Timings
 
-### Build Commands (CRITICAL TIMINGS)
+### Build and Test (CRITICAL TIMINGS)
 
 **ALWAYS follow this exact sequence:**
 
@@ -28,20 +28,15 @@ The project follows Material Design guidelines and provides a complete set of UI
 dotnet clean src/MudBlazor.slnx
 ```
 - Runs in ~2-3 seconds
-- Use when: Build failures occur, switching branches, or unexplained issues
+- Use when: Build failures occur or unexplained issues
 - No warnings or errors expected
 
 2. **Build:**
 ```bash
 dotnet build src/MudBlazor.slnx -c Release --nologo
 ```
 - **Duration: ~2-2.5 minutes** (this is NORMAL - do NOT timeout before 150 seconds)
-- Builds 15+ projects including:
-  - MudBlazor (core library) - targets net8.0 and net9.0
-  - MudBlazor.Docs.Compiler - generates 745+ documentation files
-  - MudBlazor.UnitTests.Docs.Generator - generates test files
-  - Multiple doc hosting projects (Server, Wasm, WasmHost)
-  - Analyzers, source generators, and test projects
+- Builds 15+ projects including docs and source generators
 - Expected output: "Build succeeded" with 0 warnings, 0 errors
 - JavaScript files are compiled: wwwroot/MudBlazor.min.js
 - SCSS is compiled to CSS automatically
@@ -55,7 +50,14 @@ dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Rel
 - Runs 3,734+ tests (some skipped performance tests)
 - Expected output: "Passed! - Failed: 0, Passed: 3734, Skipped: 10"
 - **ALWAYS use `--no-build`** to avoid rebuilding (saves time)
-- Tests must pass before submitting PRs
+
+### Formatting (REQUIRED)
+
+```bash
+dotnet format src/MudBlazor.slnx
+```
+- MUST run before finalizing changes
+- CI will fail if code is not properly formatted
 
 ### Running Docs Locally
 
@@ -65,7 +67,17 @@ dotnet run --project src/MudBlazor.Docs.Server/MudBlazor.Docs.Server.csproj
 - Launches at https://localhost:5001 (or http://localhost:5000)
 - Best for debugging visual changes and testing components interactively
 
-### Build Troubleshooting
+### Other Commands
+
+```bash
+# Run test viewer (for visual debugging of tests)
+dotnet run --project src/MudBlazor.UnitTests.Viewer/MudBlazor.UnitTests.Viewer.csproj
+
+# Pack for local testing
+dotnet pack src/MudBlazor/MudBlazor.csproj -c Release -o ./LocalNuGet -p:Version=8.0.0-custom
+```
+
+### Troubleshooting
 
 **If build fails:**
 1. Run `dotnet clean src/MudBlazor.slnx` first
@@ -81,8 +93,7 @@ dotnet run --project src/MudBlazor.Docs.Server/MudBlazor.Docs.Server.csproj
 
 **If CI formatting check fails:**
 1. Run `dotnet format src/MudBlazor.slnx` to auto-fix formatting issues
-2. Commit the formatting changes
-3. Common issues: blank lines after attributes, missing UTF-8 BOM, incorrect indentation
+2. Common issues: blank lines after attributes, missing UTF-8 BOM, incorrect indentation
 
 ## Project Structure
 
@@ -132,7 +143,7 @@ src/
 ```
 
 ### Important Configuration Files
-- **src/.editorconfig** - C# code style rules (Microsoft Roslyn defaults with MudBlazor team overrides)
+- **src/.editorconfig** - C# code style rules (Roslyn defaults + MudBlazor team overrides)
   - Instance fields: `_camelCase` with underscore prefix
   - File header template required (copyright notice)
   - CS4014 (unawaited async) set to ERROR
@@ -144,14 +155,10 @@ src/
 ## Testing Instructions
 
 ### Running Tests
+- Build first is required; use the Build and Test sequence above.
+- Always use `--no-build` for tests after a successful build.
+- Run a specific test:
 ```bash
-# Build first (required)
-dotnet build src/MudBlazor.slnx -c Release --nologo
-
-# Run all unit tests (ALWAYS use --no-build to save time)
-dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Release --nologo
-
-# Run specific test
 dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --filter "TestName" --no-build -c Release
 ```
 
@@ -161,15 +168,15 @@ dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --filter "TestNam
 1. **Never save HTML elements from `Find()` or `FindAll()` in variables** - they become stale after interaction
 2. **Always use `InvokeAsync()` when setting component parameters or calling methods**
 
-**✅ GOOD Example:**
+**GOOD example:**
 ```csharp
 var comp = ctx.RenderComponent<MudTextField<string>>();
 comp.Find("input").Change("Garfield");  // Query each time
 comp.Find("input").Blur();
 comp.FindComponent<MudTextField<string>>().Instance.Value.Should().NotBeNullOrEmpty();
 ```
 
-**❌ BAD Example:**
+**BAD example:**
 ```csharp
 var textField = comp.Find("input");  // DON'T DO THIS
 textField.Change("Garfield");
@@ -180,13 +187,13 @@ textField.Blur();  // Will fail - element is stale
 
 ### Using InvokeAsync
 
-**❌ BAD:**
+**BAD:**
 ```csharp
 var textField = comp.FindComponent<MudTextField<string>>().Instance;
 textField.Value = "Garfield"; // WRONG - not on UI thread
 ```
 
-**✅ GOOD:**
+**GOOD:**
 ```csharp
 var textField = comp.FindComponent<MudTextField<string>>().Instance;
 await comp.InvokeAsync(() => textField.Value = "Garfield");
@@ -210,7 +217,7 @@ await comp.InvokeAsync(() => textField.Value = "Garfield");
 
 **NEVER put logic in parameter getters/setters!** Use the ParameterState framework instead. This prevents unobserved async discards and update loops.
 
-**❌ BAD (FORBIDDEN):**
+**BAD (FORBIDDEN):**
 ```csharp
 private bool _expanded;
 
@@ -228,7 +235,7 @@ public bool Expanded
 }
 ```
 
-**✅ GOOD (REQUIRED):**
+**GOOD (REQUIRED):**
 ```csharp
 private readonly ParameterState<bool> _expandedState;
 
@@ -258,7 +265,7 @@ private async Task OnExpandedChangedAsync()
 
 ### Never Overwrite Parameters
 
-**❌ BAD:**
+**BAD:**
 ```csharp
 private Task ToggleAsync()
 {
@@ -267,7 +274,7 @@ private Task ToggleAsync()
 }
 ```
 
-**✅ GOOD:**
+**GOOD:**
 ```csharp
 private Task ToggleAsync()
 {
@@ -277,7 +284,7 @@ private Task ToggleAsync()
 
 ### Never Set External Component Parameters (BL0005 Warning)
 
-**❌ BAD:**
+**BAD:**
 ```razor
 <CalendarComponent @ref="@_calendarRef" />
 @code {
@@ -289,7 +296,7 @@ private Task ToggleAsync()
 }
 ```
 
-**✅ GOOD:**
+**GOOD:**
 ```razor
 <CalendarComponent ShowOnlyOneCalendar="@_showOnlyOne" />
 @code {
@@ -320,98 +327,44 @@ private Task ToggleAsync()
 
 ### Title Format
 ```
-<component name>: <short description in imperative> (<linked issue>)
+<component name>: <short description in imperative>
 ```
-Example: `DateRangePicker: Fix initializing DateRange with null values (#1997)`
+Example: `DateRangePicker: Fix initializing DateRange with null values`
 
-### PR Requirements
-- Single topic per PR (one feature/bug fix)
-- Target the `dev` branch
-- All tests must pass
-- Include unit tests for logic changes
-- No unnecessary refactoring
-- Link related issues using `Fixes #<issue>` (bugs) or `Closes #<issue>` (features)
-- Include screenshots/videos for visual changes
-- Code must be properly formatted per .editorconfig
+## Workflow Checkpoints (REQUIRED)
 
-### Branch Management
-- Use descriptive branches: `feature/my-new-feature` or `fix/my-bug-fix`
-- Keep branches up to date by merging `dev` (don't rebase)
-- Use draft PRs for work in progress
+### Before Starting Work
+- Always check initial state by running the Build and Test sequence (skip Clean unless needed).
 
-## Build and Validation Workflow
+### After Changes
+1. Clean if needed (use the Clean command above)
+2. Format code (REQUIRED - MUST run before finalizing changes)
+3. Run the Build and Test sequence
+4. (Optional) Run docs locally with the Docs Server command above
 
-### Development Workflow by Task Type
+## Development Workflow by Task Type
 
 **For Component Changes:**
 1. Locate files:
    - Component code: `src/MudBlazor/Components/<ComponentName>/`
    - Component styles: `src/MudBlazor/Styles/components/_<componentname>.scss`
    - Component tests: `src/MudBlazor.UnitTests/Components/<ComponentName>Tests.cs`
    - Test components: `src/MudBlazor.UnitTests.Viewer/TestComponents/<ComponentName>/`
-
 2. Make your changes (follow ParameterState pattern)
-
-3. Build and test iteratively:
-```bash
-dotnet build src/MudBlazor.slnx -c Release --nologo
-dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Release --nologo
-```
-
-4. Before committing:
-```bash
-# Format code (REQUIRED)
-dotnet format src/MudBlazor.slnx
-```
-
-5. Trigger copilot code review and address all issues (REQUIRED for code changes)
-
-6. Run docs locally to verify (optional):
-```bash
-dotnet run --project src/MudBlazor.Docs.Server/MudBlazor.Docs.Server.csproj
-```
+3. Build and test iteratively using the Build and Test sequence
+4. Before finalizing, run `dotnet format src/MudBlazor.slnx` (REQUIRED)
+5. Run docs locally to verify (optional)
 
 **For Documentation Changes:**
 1. Edit in `src/MudBlazor.Docs/Pages/Components/<ComponentName>.razor`
-2. Build to generate files (runs MudBlazor.Docs.Compiler):
-```bash
-dotnet build src/MudBlazor.slnx -c Release --nologo
-```
+2. Run the Build command to generate files (MudBlazor.Docs.Compiler)
 3. Preview locally with docs server
 
 **For Test Changes:**
 1. Create test component in `src/MudBlazor.UnitTests.Viewer/TestComponents/<ComponentName>/`
 2. Write bUnit test in `src/MudBlazor.UnitTests/Components/<ComponentName>Tests.cs`
-3. Build and run tests
-4. Debug visually if needed:
-```bash
-dotnet run --project src/MudBlazor.UnitTests.Viewer/MudBlazor.UnitTests.Viewer.csproj
-```
-
-### Before Making Changes
-```bash
-# Always check initial state
-dotnet build src/MudBlazor.slnx -c Release --nologo
-dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Release --nologo
-```
-
-### After Making Changes
-```bash
-# Clean if needed (switching branches or unexplained issues)
-dotnet clean src/MudBlazor.slnx
-
-# Format code (REQUIRED - MUST run before committing)
-dotnet format src/MudBlazor.slnx
-
-# Build
-dotnet build src/MudBlazor.slnx -c Release --nologo
-
-# Run tests
-dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Release --nologo
-```
-
-**If you made code changes (not just documentation):**
-- MUST trigger a copilot code review and address all issues before finalizing the PR
+3. Build and run tests using the Build and Test sequence
+4. Debug visually if needed with the test viewer command
 
 ## Code Style Highlights
 
@@ -457,13 +410,10 @@ dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Rel
 2. **Stale HTML element references in tests** - Always re-query with `Find()` instead of saving elements
 3. **Direct parameter assignment on component refs** - Use declarative binding (BL0005 warning)
 4. **Missing `InvokeAsync` in tests** - Required for parameter changes in bUnit tests
-5. **Breaking existing tests** - Run full test suite before submitting PR
-6. **Targeting wrong branch** - Always target `dev`, not `master`
-7. **Multiple topics in one PR** - Keep PRs focused on single issue
-8. **Build timeouts** - Set timeout to at least 180 seconds for builds, 120 seconds for tests
-9. **Missing `--no-build` flag** - Always use when running tests after a successful build
-10. **Forgetting to run `dotnet format`** - MUST run `dotnet format src/MudBlazor.slnx` before committing
-11. **Skipping code review** - MUST trigger copilot code review for any code changes and address all issues
+5. **Breaking existing tests** - Run full test suite before finalizing changes
+6. **Build timeouts** - Set timeout to at least 180 seconds for builds, 120 seconds for tests
+7. **Missing `--no-build` flag** - Always use when running tests after a successful build
+8. **Forgetting to run `dotnet format`** - MUST run `dotnet format src/MudBlazor.slnx` before finalizing changes
 
 ## Continuous Integration
 
@@ -475,73 +425,4 @@ The GitHub Actions workflow (`.github/workflows/build-test-mudblazor.yml`) runs:
 5. **Code Quality** - SonarCloud analysis
 6. **Security Scanning** - Dependency checks
 
-**All checks must pass before merging.**
-
-## Additional Resources
-
-- **CONTRIBUTING.md** - Detailed contribution guidelines
-- **README.md** - Quick start and installation
-- **Documentation Site** - https://mudblazor.com
-- **Discord** - https://discord.gg/mudblazor
-
-## Quick Reference
-
-```bash
-# Check .NET version
-dotnet --version  # Should be 10.0.100 or later
-
-# Full build and test cycle
-dotnet clean src/MudBlazor.slnx
-dotnet build src/MudBlazor.slnx -c Release --nologo  # ~2 minutes
-dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Release --nologo  # ~1.5 minutes
-
-# Test specific component
-dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --filter "ButtonTests" --no-build -c Release
-
-# Run docs locally (server mode - best for debugging)
-dotnet run --project src/MudBlazor.Docs.Server/MudBlazor.Docs.Server.csproj
-
-# Run test viewer (for visual debugging of tests)
-dotnet run --project src/MudBlazor.UnitTests.Viewer/MudBlazor.UnitTests.Viewer.csproj
-
-# Pack for local testing
-dotnet pack src/MudBlazor/MudBlazor.csproj -c Release -o ./LocalNuGet -p:Version=8.0.0-custom
-```
-
-## Validation Steps Before PR
-
-**ALWAYS run this sequence before creating/updating a PR:**
-
-```bash
-# 1. Clean (if switching branches or weird issues)
-dotnet clean src/MudBlazor.slnx
-
-# 2. Format code (REQUIRED - MUST run before committing ANY changes)
-dotnet format src/MudBlazor.slnx
-# This MUST be run to ensure code formatting is correct
-# CI will fail if code is not properly formatted
-
-# 3. Build
-dotnet build src/MudBlazor.slnx -c Release --nologo
-# Expected: "Build succeeded" with 0 warnings, 0 errors in ~2 minutes
-
-# 4. Test
-dotnet test src/MudBlazor.UnitTests/MudBlazor.UnitTests.csproj --no-build -c Release --nologo
-# Expected: "Passed! - Failed: 0, Passed: 3734+, Skipped: 10" in ~1.5 minutes
-
-# 5. (Optional) Test docs locally
-dotnet run --project src/MudBlazor.Docs.Server/MudBlazor.Docs.Server.csproj
-```
-
-### Code Review Requirement
-
-**CRITICAL: If you made ANY code changes (not just documentation), you MUST:**
-1. Trigger a copilot code review before finalizing the PR
-2. Address all issues identified in the code review
-3. Re-run the code review if significant changes were made after the initial review
-
-**Documentation-only changes do not require a code review.**
-
----
-
-When in doubt, check the existing code patterns, follow the guidelines in CONTRIBUTING.md, and ask questions on Discord before implementing.
+**Keep changes compatible with all checks.**
PATCH

echo "Gold patch applied."
