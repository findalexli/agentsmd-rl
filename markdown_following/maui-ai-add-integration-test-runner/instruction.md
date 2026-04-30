# Add Integration Test Runner Skill

## Problem

The .NET MAUI integration test infrastructure has two issues:

1. **MSBuild test isolation**: When integration tests run, MSBuild walks up the directory tree from the test output directory and inherits the MAUI repo's `Directory.Build.props` and `Directory.Build.targets` files (which contain Arcade SDK settings). This causes tests to use the repo's `artifacts/` folder for obj/bin output instead of their own local directories, leading to unreliable test behavior where test outputs pollute the repo's build artifacts.

2. **No standardized test runner**: Contributors run integration tests using raw `dotnet test` commands with manual environment variable setup. There's no automated skill that handles the full workflow (build, pack, install workloads, set env vars, run tests).

## Expected Behavior

### 1. MSBuild Isolation Fix

The test setup code should create empty MSBuild project files (`Directory.Build.props` and `Directory.Build.targets`) in the test directory root. These files should contain valid XML with a root `<Project>` element and a comment explaining their purpose: stopping MSBuild from walking up the directory tree and inheriting the MAUI repo's settings.

The fix should use `File.WriteAllText` to write these files as triple-quoted raw string literals containing XML with `<Project>` as the root element.

### 2. New `run-integration-tests` Skill

Create a new skill at `.github/skills/run-integration-tests/` with the following files:

**SKILL.md requirements:**
- Must start with YAML frontmatter (`---` at the first line)
- Frontmatter must include `name: run-integration-tests` and a `description:` field
- Must document all test categories: Build, WindowsTemplates, macOSTemplates, Blazor, MultiProject, Samples, AOT, RunOnAndroid, RunOniOS
- Must reference `Run-IntegrationTests.ps1` in the documentation

**Run-IntegrationTests.ps1 requirements:**
- Must start with a comment block (either `#` or `<#` for PowerShell comment syntax)
- Must have a `param()` block with a `[ValidateSet()]` attribute containing the categories: Build, WindowsTemplates, macOSTemplates, Blazor, MultiProject, Samples, AOT, RunOnAndroid, RunOniOS
- Must include these parameter switches: SkipBuild, SkipInstall, AutoProvision
- Must include a `MAUI_PACKAGE_VERSION` parameter for setting the package version
- Must set `$ErrorActionPreference = "Stop"` for error handling
- Must include `[CmdletBinding()]` attribute on the `param()` block
- The script should automate the full workflow: building, packing, setting environment variables, and running tests via `dotnet test`

### 3. Documentation Updates

**.github/copilot-instructions.md:**
- Must have YAML frontmatter at the start (`---` within first 10 characters)
- Must reference skills using the format with numbered list and bold skill names like `**run-integration-tests**`
- Must reference the path `.github/skills/run-integration-tests/SKILL.md`
- Must include the text "ALWAYS use this skill" to direct contributors to use the skill instead of manual `dotnet test` commands
- Must maintain sequential skill numbering after adding the new skill

**.github/instructions/integration-tests.instructions.md:**
- Must contain markdown sections (with `## ` headers)
- Must reference "run-integration-tests" and "Run-IntegrationTests.ps1"
- Must include the text "ALWAYS" to instruct contributors to always use the skill

## Files to Look At

- `src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs` — test base class where test setup logic needs isolation fix
- `.github/copilot-instructions.md` — add the new skill to the skills section
- `.github/instructions/integration-tests.instructions.md` — update to reference the new skill
- `.github/skills/run-integration-tests/SKILL.md` — new skill documentation (create directory and file)
- `.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1` — new automation script (create directory and file)
