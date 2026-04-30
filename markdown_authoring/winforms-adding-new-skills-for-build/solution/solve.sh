#!/usr/bin/env bash
set -euo pipefail

cd /workspace/winforms

# Idempotency guard
if grep -qF "* Visual Studio 2022 (for IDE builds) \u2014 see `WinForms.vsconfig` for required wor" ".github/skills/building-code/SKILL.md" && grep -qF "| Test exe still says \"framework not found\" after install | Ensure the **archite" ".github/skills/download-sdk/SKILL.md" && grep -qF "| `[Collection(\"Sequential\")]` | Tests that must **not** run in parallel (e.g. c" ".github/skills/running-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/building-code/SKILL.md b/.github/skills/building-code/SKILL.md
@@ -0,0 +1,153 @@
+---
+name: building-code
+description: >-
+  Instructions for restoring and building the WinForms repository.
+  Use when asked how to restore NuGet packages, build the full solution,
+  build a single project, create packages, or troubleshoot build errors.
+metadata:
+  author: dotnet-winforms
+  version: "1.0"
+---
+
+# Building the WinForms Repository
+
+## Prerequisites
+
+* Windows is required for WinForms runtime scenarios, test execution, and Visual
+  Studio workflows.
+* Linux is supported for command-line restore/build only; use `build.sh`
+  instead of `build.cmd` / `Restore.cmd`.
+* Visual Studio 2022 (for IDE builds) — see `WinForms.vsconfig` for required workloads.
+* The repo-local .NET SDK (specified in `global.json`) is used automatically by
+  `build.cmd` and `Restore.cmd`. You do **not** need a machine-wide SDK install
+  for command-line builds.
+
+---
+
+## 1  Restore
+
+Restoring downloads the repo-local SDK and all NuGet packages.
+
+```
+.\Restore.cmd
+```
+
+Under the hood this runs:
+
+```powershell
+eng\common\Build.ps1 -NativeToolsOnMachine -restore
+```
+
+You can pass any extra `Build.ps1` flags after `Restore.cmd`, e.g.
+`.\Restore.cmd -configuration Release`.
+
+---
+
+## 2  Full Solution Build (preferred)
+
+```
+.\build.cmd
+```
+
+This restores **and** builds `Winforms.sln` in `Debug|Any CPU` by default.
+
+Under the hood this runs:
+
+```powershell
+eng\common\Build.ps1 -NativeToolsOnMachine -restore -build -bl
+```
+
+### Common flags
+
+| Flag | Short | Description |
+|------|-------|-------------|
+| `-configuration <Debug\|Release>` | `-c` | Build configuration (default: `Debug`) |
+| `-platform <x86\|x64\|Any CPU>` | | Platform (default: `Any CPU`) |
+| `-restore` | `-r` | Restore only |
+| `-build` | `-b` | Build only (skip restore if already done) |
+| `-rebuild` | | Clean + build |
+| `-clean` | | Delete build artifacts |
+| `-pack` | | Create NuGet packages (`Microsoft.Private.Winforms`) |
+| `-bl` / `-binaryLog` | | Emit `artifacts\log\Debug\Build.binlog` |
+| `-ci` | | CI mode (stricter warnings, signing, etc.) |
+| `-test` | `-t` | Build **and** run unit tests |
+| `-integrationTest` | | Build **and** run integration / functional tests |
+
+### Examples
+
+```bash
+# Release build
+.\build.cmd -configuration Release
+
+# Build and run unit tests
+.\build.cmd -test
+
+# Create NuGet package
+.\build.cmd -pack
+```
+
+---
+
+## 3  Optimized Building a Single Project (fast inner-loop)
+
+Prefer rebuilding just the project(s) with recent changes by using the
+standard `dotnet build` command, **after** at least one initial successful
+full restore (via `.\Restore.cmd` or `.\build.cmd`).
+
+This is **much** faster than building the whole solution.
+
+```bash
+# Build a single src project
+dotnet build src\System.Windows.Forms\System.Windows.Forms.csproj
+
+# Build a single test project
+dotnet build src\test\unit\System.Windows.Forms\System.Windows.Forms.Tests.csproj
+
+# Release configuration
+dotnet build src\System.Windows.Forms\System.Windows.Forms.csproj -c Release
+```
+
+> **Tip:** The repo-local SDK must be on your `PATH`. Running `.\start-code.cmd`
+> or `.\start-vs.cmd` prepends it automatically. From a plain terminal you can
+> also run `.\Restore.cmd` first (it sets up the SDK).
+
+---
+
+## 4  Building from Visual Studio
+
+1. Run `.\Restore.cmd` (one-time, or after SDK/package changes).
+2. Run `.\start-vs.cmd` — opens `Winforms.sln` with the repo-local SDK on `PATH`.
+3. Build normally (<kbd>Ctrl+Shift+B</kbd>).
+
+## 5  Building from Visual Studio Code
+
+1. (Optional) `.\Restore.cmd`
+2. `.\start-code.cmd` — opens the workspace with the repo-local SDK on `PATH`.
+3. Build from the integrated terminal: `.\build.cmd` or `dotnet build <project>`.
+
+---
+
+## Build Outputs
+
+| Artifact | Location |
+|----------|----------|
+| Binaries | `artifacts\bin\<Project>\Debug\<tfm>\` |
+| Logs | `artifacts\log\` |
+| Binary log | `artifacts\log\Debug\Build.binlog` |
+| Test results | `artifacts\TestResults\` |
+| NuGet packages | `artifacts\packages\` |
+
+Use the [MSBuild Structured Log Viewer](https://msbuildlog.com/) to inspect
+`.binlog` files when troubleshooting build errors.
+
+---
+
+## Troubleshooting
+
+* **Most errors are compile errors** — fix them as usual.
+* **MSBuild task errors** — inspect `artifacts\log\Debug\Build.binlog`.
+* **SDK version mismatch** — the repo pins its SDK in `global.json`;
+  run `.\Restore.cmd` to ensure the correct SDK is available.
+* **VS preview features** — if using a non-Preview VS, enable
+  *Tools → Options → Environment → Preview Features →
+  Use previews of the .NET SDK*.
diff --git a/.github/skills/download-sdk/SKILL.md b/.github/skills/download-sdk/SKILL.md
@@ -0,0 +1,194 @@
+---
+name: download-sdk
+description: >-
+  Instructions for downloading and installing .NET preview runtime versions
+  required by the WinForms repository. Use when test executables fail with
+  "framework not found" errors or when a specific .NET preview runtime
+  version needs to be installed.
+metadata:
+  author: dotnet-winforms
+  version: "1.0"
+---
+
+# Downloading and Installing .NET Preview Runtimes
+
+The WinForms repository targets **.NET preview** builds. Test executables and
+built assemblies require a matching runtime version that may not be publicly
+available on the official .NET download page. Use the internal CI feed URL
+pattern below to download and install the exact version needed.
+
+---
+
+## 1  Determining the Required Version
+
+The required runtime version can be found in multiple ways:
+
+### From an error message
+
+When a test executable cannot find its target framework, the error includes the
+version:
+
+```
+Framework: 'Microsoft.NETCore.App', version '11.0.0-preview.4.26203.108' (x64)
+```
+
+### From runtimeconfig.json (programmatic — preferred)
+
+Each test executable has a `.runtimeconfig.json` next to it that declares the
+exact version required:
+
+```powershell
+$rc = Get-Content "artifacts\bin\System.Windows.Forms.Tests\Debug\net11.0-windows7.0\System.Windows.Forms.Tests.runtimeconfig.json" | ConvertFrom-Json
+$version = $rc.runtimeOptions.framework.version
+Write-Host "Required runtime: $version"
+```
+
+---
+
+## 2  Download URL Pattern
+
+Use the following base URL, replacing `{version}` with the full version string:
+
+### x64 (64-bit) — required for standard test runs
+
+```
+https://ci.dot.net/public/Runtime/{version}/dotnet-runtime-{version}-win-x64.msi
+```
+
+### x86 (32-bit) — required for 32-bit test runs
+
+```
+https://ci.dot.net/public/Runtime/{version}/dotnet-runtime-{version}-win-x86.msi
+```
+
+### Example
+
+For version `11.0.0-preview.4.26203.108`:
+
+```
+x64: https://ci.dot.net/public/Runtime/11.0.0-preview.4.26203.108/dotnet-runtime-11.0.0-preview.4.26203.108-win-x64.msi
+x86: https://ci.dot.net/public/Runtime/11.0.0-preview.4.26203.108/dotnet-runtime-11.0.0-preview.4.26203.108-win-x86.msi
+```
+
+---
+
+## 3  Download and Install (PowerShell)
+
+```powershell
+$version = "11.0.0-preview.4.26203.108"   # ← replace with needed version
+
+# Download both architectures
+$url64 = "https://ci.dot.net/public/Runtime/$version/dotnet-runtime-$version-win-x64.msi"
+$url86 = "https://ci.dot.net/public/Runtime/$version/dotnet-runtime-$version-win-x86.msi"
+$msi64 = "$env:TEMP\dotnet-runtime-$version-win-x64.msi"
+$msi86 = "$env:TEMP\dotnet-runtime-$version-win-x86.msi"
+
+Invoke-WebRequest -Uri $url64 -OutFile $msi64 -UseBasicParsing
+Invoke-WebRequest -Uri $url86 -OutFile $msi86 -UseBasicParsing
+
+# Install (requires elevation)
+Start-Process msiexec.exe -ArgumentList "/i `"$msi64`" /quiet /norestart" -Wait -Verb RunAs
+Start-Process msiexec.exe -ArgumentList "/i `"$msi86`" /quiet /norestart" -Wait -Verb RunAs
+
+# Verify installation
+& "C:\Program Files\dotnet\dotnet.exe" --list-runtimes | Select-String $version
+
+# Clean up
+Remove-Item $msi64, $msi86 -ErrorAction SilentlyContinue
+```
+
+> **Important:** The `-Verb RunAs` flag triggers a UAC elevation prompt.
+> Without it, the MSI install silently fails with exit code **1603**.
+
+---
+
+## 4  Verifying the Installation
+
+After installation, verify the runtime is available:
+
+```powershell
+# x64
+& "C:\Program Files\dotnet\dotnet.exe" --list-runtimes | Select-String $version
+
+# x86
+& "C:\Program Files (x86)\dotnet\dotnet.exe" --list-runtimes | Select-String $version
+
+# Or check the shared framework directory directly
+Get-ChildItem "C:\Program Files\dotnet\shared\Microsoft.NETCore.App" -Filter "$($version.Split('-')[0])*"
+Get-ChildItem "C:\Program Files (x86)\dotnet\shared\Microsoft.NETCore.App" -Filter "$($version.Split('-')[0])*"
+```
+
+---
+
+## 5  Fully Automated: Detect, Download, and Install
+
+This script reads the required version from any test executable's
+`runtimeconfig.json`, downloads both architectures, and installs them:
+
+```powershell
+# Auto-detect version from the first test runtimeconfig found
+$rc = Get-ChildItem "artifacts\bin\*Tests*\Debug\*\*.runtimeconfig.json" |
+    Select-Object -First 1
+$version = (Get-Content $rc | ConvertFrom-Json).runtimeOptions.framework.version
+Write-Host "Required runtime: $version"
+
+# Check if already installed
+$installed = & "C:\Program Files\dotnet\dotnet.exe" --list-runtimes 2>$null |
+    Select-String ([regex]::Escape($version))
+if ($installed) {
+    Write-Host "Runtime $version is already installed."
+    return
+}
+
+# Download
+$base = "https://ci.dot.net/public/Runtime/$version"
+$msi64 = "$env:TEMP\dotnet-runtime-$version-win-x64.msi"
+$msi86 = "$env:TEMP\dotnet-runtime-$version-win-x86.msi"
+Invoke-WebRequest "$base/dotnet-runtime-$version-win-x64.msi" -OutFile $msi64 -UseBasicParsing
+Invoke-WebRequest "$base/dotnet-runtime-$version-win-x86.msi" -OutFile $msi86 -UseBasicParsing
+
+# Install (elevated)
+Start-Process msiexec.exe -ArgumentList "/i `"$msi64`" /quiet /norestart" -Wait -Verb RunAs
+Start-Process msiexec.exe -ArgumentList "/i `"$msi86`" /quiet /norestart" -Wait -Verb RunAs
+
+# Verify
+& "C:\Program Files\dotnet\dotnet.exe" --list-runtimes | Select-String $version
+
+# Clean up
+Remove-Item $msi64, $msi86 -ErrorAction SilentlyContinue
+```
+
+---
+
+## 6  Alternative: Use the Repo-Local Runtime
+
+The repository includes a local `.dotnet` folder (populated by `.\Restore.cmd`)
+that may already have the required runtime. To use it instead of installing
+system-wide:
+
+```powershell
+# From the repository root:
+$env:DOTNET_ROOT = "$PWD\.dotnet"
+$env:PATH = "$PWD\.dotnet;$env:PATH"
+```
+
+Check available versions:
+
+```powershell
+Get-ChildItem ".dotnet\shared\Microsoft.NETCore.App" | Select Name
+```
+
+> **Note:** The repo-local runtime works for running test executables but may
+> not be picked up by `vstest.console.exe` or other external tools.
+
+---
+
+## 7  Troubleshooting
+
+| Problem | Solution |
+|---------|----------|
+| MSI install fails with exit code **1603** | Run with `-Verb RunAs` for admin elevation |
+| MSI install exits **0** but runtime not listed | The install ran without elevation and failed silently — retry with `-Verb RunAs` |
+| Download returns **404** | Double-check the version string; the runtime may not be published to the CI feed yet |
+| Test exe still says "framework not found" after install | Ensure the **architecture** matches (x64 vs x86); check that the test exe is looking for `Microsoft.NETCore.App` (not `Microsoft.WindowsDesktop.App` or `Microsoft.AspNetCore.App`) |
+| Need `Microsoft.WindowsDesktop.App` | Replace `Runtime` with `WindowsDesktop` in the URL: `https://ci.dot.net/public/WindowsDesktop/{version}/windowsdesktop-runtime-{version}-win-x64.msi` |
diff --git a/.github/skills/running-tests/SKILL.md b/.github/skills/running-tests/SKILL.md
@@ -0,0 +1,341 @@
+---
+name: running-tests
+description: >-
+  Instructions for running unit tests, integration tests, and individual tests
+  in the WinForms repository. Use this when asked how to run tests, filter
+  them, use Visual Studio workflows, or troubleshoot test failures.
+metadata:
+  author: dotnet-winforms
+  version: "2.0"
+---
+
+# Running Tests in the WinForms Repository
+
+The repository uses **xUnit v3** with **Microsoft.Testing.Platform** as its
+test framework. Tests are organized into **unit tests** and
+**integration / functional tests**.
+
+> **Important:** The test projects build as self-contained executables using
+> Microsoft.Testing.Platform (not the legacy VSTest adapter). The `dotnet test`
+> `--filter` flag and `vstest.console.exe` do **not** work with these projects.
+> See sections 4 and 4b for the correct filtering syntax.
+
+---
+
+## 1  Running All Unit Tests
+
+```bash
+.\build.cmd -test
+```
+
+This builds the solution **and** executes every unit test project. Results
+appear in `artifacts\TestResults\`.
+
+### Release configuration
+
+```bash
+.\build.cmd -test -configuration Release
+```
+
+---
+
+## 2  Running All Integration / Functional Tests
+
+```bash
+.\build.cmd -integrationTest
+```
+
+Functional tests open and close windows automatically — do not interact with the
+desktop while they run.
+
+---
+
+## 3  Running Tests for a Single Project
+
+After a full build (`.\build.cmd`), navigate to the test project directory and
+use `dotnet test`:
+
+```bash
+# Unit tests for System.Windows.Forms
+pushd src\test\unit\System.Windows.Forms
+dotnet test
+
+# Unit tests for System.Drawing.Common
+pushd src\System.Drawing.Common\tests
+dotnet test
+
+# Unit tests for System.Windows.Forms.Primitives
+pushd src\System.Windows.Forms.Primitives\tests\UnitTests
+dotnet test
+```
+
+> **Tip:** The repo-local SDK must be on your `PATH`.
+> Run `.\Restore.cmd` or launch via `.\start-code.cmd` / `.\start-vs.cmd`.
+
+### Key test project paths
+
+| Test suite | Project directory |
+|------------|-------------------|
+| System.Windows.Forms.Tests | `src\test\unit\System.Windows.Forms` |
+| System.Drawing.Common.Tests | `src\System.Drawing.Common\tests` |
+| System.Windows.Forms.Primitives.Tests | `src\System.Windows.Forms.Primitives\tests\UnitTests` |
+| System.Windows.Forms.Design.Tests | `src\System.Windows.Forms.Design\tests\UnitTests` |
+| System.Windows.Forms.Analyzers.Tests | `src\System.Windows.Forms.Analyzers\tests\UnitTests` |
+
+---
+
+## 4  Running a Single Test or Filtered Tests (via executable)
+
+The preferred way to run individual tests is to invoke the compiled test
+executable directly from `artifacts\bin\`. The executables use xUnit v3's
+built-in filter options — **not** the `--filter` flag.
+
+### Prerequisites
+
+The test executables target a .NET preview runtime. The correct runtime version
+must be installed system-wide, **or** you must set `DOTNET_ROOT` to the
+repo-local `.dotnet` folder:
+
+```powershell
+# From the repository root:
+$env:DOTNET_ROOT = "$PWD\.dotnet"
+$env:PATH = "$PWD\.dotnet;$env:PATH"
+```
+
+If the required .NET runtime is not installed, use the `download-sdk` skill to
+install it.
+
+> **Note:** The TFM in executable paths (e.g. `net11.0`) changes with each
+> major .NET version. Check `artifacts\bin\<ProjectName>\Debug\` for the
+> actual TFM directory name.
+
+### Filter by method name (fully qualified)
+
+```powershell
+& "artifacts\bin\System.Windows.Forms.Tests\Debug\net11.0-windows7.0\System.Windows.Forms.Tests.exe" `
+  --filter-method "System.Windows.Forms.Tests.ButtonTests.Button_AutoSizeModeGetSet"
+```
+
+### Filter by class
+
+```powershell
+& "artifacts\bin\System.Windows.Forms.Tests\Debug\net11.0-windows7.0\System.Windows.Forms.Tests.exe" `
+  --filter-class "System.Windows.Forms.Tests.ButtonTests"
+```
+
+### Filter by namespace
+
+```powershell
+& "artifacts\bin\System.Drawing.Common.Tests\Debug\net11.0\System.Drawing.Common.Tests.exe" `
+  --filter-namespace "System.Drawing.Tests"
+```
+
+### Wildcard matching
+
+All filter options support `*` wildcards at the beginning and/or end:
+
+```powershell
+# All test methods containing "AutoSize"
+--filter-method "*AutoSize*"
+
+# All classes ending with "ButtonTests"
+--filter-class "*ButtonTests"
+```
+
+### Filter by trait
+
+```powershell
+--filter-trait "Category=Accessibility"
+```
+
+### Exclude tests (negated filters)
+
+```powershell
+--filter-not-method "*SlowTest*"
+--filter-not-class "System.Windows.Forms.Tests.ClipboardTests"
+--filter-not-trait "Category=Interactive"
+```
+
+### Query filter language
+
+For complex filtering, use `--filter-query` with xUnit's
+[query filter language](https://xunit.net/docs/query-filter-language):
+
+```powershell
+--filter-query "/*/*/ButtonTests/*"
+```
+
+### Useful options
+
+| Option | Description |
+|--------|-------------|
+| `--list-tests` | List all tests without running them |
+| `--stop-on-fail` `on` | Stop on first failure |
+| `--show-live-output` `on` | Show `ITestOutputHelper` output live |
+| `--output` `Detailed` | Verbose output |
+| `--parallel` `none` | Disable parallel execution |
+| `--report-trx` | Generate a TRX report |
+| `--report-xunit-html` | Generate an HTML report |
+
+---
+
+## 4b  Running a Single Test via `dotnet test` (alternative)
+
+`dotnet test` can also be used from the test project directory, but note that
+the `--filter` flag **does not work** with the Microsoft.Testing.Platform
+runner. To pass xUnit v3 filter options through `dotnet test`, use `--`:
+
+```bash
+pushd src\test\unit\System.Windows.Forms
+dotnet test -- --filter-method "System.Windows.Forms.Tests.ButtonTests.Button_AutoSizeModeGetSet"
+```
+
+> **Note:** If `dotnet test --filter` reports "Zero tests ran" with exit
+> code 5, this is expected — switch to the executable approach in section 4
+> or use the `--` separator.
+
+---
+
+## 5  Running Tests from Visual Studio
+
+1. Launch via `.\start-vs.cmd` (ensures repo-local SDK is on `PATH`).
+2. Open **Test Explorer** (<kbd>Ctrl+E, T</kbd>).
+3. Run / debug tests as usual.
+
+For common VS-specific issues see `docs\testing-in-vs.md`.
+
+---
+
+## 6  Test Project Layout
+
+Each WinForms library has its own test projects:
+
+```
+src\
+  test\
+    unit\
+      System.Windows.Forms\       ← System.Windows.Forms.Tests.csproj
+  System.Drawing.Common\
+    tests\                        ← System.Drawing.Common.Tests.csproj
+  System.Windows.Forms.Primitives\
+    tests\UnitTests\              ← ...Primitives.Tests.csproj
+  System.Windows.Forms.Design\
+    tests\UnitTests\              ← ...Design.Tests.csproj
+  System.Windows.Forms.Analyzers\
+    tests\UnitTests\              ← ...Analyzers.Tests.csproj
+  ...
+```
+
+Test output (compiled executables) goes to:
+
+```
+artifacts\bin\<ProjectName>\Debug\<tfm>\<ProjectName>.exe
+```
+
+New test source files are auto-included (SDK-style project) — no `.csproj`
+edits needed.
+
+---
+
+## 7  Test Attributes & Categories
+
+| Attribute | When to use |
+|-----------|-------------|
+| `[WinFormsFact]` / `[WinFormsTheory]` | Tests involving UI controls or requiring a synchronization context |
+| `[StaFact]` / `[StaTheory]` | Tests requiring an STA thread but not the full WinForms context |
+| `[Fact]` / `[Theory]` | Pure logic tests with no UI or threading requirements |
+| `[Collection("Sequential")]` | Tests that must **not** run in parallel (e.g. clipboard, drag-and-drop, global state) |
+
+### Theory data
+
+Use `[InlineData]` or `[MemberData]` for parameterized tests. Avoid creating
+UI controls inside member-data methods — create them inside the test body
+instead.
+
+---
+
+## 8  Test Results & Troubleshooting
+
+| Artifact | Location |
+|----------|----------|
+| TRX results | `artifacts\TestResults\Debug\<Project>_<tfm>_<arch>.trx` |
+| HTML results | `artifacts\TestResults\Debug\<Project>_<tfm>_<arch>.html` |
+| XML results | `artifacts\TestResults\Debug\<Project>_<tfm>_<arch>.xml` |
+| Log summary | `artifacts\log\` |
+| Binary log | `artifacts\log\Debug\Build.binlog` |
+
+### Parsing test results programmatically
+
+TRX files are XML with namespace `http://microsoft.com/schemas/VisualStudio/TeamTest/2010`.
+To find failed tests:
+
+```powershell
+Get-ChildItem "artifacts\TestResults\Debug\*.trx" | ForEach-Object {
+    [xml]$trx = Get-Content $_.FullName
+    $ns = @{t='http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
+    $counters = Select-Xml -Xml $trx -XPath '//t:ResultSummary/t:Counters' -Namespace $ns |
+        Select-Object -ExpandProperty Node
+    if ([int]$counters.failed -gt 0) {
+        Write-Host "=== $($_.BaseName) ($($counters.failed) failed) ==="
+        Select-Xml -Xml $trx -XPath '//t:UnitTestResult[@outcome="Failed"]' -Namespace $ns |
+            ForEach-Object { Write-Host "  FAIL: $($_.Node.testName)" }
+    }
+}
+```
+
+### Common issues
+
+* **"Zero tests ran" with `dotnet test --filter`** — the repo uses
+  Microsoft.Testing.Platform, which does not support the `--filter` flag.
+  Use the test executable directly with `--filter-method` /
+  `--filter-class` (see section 4), or pass filters after `--` separator.
+* **"Could not find testhost" / "testhost.deps.json not found"** —
+  `vstest.console.exe` and `dotnet vstest` cannot run these test assemblies.
+  Use the test executable directly (section 4).
+* **"framework not found" when running test .exe** — the required .NET
+  preview runtime is not installed. Set `DOTNET_ROOT` to the repo-local
+  `.dotnet` folder, or install the runtime using the `download-sdk` skill.
+* **Test runner crash** — configure automatic memory-dump collection
+  ([Collecting User-Mode Dumps](https://learn.microsoft.com/windows/win32/wer/collecting-user-mode-dumps)),
+  then reproduce and inspect the dump in WinDbg.
+* **Flaky clipboard / drag-and-drop tests** — ensure they are in the
+  `[Collection("Sequential")]` collection so they don't run in parallel.
+* **VS test discovery fails** — see `docs\testing-in-vs.md`.
+
+---
+
+## Quick-Reference Command Cheat Sheet
+
+```bash
+# Full build + all unit tests
+.\build.cmd -test
+
+# Full build + all integration tests
+.\build.cmd -integrationTest
+
+# Single project tests (after initial build)
+pushd src\test\unit\System.Windows.Forms
+dotnet test
+
+# --- Running individual tests via executable (preferred) ---
+
+# Set up repo-local runtime (from repo root, if system runtime is not installed)
+$env:DOTNET_ROOT = "$PWD\.dotnet"
+$env:PATH = "$PWD\.dotnet;$env:PATH"
+
+# Single test by fully-qualified method name
+& "artifacts\bin\System.Windows.Forms.Tests\Debug\net11.0-windows7.0\System.Windows.Forms.Tests.exe" `
+  --filter-method "System.Windows.Forms.Tests.ButtonTests.Button_AutoSizeModeGetSet"
+
+# All tests in a class
+& "artifacts\bin\System.Windows.Forms.Tests\Debug\net11.0-windows7.0\System.Windows.Forms.Tests.exe" `
+  --filter-class "System.Windows.Forms.Tests.ButtonTests"
+
+# Wildcard match on method name
+& "artifacts\bin\System.Windows.Forms.Tests\Debug\net11.0-windows7.0\System.Windows.Forms.Tests.exe" `
+  --filter-method "*AutoSize*"
+
+# List all tests without running
+& "artifacts\bin\System.Windows.Forms.Tests\Debug\net11.0-windows7.0\System.Windows.Forms.Tests.exe" `
+  --list-tests
+```
PATCH

echo "Gold patch applied."
