#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'run-integration-tests' .github/copilot-instructions.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create directory structure
mkdir -p .github/skills/run-integration-tests/scripts

# Create SKILL.md
cat > .github/skills/run-integration-tests/SKILL.md << 'SKILLEOF'
---
name: run-integration-tests
description: Build, pack, and run .NET MAUI integration tests locally
author: maui-team
version: 1.0.0
---

## Tools Required
- PowerShell 7+
- .NET SDK (version specified in global.json)
- MSBuild
- NuGet

## When to Use
Use this skill when you need to run .NET MAUI integration tests locally, including:
- Running specific test categories (Build, WindowsTemplates, macOSTemplates, etc.)
- Building and packing test dependencies
- Testing templates on different platforms
- Running iOS/Android emulator tests

## Scripts

### Run-IntegrationTests.ps1
Main script for running integration tests with various options.

**Location:** `.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1`

**Parameters:**
- `-Category`: Test category to run (Build, WindowsTemplates, macOSTemplates, Blazor, MultiProject, Samples, AOT, RunOnAndroid, RunOniOS)
- `-SkipBuild`: Skip building and packing (use if already done)
- `-SkipInstall`: Skip installing .NET workloads
- `-AutoProvision`: Automatically provision Xcode on macOS
- `-Configuration`: Build configuration (Debug or Release)
- `-TestFilter`: Custom test filter expression

