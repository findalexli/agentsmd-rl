#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'run-integration-tests' .github/copilot-instructions.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
index 604d89989798..91dc349110c8 100644
--- a/.github/copilot-instructions.md
+++ b/.github/copilot-instructions.md
@@ -265,9 +265,15 @@ Skills are modular capabilities that can be invoked directly or used by agents.
    - **Trigger phrases**: "check build for PR #XXXXX", "why did PR build fail", "get build status"
    - **Used by**: When investigating CI failures

+8. **run-integration-tests** (`.github/skills/run-integration-tests/SKILL.md`)
+   - **Purpose**: Build, pack, and run .NET MAUI integration tests locally
+   - **Trigger phrases**: "run integration tests", "test templates locally", "run macOSTemplates tests", "run RunOniOS tests"
+   - **Categories**: Build, WindowsTemplates, macOSTemplates, Blazor, MultiProject, Samples, AOT, RunOnAndroid, RunOniOS
+   - **Note**: **ALWAYS use this skill** instead of manual `dotnet test` commands for integration tests
+
 #### Internal Skills (Used by Agents)

-8. **try-fix** (`.github/skills/try-fix/SKILL.md`)
+9. **try-fix** (`.github/skills/try-fix/SKILL.md`)
    - **Purpose**: Proposes ONE independent fix approach, applies it, tests, records result with failure analysis, then reverts
    - **Used by**: pr agent Phase 3 (Fix phase) - rarely invoked directly by users
    - **Behavior**: Reads prior attempts to learn from failures. Max 5 attempts per session.
diff --git a/.github/instructions/integration-tests.instructions.md b/.github/instructions/integration-tests.instructions.md
index 89b3009cc6cc..672a0294f2ca 100644
--- a/.github/instructions/integration-tests.instructions.md
+++ b/.github/instructions/integration-tests.instructions.md
@@ -147,13 +147,57 @@ if (!TestEnvironment.IsWindows)

 ## Running Tests Locally

-### Prerequisites
+### 🚨 ALWAYS Use the Skill

-1. Verify `.dotnet/` folder exists (local SDK). If missing, stop and tell user to run `dotnet cake` to provision locally.
-2. Set `MAUI_PACKAGE_VERSION` environment variable. If missing, tests will fail with "MAUI_PACKAGE_VERSION was not set."
-   - Example: `export MAUI_PACKAGE_VERSION=$(ls .dotnet/packs/Microsoft.Maui.Sdk | head -1)`
+**When asked to run integration tests, ALWAYS use the `run-integration-tests` skill:**

-### Environment Variables
+```powershell
+# macOS examples
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "macOSTemplates" -SkipBuild -SkipInstall -SkipXcodeVersionCheck
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "RunOniOS" -SkipBuild -SkipInstall -SkipXcodeVersionCheck
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "RunOnAndroid" -SkipBuild -SkipInstall
+
+# Windows examples
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "WindowsTemplates" -SkipBuild -SkipInstall
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "Build" -SkipBuild -SkipInstall
+```
+
+The skill handles:
+- ✅ Environment variable setup (`MAUI_PACKAGE_VERSION`, `SKIP_XCODE_VERSION_CHECK`)
+- ✅ Cross-platform support (Windows and macOS)
+- ✅ Test results in TRX format
+- ✅ Proper error reporting
+
+See `.github/skills/run-integration-tests/SKILL.md` for full documentation.
+
+---
+
+### Prerequisites (Manual Setup)
+
+If the skill reports missing prerequisites, provision the local SDK:
+
+1. **Provision the local SDK and workloads** - The `.dotnet/` folder must contain a fully provisioned .NET SDK with MAUI workloads. Run:
+
+   ```bash
+   # Step 1: Download the .NET SDK (creates .dotnet/dotnet binary)
+   ./build.sh --target=dotnet
+
+   # Step 2: Install MAUI workloads into the local SDK (takes ~5 minutes)
+   ./build.sh --target=dotnet-local-workloads
+   ```
+
+   **Verification**: After provisioning, verify the setup:
+   ```bash
+   # Check dotnet binary exists
+   ls .dotnet/dotnet
+
+   # Check MAUI workloads are installed
+   ls .dotnet/packs/Microsoft.Maui.Sdk
+   ```
+
+### Environment Variables (Reference)
+
+The skill sets these automatically, but for manual runs:

 | Variable | Required | Purpose |
 |----------|----------|---------|
