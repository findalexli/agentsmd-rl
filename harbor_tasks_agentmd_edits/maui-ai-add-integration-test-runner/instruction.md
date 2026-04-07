# Add Integration Test Runner Skill

## Problem

The .NET MAUI integration test infrastructure has two issues:

1. **MSBuild test isolation**: When integration tests run, MSBuild walks up the directory tree from the test output directory and inherits the MAUI repo's `Directory.Build.props` and `Directory.Build.targets` files (which contain Arcade SDK settings). This causes tests to use the repo's `artifacts/` folder for obj/bin output instead of their own local directories, leading to unreliable test behavior.

2. **No standardized test runner**: Contributors run integration tests using raw `dotnet test` commands with manual environment variable setup. There's no automated skill that handles the full workflow (build, pack, install workloads, set env vars, run tests).

## Expected Behavior

1. The `SetUpNuGetPackages` method in `src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs` should create `Directory.Build.props` and `Directory.Build.targets` files in the test directory root. These empty MSBuild project files prevent MSBuild from walking up and inheriting the repo's Arcade SDK settings, ensuring proper test isolation.

2. A new `run-integration-tests` skill should be added to `.github/skills/run-integration-tests/` with:
   - A `SKILL.md` documenting when to use it, available test categories, parameters, and troubleshooting
   - A `scripts/Run-IntegrationTests.ps1` PowerShell script that automates the full workflow: building, packing, installing workloads, setting environment variables, and running tests

3. The project's copilot instructions and integration test instructions should be updated to reference this new skill, directing contributors to ALWAYS use it instead of manual `dotnet test` commands.

## Files to Look At

- `src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs` — test base class where `SetUpNuGetPackages()` needs the isolation fix
- `.github/copilot-instructions.md` — add the new skill to the skills section
- `.github/instructions/integration-tests.instructions.md` — update to reference the new skill
- `.github/skills/run-integration-tests/SKILL.md` — new skill documentation (create directory and file)
- `.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1` — new automation script (create directory and file)