**Examples:**
\`\`\`powershell
# Run Build category tests
.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category Build

# Run iOS tests
.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category RunOniOS

# Run with custom filter
.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -TestFilter "FullyQualifiedName~MyTest"
\`\`\`

## Common Pitfalls
- Ensure you have the correct .NET SDK version installed
- Some tests require specific platform SDKs (Xcode, Android SDK)
- Template tests may take a long time to run
SKILLEOF

echo "Created SKILL.md"

# Create Run-IntegrationTests.ps1
cat > .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 << 'PS1EOF'
<#
.SYNOPSIS
    Build, pack, and run .NET MAUI integration tests locally.
.DESCRIPTION
    This script handles the full lifecycle of running integration tests:
    1. Optionally builds the Maui.sln and packs required NuGet packages
    2. Sets up the test environment with proper configuration
    3. Runs the specified integration tests with appropriate filters
.PARAMETER Category
    Test category to run. Valid values: Build, WindowsTemplates, macOSTemplates, Blazor, MultiProject, Samples, AOT, RunOnAndroid, RunOniOS
.PARAMETER SkipBuild
    Skip the build and pack step. Useful if you have already built and just want to run tests.
.PARAMETER SkipInstall
    Skip .NET workload installation.
.PARAMETER AutoProvision
    Automatically provision required Xcode version (macOS only).
.PARAMETER Configuration
    Build configuration: Debug or Release (default: Debug).
.PARAMETER TestFilter
    Additional test filter expression to apply.
.PARAMETER MAUI_PACKAGE_VERSION
    Override the MAUI package version to use for testing.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = \$false)]
    [ValidateSet("Build", "WindowsTemplates", "macOSTemplates", "Blazor", "MultiProject", "Samples", "AOT", "RunOnAndroid", "RunOniOS")]
    [string] \$Category,

    [Parameter(Mandatory = \$false)]
    [switch] \$SkipBuild,

    [Parameter(Mandatory = \$false)]
    [switch] \$SkipInstall,

    [Parameter(Mandatory = \$false)]
    [switch] \$SkipXcodeVersionCheck,

    [Parameter(Mandatory = \$false)]
    [switch] \$AutoProvision,

    [Parameter(Mandatory = \$false)]
    [string] \$Configuration = "Debug",

    [Parameter(Mandatory = \$false)]
    [string] \$TestFilter = "",

    [Parameter(Mandatory = \$false)]
    [string] \$MAUI_PACKAGE_VERSION = ""
)

\$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ".NET MAUI Integration Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Display MAUI_PACKAGE_VERSION if set
if (\$MAUI_PACKAGE_VERSION) {
    Write-Host "MAUI_PACKAGE_VERSION: \$MAUI_PACKAGE_VERSION" -ForegroundColor Green
}

# Validate category-specific requirements
if (\$Category -in @("RunOnAndroid", "RunOniOS") -and -not \$SkipBuild) {
    Write-Host "WARNING: Android/iOS tests require build artifacts. Ensure you have run with -Category Build first." -ForegroundColor Yellow
}

# Set up test filter
\$effectiveFilter = ""
if (\$Category) {
    \$effectiveFilter = "Category=\$Category"
}
if (\$TestFilter) {
    if (\$effectiveFilter) {
        \$effectiveFilter = "(\$effectiveFilter) & (\$TestFilter)"
    } else {
        \$effectiveFilter = \$TestFilter
    }
}

Write-Host "Test Filter: \$effectiveFilter" -ForegroundColor Green

# Run tests via dotnet test
Push-Location src/TestUtils/src/Microsoft.Maui.IntegrationTests
try {
    \$testExitCode = 0
    
    if (\$effectiveFilter) {
        dotnet test --filter "\$effectiveFilter" --no-build -c \$Configuration
        \$testExitCode = \$LASTEXITCODE
    } else {
        dotnet test --no-build -c \$Configuration
        \$testExitCode = \$LASTEXITCODE
    }
    
    # Output results summary
    \$resultsPath = "TestResults"
    if (Test-Path \$resultsPath) {
        \$trxFiles = Get-ChildItem -Path \$resultsPath -Filter "*.trx" -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 5
        if (\$trxFiles) {
            Write-Host ""
            Write-Host "Generated TRX Files:" -ForegroundColor Yellow
            foreach (\$trx in \$trxFiles) {
                Write-Host "  - \$(\$trx.FullName)" -ForegroundColor Gray
            }
        }
    }
    
    exit \$testExitCode
}
catch {
    Write-Host ""
    Write-Host "ERROR: \$(\$_.Exception.Message)" -ForegroundColor Red
    Write-Host \$_.ScriptStackTrace -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}
PS1EOF

echo "Created Run-IntegrationTests.ps1"

# Update copilot-instructions.md - add run-integration-tests skill after pr-build-status
cat > /tmp/update_copilot.py << 'PYEOF'
with open('.github/copilot-instructions.md', 'r') as f:
    content = f.read()

# Find pr-build-status (currently #8) and add run-integration-tests after it
old_section = '''8. **pr-build-status** (`.github/skills/pr-build-status/SKILL.md`)
   - **Purpose**: Retrieves Azure DevOps build information for PRs (build IDs, stage status, failed jobs)
   - **Trigger phrases**: "check build for PR #XXXXX", "why did PR build fail", "get build status"
   - **Used by**: When investigating CI failures

#### Internal Skills (Used by Agents)

8. **try-fix**'''

new_section = '''8. **pr-build-status** (`.github/skills/pr-build-status/SKILL.md`)
   - **Purpose**: Retrieves Azure DevOps build information for PRs (build IDs, stage status, failed jobs)
   - **Trigger phrases**: "check build for PR #XXXXX", "why did PR build fail", "get build status"
   - **Used by**: When investigating CI failures

9. **run-integration-tests** (`.github/skills/run-integration-tests/SKILL.md`)
   - **Purpose**: Build, pack, and run .NET MAUI integration tests locally
   - **Trigger phrases**: "run integration tests", "test templates locally", "run macOSTemplates tests", "run RunOniOS tests"
   - **Categories**: Build, WindowsTemplates, macOSTemplates, Blazor, MultiProject, Samples, AOT, RunOnAndroid, RunOniOS
   - **Note**: **ALWAYS use this skill** instead of manual `dotnet test` commands for integration tests

#### Internal Skills (Used by Agents)

10. **try-fix**'''

if old_section in content:
    content = content.replace(old_section, new_section)
    print("Updated copilot-instructions.md - replaced section")
else:
    print("Warning: Could not find exact pattern to replace")
    # Show what we're looking for vs what's there
    if "8. **pr-build-status**" in content:
        print("Found 8. pr-build-status")
    if "8. **try-fix**" in content:
        print("Found 8. try-fix (needs renumbering)")

with open('.github/copilot-instructions.md', 'w') as f:
    f.write(content)
PYEOF
python3 /tmp/update_copilot.py

# Update integration-tests.instructions.md - add skill reference
cat > /tmp/update_integration.py << 'PYEOF'
with open('.github/instructions/integration-tests.instructions.md', 'r') as f:
    content = f.read()

# Add the skill reference at the top after the description
old_text = '''applyTo: "src/TestUtils/src/Microsoft.Maui.IntegrationTests/**/*"
---

# .NET MAUI Integration Tests Guide'''

new_text = '''applyTo: "src/TestUtils/src/Microsoft.Maui.IntegrationTests/**/*"
---

> **ALWAYS use the `run-integration-tests` skill** (via `Run-IntegrationTests.ps1`) instead of manual commands.

# .NET MAUI Integration Tests Guide'''

content = content.replace(old_text, new_text)

# Also add a reference to the skill at the end of the file
skill_ref = '''

## Running Integration Tests

**ALWAYS use the `run-integration-tests` skill** instead of running `dotnet test` directly.

See: `.github/skills/run-integration-tests/SKILL.md` and `.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1`'''

if 'run-integration-tests' not in content:
    content = content + skill_ref

with open('.github/instructions/integration-tests.instructions.md', 'w') as f:
    f.write(content)

print("Updated integration-tests.instructions.md")
PYEOF
python3 /tmp/update_integration.py

# Update BaseBuildTest.cs - add MSBuild isolation files
cat > /tmp/update_basebuild.py << 'PYEOF'
import re

with open('src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs', 'r') as f:
    content = f.read()

# Find the _isSetupComplete = true line and add our code before it
old_code = '''\t\t\t\tFileUtilities.ReplaceInFile(TestNuGetConfig, "NUGET_ONLY_PLACEHOLDER", extraPacksDir);

\t\t\t\t_isSetupComplete = true;'''

new_code = '''\t\t\t\tFileUtilities.ReplaceInFile(TestNuGetConfig, "NUGET_ONLY_PLACEHOLDER", extraPacksDir);

\t\t\t\t// Create a Directory.Build.props in the test directory root to prevent MSBuild from
\t\t\t\t// walking up and inheriting the MAUI repo's Arcade SDK settings. This ensures test
\t\t\t\t// projects use their own local obj/bin folders instead of the repo's artifacts folder.
\t\t\t\tvar testDirBuildProps = Path.Combine(TestEnvironment.GetTestDirectoryRoot(), "Directory.Build.props");
\t\t\t\tif (!File.Exists(testDirBuildProps))
\t\t\t\t{
\t\t\t\t\tFile.WriteAllText(testDirBuildProps, """
\t\t\t\t\t\t<Project>
\t\t\t\t\t\t  <!-- This file stops MSBuild from walking up the directory tree and inheriting
\t\t\t\t\t\t       the MAUI repo's Directory.Build.props and Arcade SDK settings.
\t\t\t\t\t\t       This ensures test projects use their own local obj/bin folders. -->
\t\t\t\t\t\t</Project>
\t\t\t\t\t\t""");
\t\t\t\t}

\t\t\t\t// Also create Directory.Build.targets to prevent target inheritance
\t\t\t\tvar testDirBuildTargets = Path.Combine(TestEnvironment.GetTestDirectoryRoot(), "Directory.Build.targets");
\t\t\t\tif (!File.Exists(testDirBuildTargets))
\t\t\t\t{
\t\t\t\t\tFile.WriteAllText(testDirBuildTargets, """
\t\t\t\t\t\t<Project>
\t\t\t\t\t\t  <!-- This file stops MSBuild from walking up the directory tree and inheriting
\t\t\t\t\t\t       the MAUI repo's Directory.Build.targets. -->
\t\t\t\t\t\t</Project>
\t\t\t\t\t\t""");
\t\t\t\t}

\t\t\t\t_isSetupComplete = true;'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("Updated BaseBuildTest.cs")
else:
    print("Warning: Could not find pattern to replace in BaseBuildTest.cs")

with open('src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs', 'w') as f:
    f.write(content)
PYEOF
python3 /tmp/update_basebuild.py

# Configure git and commit
git config user.email "agent@test"
git config user.name "Agent"
git add -A
git commit -m "Add run-integration-tests skill" --quiet || true

echo "Patch applied successfully."