@@ -161,9 +205,15 @@ if (!TestEnvironment.IsWindows)
 | `IOS_TEST_DEVICE` | No | iOS simulator target (e.g., `ios-simulator-64_18.5`) |
 | `SKIP_XCODE_VERSION_CHECK` | No | Set to `true` to bypass Xcode version validation |

-### Run Commands
+### Manual Run Commands (Fallback Only)
+
+**⚠️ Only use these if the skill is unavailable:**

 ```bash
+# Set environment first
+export MAUI_PACKAGE_VERSION=$(ls .dotnet/packs/Microsoft.Maui.Sdk | head -1)
+export SKIP_XCODE_VERSION_CHECK=true
+
 # Run specific category
 dotnet test src/TestUtils/src/Microsoft.Maui.IntegrationTests \
   --filter "Category=Build"
@@ -171,11 +221,6 @@ dotnet test src/TestUtils/src/Microsoft.Maui.IntegrationTests \
 # Run specific test
 dotnet test src/TestUtils/src/Microsoft.Maui.IntegrationTests \
   --filter "FullyQualifiedName~AppleTemplateTests.RunOniOS"
-
-# With iOS device and Xcode skip
-export IOS_TEST_DEVICE="ios-simulator-64_18.5"
-export SKIP_XCODE_VERSION_CHECK=true
-dotnet test ... --filter "Category=RunOniOS"
 ```

 ## Common Pitfalls
diff --git a/.github/skills/run-integration-tests/SKILL.md b/.github/skills/run-integration-tests/SKILL.md
new file mode 100644
index 000000000000..4cce1fd5da5d
--- /dev/null
+++ b/.github/skills/run-integration-tests/SKILL.md
@@ -0,0 +1,199 @@
+---
+name: run-integration-tests
+description: "Build, pack, and run .NET MAUI integration tests locally. Validates templates, samples, and end-to-end scenarios using the local workload."
+metadata:
+  author: dotnet-maui
+  version: "1.0"
+compatibility: Requires Windows for WindowsTemplates category. macOS for macOSTemplates, RunOniOS, RunOnAndroid.
+---
+
+# Run Integration Tests Skill
+
+Build the MAUI product, install local workloads, and run integration tests.
+
+## When to Use
+
+- User asks to "run integration tests"
+- User asks to "test templates locally"
+- User asks to "validate MAUI build with templates"
+- User wants to verify changes don't break template scenarios
+- User asks to run specific test categories (WindowsTemplates, Samples, Build, Blazor, etc.)
+
+## Available Test Categories
+
+| Category | Platform | Description |
+|----------|----------|-------------|
+| `Build` | All | Basic template build tests |
+| `WindowsTemplates` | Windows | Windows-specific template scenarios |
+| `macOSTemplates` | macOS | macOS-specific scenarios |
+| `Blazor` | All | Blazor hybrid templates |
+| `MultiProject` | All | Multi-project templates |
+| `Samples` | All | Sample project builds |
+| `AOT` | macOS | Native AOT compilation |
+| `RunOnAndroid` | macOS | Build, install, run on Android emulator |
+| `RunOniOS` | macOS | iOS simulator tests |
+
+## Scripts
+
+All scripts are in `.github/skills/run-integration-tests/scripts/`
+
+### Run Integration Tests (Full Workflow)
+
+```powershell
+# Run with specific category
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "WindowsTemplates"
+
+# Run with Release configuration
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "Samples" -Configuration "Release"
+
+# Run with custom test filter
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -TestFilter "FullyQualifiedName~BuildSample"
+
+# Skip build step (if already built)
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "Build" -SkipBuild
+
+# macOS: Skip Xcode version check (for version mismatches)
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "macOSTemplates" -SkipBuild -SkipInstall -SkipXcodeVersionCheck
+
+# Auto-provision SDK if not found (first-time setup)
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "Build" -AutoProvision
+```
+
+## Parameters
+
+| Parameter | Required | Default | Description |
+|-----------|----------|---------|-------------|
+| `-Category` | No | - | Test category to run (WindowsTemplates, Samples, Build, etc.) |
+| `-TestFilter` | No | - | Custom NUnit test filter expression |
+| `-Configuration` | No | Debug | Build configuration (Debug/Release) |
+| `-SkipBuild` | No | false | Skip build/pack step if already done |
+| `-SkipInstall` | No | false | Skip workload installation if already done |
+| `-SkipXcodeVersionCheck` | No | false | Skip Xcode version validation (macOS) |
+| `-AutoProvision` | No | false | Automatically provision local SDK if not found |
+| `-ResultsDirectory` | No | artifacts/integration-tests | Directory for test results |
+
+## Workflow Steps
+
+The script performs these steps:
+
+1. **Build & Pack**: `.\build.cmd -restore -pack -configuration $Configuration`
+2. **Install Workloads**: `.dotnet\dotnet build .\src\DotNet\DotNet.csproj -t:Install -c $Configuration`
+3. **Extract Version**: Reads MAUI_PACKAGE_VERSION from installed packs
+4. **Run Tests**: `.dotnet\dotnet test ... -filter "Category=$Category"`
+
+## Example Usage
+
+```powershell
+# Run WindowsTemplates tests
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "WindowsTemplates"
+
+# Run Samples tests
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "Samples"
+
+# Run multiple categories
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -TestFilter "Category=Build|Category=Blazor"
+```
+
+## Prerequisites
+
+- Windows for WindowsTemplates, macOS for macOSTemplates/RunOniOS/RunOnAndroid
+- .NET SDK (version from global.json)
+- Sufficient disk space for build artifacts
+- Local SDK and workloads must be provisioned first
+
+### Provisioning the Local SDK (Required First Time)
+
+Before running integration tests, you must provision the local .NET SDK and MAUI workloads:
+
+```bash
+# Step 1: Restore dotnet tools
+dotnet tool restore
+
+# Step 2: Provision local SDK and install workloads (~5 minutes)
+dotnet cake --target=dotnet
+
+# Step 3: Install MAUI local workloads
+dotnet cake --target=dotnet-local-workloads
+```
+
+**Verification:**
+```bash
+# Check SDK exists
+ls .dotnet/dotnet
+
+# Check MAUI SDK version
+ls .dotnet/packs/Microsoft.Maui.Sdk
+```
+
+> **Note:** The old `./build.sh --target=dotnet` syntax no longer works. Use `dotnet cake` directly.
+
+## Output
+
+- Test results in TRX format at `<ResultsDirectory>/`
+- Build logs in `artifacts/` directory
+- Console output with test pass/fail summary
+
+## Troubleshooting
+
+| Issue | Solution |
+|-------|----------|
+| "MAUI_PACKAGE_VERSION was not set" | Ensure build step completed successfully |
+| "Local .dotnet SDK not found" | Run `dotnet tool restore && dotnet cake --target=dotnet && dotnet cake --target=dotnet-local-workloads` |
+| Template not found | Workload installation may have failed |
+| Build failures | Check `artifacts/log/` for detailed build logs |
+| "Cannot proceed with locked .dotnet folder" | Kill processes using `.dotnet`: `Get-Process | Where-Object { $_.Path -like "*\.dotnet\*" } | ForEach-Object { Stop-Process -Id $_.Id -Force }` |
+| Session times out / becomes invalid | Integration tests are long-running (15-60+ min). Run manually in a terminal window instead of via Copilot CLI |
+| Tests take too long | Start with `Build` category (fastest), then run others. Use `-SkipBuild -SkipInstall` if workloads are already installed |
+| iOS tests fail with "mlaunch exited with 1" | Simulator state issue. Run individual tests instead of the whole category (see below) |
+| iOS simulator state errors (code 137/149) | Reset simulator: `xcrun simctl shutdown all && xcrun simctl erase all` or run tests individually |
+
+## Running Manually (Recommended for Long-Running Tests)
+
+Integration tests can take 15-60+ minutes depending on the category. For best results, run directly in a terminal:
+
+```powershell
+cd D:\repos\dotnet\maui
+
+# Option 1: Use the skill script
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category "Build" -SkipBuild -SkipInstall
+
+# Option 2: Run dotnet test directly (if workloads already installed)
+$env:MAUI_PACKAGE_VERSION = (Get-ChildItem .dotnet\packs\Microsoft.Maui.Sdk -Directory | Sort-Object Name -Descending | Select-Object -First 1).Name
+.dotnet\dotnet test src\TestUtils\src\Microsoft.Maui.IntegrationTests --filter "Category=Build"
+```
+
+### Running All Categories Sequentially
+
+```powershell
+# Windows categories (run on Windows)
+$categories = @("Build", "WindowsTemplates", "Blazor", "MultiProject", "Samples")
+foreach ($cat in $categories) {
+    Write-Host "Running $cat..." -ForegroundColor Cyan
+    pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -Category $cat -SkipBuild -SkipInstall
+}
+```
+
+### Running Individual iOS Tests (Recommended)
+
+Running all iOS tests together (`-Category "RunOniOS"`) can cause simulator state issues. For better reliability, run tests individually:
+
+```powershell
+# Available iOS tests
+$iosTests = @(
+    "RunOniOS_MauiDebug",
+    "RunOniOS_MauiRelease",
+    "RunOniOS_MauiReleaseTrimFull",
+    "RunOniOS_BlazorDebug",
+    "RunOniOS_BlazorRelease",
+    "RunOniOS_MauiNativeAOT"
+)
+
+# Run a specific iOS test
+pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -TestFilter "FullyQualifiedName~RunOniOS_MauiDebug" -SkipBuild -SkipInstall -SkipXcodeVersionCheck
+
+# Run all iOS tests individually (more reliable than running category)
+foreach ($test in $iosTests) {
+    Write-Host "Running $test..." -ForegroundColor Cyan
+    pwsh .github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 -TestFilter "FullyQualifiedName~$test" -SkipBuild -SkipInstall -SkipXcodeVersionCheck
+}
+```
diff --git a/.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1 b/.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1
new file mode 100644
index 000000000000..db28fe90b3e4
--- /dev/null
+++ b/.github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1
@@ -0,0 +1,358 @@
+<#
+.SYNOPSIS
+    Build, pack, and run .NET MAUI integration tests locally.
+
+.DESCRIPTION
+    This script automates the full workflow for running integration tests:
+    1. Build and pack the MAUI product
+    2. Install the generated MAUI workloads locally
+    3. Extract and set MAUI_PACKAGE_VERSION
+    4. Run integration tests with specified filter
+
+.PARAMETER Category
+    Test category to run (WindowsTemplates, Samples, Build, Blazor, MultiProject, etc.)
+
+.PARAMETER TestFilter
+    Custom NUnit test filter expression. Overrides -Category if specified.
+
+.PARAMETER Configuration
+    Build configuration (Debug or Release). Default: Debug
+
+.PARAMETER SkipBuild
+    Skip the build and pack step (useful if already built)
+
+.PARAMETER ResultsDirectory
+    Directory for test results. Default: artifacts/integration-tests
+
+.EXAMPLE
+    .\Run-IntegrationTests.ps1 -Category "WindowsTemplates"
+
+.EXAMPLE
+    .\Run-IntegrationTests.ps1 -Category "Samples" -Configuration "Release"
+
+.EXAMPLE
+    .\Run-IntegrationTests.ps1 -TestFilter "FullyQualifiedName~BuildSample" -SkipBuild
+#>
+
+param(
+    [Parameter()]
+    [ValidateSet("Build", "WindowsTemplates", "macOSTemplates", "Blazor", "MultiProject", "Samples", "AOT", "RunOnAndroid", "RunOniOS")]
+    [string]$Category,
+
+    [Parameter()]
+    [string]$TestFilter,
+
+    [Parameter()]
+    [ValidateSet("Debug", "Release")]
+    [string]$Configuration = "Debug",
+
+    [Parameter()]
+    [switch]$SkipBuild,
+
+    [Parameter()]
+    [switch]$SkipInstall,
+
+    [Parameter()]
+    [switch]$SkipXcodeVersionCheck,
+
+    [Parameter()]
+    [switch]$AutoProvision,
+
+    [Parameter()]
+    [string]$ResultsDirectory = "artifacts/integration-tests"
+)
+
+$ErrorActionPreference = "Stop"
+$RepoRoot = (Get-Item $PSScriptRoot).Parent.Parent.Parent.Parent.FullName
+$RunningOnWindows = $IsWindows -or $env:OS -eq 'Windows_NT'
+$RunningOnMacOS = $IsMacOS -or ((Get-Command uname -ErrorAction SilentlyContinue) -and ((uname) -eq 'Darwin'))
+
+Write-Host "======================================================================" -ForegroundColor Cyan
+Write-Host "       .NET MAUI Integration Tests Runner                            " -ForegroundColor Cyan
+Write-Host "======================================================================" -ForegroundColor Cyan
+Write-Host ""
+Write-Host "Repository Root: $RepoRoot"
+Write-Host "Platform:        $(if ($RunningOnWindows) { 'Windows' } elseif ($RunningOnMacOS) { 'macOS' } else { 'Linux' })"
+Write-Host "Configuration:   $Configuration"
+Write-Host "Category:        $(if ($Category) { $Category } else { 'Custom filter' })"
+Write-Host "Skip Build:      $SkipBuild"
+Write-Host ""
+
+Push-Location $RepoRoot
+
+try {
+    # ======================================================================
+    # Pre-flight: Check for processes using .dotnet folder (Windows only)
+    # ======================================================================
+    $dotnetFolder = Join-Path $RepoRoot ".dotnet"
+
+    if ($RunningOnWindows) {
+        $lockingProcesses = Get-Process | Where-Object { $_.Path -like "$dotnetFolder\*" } -ErrorAction SilentlyContinue
+
+        if ($lockingProcesses) {
+            Write-Host "========================================================================" -ForegroundColor Red
+            Write-Host "WARNING: Processes are using the .dotnet folder!" -ForegroundColor Red
+            Write-Host "========================================================================" -ForegroundColor Red
+            Write-Host ""
+            Write-Host "The following processes have locks on files in .dotnet:" -ForegroundColor Yellow
+            foreach ($proc in $lockingProcesses) {
+                Write-Host "  - PID: $($proc.Id) | Name: $($proc.ProcessName) | Path: $($proc.Path)" -ForegroundColor Gray
+            }
+            Write-Host ""
+            Write-Host "To fix this, run:" -ForegroundColor Cyan
+            Write-Host '  Get-Process | Where-Object { $_.Path -like "*\.dotnet\*" } | ForEach-Object { Stop-Process -Id $_.Id -Force }' -ForegroundColor White
+            Write-Host ""
+            throw "Cannot proceed with locked .dotnet folder. Kill the processes above and retry."
+        }
+
+        Write-Host "No processes locking .dotnet folder" -ForegroundColor Green
+    }
+    else {
+        Write-Host "Skipping process lock check (not Windows)" -ForegroundColor Green
+    }
+    Write-Host ""
+
+    # ======================================================================
+    # Step 1: Build and Pack
+    # ======================================================================
+    if (-not $SkipBuild) {
+        Write-Host "========================================================================" -ForegroundColor Yellow
+        Write-Host "Step 1: Building and Packing MAUI..." -ForegroundColor Yellow
+        Write-Host "========================================================================" -ForegroundColor Yellow
+
+        if ($RunningOnWindows) {
+            $buildCmd = Join-Path $RepoRoot 'build.cmd'
+            $buildArgs = @("-restore", "-pack", "-configuration", $Configuration, "-warnAsError", "false")
+            Write-Host "Running: $buildCmd $($buildArgs -join ' ')" -ForegroundColor Gray
+            & $buildCmd @buildArgs
+        }
+        else {
+            $buildCmd = Join-Path $RepoRoot 'build.sh'
+            $buildArgs = @("-restore", "-pack", "-configuration", $Configuration, "-warnAsError", "false")
+            Write-Host "Running: $buildCmd $($buildArgs -join ' ')" -ForegroundColor Gray
+            & bash $buildCmd @buildArgs
+        }
+
+        if ($LASTEXITCODE -ne 0) {
+            throw "Build and pack failed with exit code $LASTEXITCODE"
+        }
+
+        Write-Host "Build and pack completed successfully" -ForegroundColor Green
+        Write-Host ""
+    }
+    else {
+        Write-Host "========================================================================" -ForegroundColor Yellow
+        Write-Host "Step 1: Skipping build (SkipBuild specified)" -ForegroundColor Yellow
+        Write-Host "========================================================================" -ForegroundColor Yellow
+        Write-Host ""
+    }
+
+    # ======================================================================
+    # Step 2: Install Workloads
+    # ======================================================================
+    $dotnetPath = if ($RunningOnWindows) {
+        Join-Path $RepoRoot ".dotnet\dotnet.exe"
+    } else {
+        Join-Path $RepoRoot ".dotnet/dotnet"
+    }
+
+    if (-not (Test-Path $dotnetPath)) {
+        if ($AutoProvision) {
+            Write-Host "========================================================================" -ForegroundColor Yellow
+            Write-Host "Auto-provisioning local .NET SDK and MAUI workloads..." -ForegroundColor Yellow
+            Write-Host "========================================================================" -ForegroundColor Yellow
+
+            Write-Host "Restoring dotnet tools..." -ForegroundColor Gray
+            & dotnet tool restore
+            if ($LASTEXITCODE -ne 0) {
+                throw "Failed to restore dotnet tools"
+            }
+
+            Write-Host "Provisioning local SDK (dotnet cake --target=dotnet)..." -ForegroundColor Gray
+            & dotnet cake --target=dotnet
+            if ($LASTEXITCODE -ne 0) {
+                throw "Failed to provision local SDK"
+            }
+
+            Write-Host "Installing MAUI workloads (dotnet cake --target=dotnet-local-workloads)..." -ForegroundColor Gray
+            & dotnet cake --target=dotnet-local-workloads
+            if ($LASTEXITCODE -ne 0) {
+                throw "Failed to install MAUI workloads"
+            }
+
+            Write-Host "Auto-provisioning completed successfully" -ForegroundColor Green
+            Write-Host ""
+        }
+        else {
+            throw "Local .dotnet SDK not found at: $dotnetPath. Run with -AutoProvision to automatically provision, or manually run: dotnet tool restore && dotnet cake --target=dotnet && dotnet cake --target=dotnet-local-workloads"
+        }
+    }
+
+    if (-not $SkipInstall) {
+        Write-Host "========================================================================" -ForegroundColor Yellow
+        Write-Host "Step 2: Installing MAUI Workloads..." -ForegroundColor Yellow
+        Write-Host "========================================================================" -ForegroundColor Yellow
+
+        $installArgs = @(
+            "build",
+            ".\src\DotNet\DotNet.csproj",
+            "-t:Install",
+            "-c", $Configuration
+        )
+
+        Write-Host "Running: $dotnetPath $($installArgs -join ' ')" -ForegroundColor Gray
+
+        & $dotnetPath @installArgs
+
+        if ($LASTEXITCODE -ne 0) {
+            throw "Workload installation failed with exit code $LASTEXITCODE"
+        }
+
+        Write-Host "Workload installation completed successfully" -ForegroundColor Green
+        Write-Host ""
+    }
+    else {
+        Write-Host "========================================================================" -ForegroundColor Yellow
+        Write-Host "Step 2: Skipping workload install (SkipInstall specified)" -ForegroundColor Yellow
+        Write-Host "========================================================================" -ForegroundColor Yellow
+        Write-Host ""
+    }
+
+    # ======================================================================
+    # Step 3: Extract MAUI Package Version
+    # ======================================================================
+    Write-Host "========================================================================" -ForegroundColor Yellow
+    Write-Host "Step 3: Extracting MAUI Package Version..." -ForegroundColor Yellow
+    Write-Host "========================================================================" -ForegroundColor Yellow
+
+    $packsPath = Join-Path $RepoRoot ".dotnet/packs/Microsoft.Maui.Sdk"
+
+    if (-not (Test-Path $packsPath)) {
+        throw "Microsoft.Maui.Sdk packs not found at: $packsPath"
+    }
+
+    $globalJsonPath = Join-Path $RepoRoot "global.json"
+    $globalJson = Get-Content $globalJsonPath | ConvertFrom-Json
+    $sdkVersion = $globalJson.tools.dotnet
+    $sdkMajorVersion = $sdkVersion.Split('.')[0]
+
+    Write-Host "SDK Version: $sdkVersion (major: $sdkMajorVersion)" -ForegroundColor Gray
+
+    $versionFolder = Get-ChildItem -Path $packsPath -Directory |
+        Where-Object { $_.Name -match "^$sdkMajorVersion\." } |
+        Sort-Object { [Version]($_.Name -replace '-.*$', '') } -Descending |
+        Select-Object -First 1
+
+    if (-not $versionFolder) {
+        Write-Host "No version matching SDK $sdkMajorVersion.x found, falling back to latest..." -ForegroundColor Yellow
+        $versionFolder = Get-ChildItem -Path $packsPath -Directory | Sort-Object Name -Descending | Select-Object -First 1
+    }
+
+    if (-not $versionFolder) {
+        throw "No version folders found in: $packsPath"
+    }
+
+    $mauiPackageVersion = $versionFolder.Name
+    $env:MAUI_PACKAGE_VERSION = $mauiPackageVersion
+
+    if ($SkipXcodeVersionCheck) {
+        $env:SKIP_XCODE_VERSION_CHECK = "true"
+        Write-Host "SKIP_XCODE_VERSION_CHECK: true" -ForegroundColor Yellow
+    }
+
+    Write-Host "MAUI_PACKAGE_VERSION: $mauiPackageVersion" -ForegroundColor Green
+    Write-Host "Environment variable set" -ForegroundColor Green
+    Write-Host ""
+
+    # ======================================================================
+    # Step 4: Run Integration Tests
+    # ======================================================================
+    Write-Host "========================================================================" -ForegroundColor Yellow
+    Write-Host "Step 4: Running Integration Tests..." -ForegroundColor Yellow
+    Write-Host "========================================================================" -ForegroundColor Yellow
+
+    $resultsPath = Join-Path $RepoRoot $ResultsDirectory
+    if (-not (Test-Path $resultsPath)) {
+        New-Item -ItemType Directory -Path $resultsPath -Force | Out-Null
+    }
+
+    $effectiveFilter = if ($TestFilter) {
+        $TestFilter
+    }
+    elseif ($Category) {
+        "Category=$Category"
+    }
+    else {
+        throw "Either -Category or -TestFilter must be specified"
+    }
+
+    $testProjectPath = Join-Path $RepoRoot "src/TestUtils/src/Microsoft.Maui.IntegrationTests/Microsoft.Maui.IntegrationTests.csproj"
+
+    $testArgs = @(
+        "test",
+        $testProjectPath,
+        "--configuration", $Configuration,
+        "--filter", $effectiveFilter,
+        "--logger", "trx",
+        "--results-directory", $resultsPath
+    )
+
+    Write-Host "Test Filter: $effectiveFilter" -ForegroundColor Cyan
+    Write-Host "Results Directory: $resultsPath" -ForegroundColor Cyan
+    Write-Host "Running: $dotnetPath $($testArgs -join ' ')" -ForegroundColor Gray
+    Write-Host ""
+
+    & $dotnetPath @testArgs
+
+    $testExitCode = $LASTEXITCODE
+
+    Write-Host ""
+    Write-Host "========================================================================" -ForegroundColor Cyan
+    Write-Host "                    Test Summary                                       " -ForegroundColor Cyan
+    Write-Host "========================================================================" -ForegroundColor Cyan
+    Write-Host "Configuration:        $Configuration"
+    Write-Host "Category/Filter:      $effectiveFilter"
+    Write-Host "MAUI_PACKAGE_VERSION: $mauiPackageVersion"
+    Write-Host "Results Directory:    $resultsPath"
+
+    if ($testExitCode -eq 0) {
+        Write-Host "Result:               PASSED" -ForegroundColor Green
+    }
+    else {
+        Write-Host "Result:               FAILED (Exit Code: $testExitCode)" -ForegroundColor Red
+    }
+
+    Write-Host "========================================================================" -ForegroundColor Cyan
+
+    $trxFiles = Get-ChildItem -Path $resultsPath -Filter "*.trx" -ErrorAction SilentlyContinue
+    if ($trxFiles) {
+        Write-Host ""
+        Write-Host "Generated TRX Files:" -ForegroundColor Yellow
+        foreach ($trx in $trxFiles) {
+            Write-Host "  - $($trx.FullName)" -ForegroundColor Gray
+        }
+    }
+
+    exit $testExitCode
+}
+catch {
+    Write-Host ""
+    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
+    Write-Host $_.ScriptStackTrace -ForegroundColor Red
+    exit 1
+}
+finally {
+    Pop-Location
+}
diff --git a/src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs b/src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs
index c42775f45790..80c493c1bc39 100644
--- a/src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs
+++ b/src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs
@@ -102,6 +102,33 @@ private void SetUpNuGetPackages()
 				FileUtilities.ReplaceInFile(TestNuGetConfig, "<add key=\"nuget-only\" value=\"true\" />", "");
 				FileUtilities.ReplaceInFile(TestNuGetConfig, "NUGET_ONLY_PLACEHOLDER", extraPacksDir);

+				// Create a Directory.Build.props in the test directory root to prevent MSBuild from
+				// walking up and inheriting the MAUI repo's Arcade SDK settings. This ensures test
+				// projects use their own local obj/bin folders instead of the repo's artifacts folder.
+				var testDirBuildProps = Path.Combine(TestEnvironment.GetTestDirectoryRoot(), "Directory.Build.props");
+				if (!File.Exists(testDirBuildProps))
+				{
+					File.WriteAllText(testDirBuildProps, """
+						<Project>
+						  <!-- This file stops MSBuild from walking up the directory tree and inheriting
+						       the MAUI repo's Directory.Build.props and Arcade SDK settings.
+						       This ensures test projects use their own local obj/bin folders. -->
+						</Project>
+						""");
+				}
+
+				// Also create Directory.Build.targets to prevent target inheritance
+				var testDirBuildTargets = Path.Combine(TestEnvironment.GetTestDirectoryRoot(), "Directory.Build.targets");
+				if (!File.Exists(testDirBuildTargets))
+				{
+					File.WriteAllText(testDirBuildTargets, """
+						<Project>
+						  <!-- This file stops MSBuild from walking up the directory tree and inheriting
+						       the MAUI repo's Directory.Build.targets. -->
+						</Project>
+						""");
+				}
+
 				_isSetupComplete = true;
 			}
 		}

PATCH

echo "Patch applied successfully."
