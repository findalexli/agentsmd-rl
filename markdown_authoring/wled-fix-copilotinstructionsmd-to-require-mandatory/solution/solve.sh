#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wled

# Idempotency guard
if grep -qF "**When validating your changes before finishing, you MUST wait for the hardware " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -30,6 +30,27 @@ The build has two main phases:
    - Common environments: `nodemcuv2`, `esp32dev`, `esp8266_2m`
    - List all targets: `pio run --list-targets`
 
+## Before Finishing Work
+
+**CRITICAL: You MUST complete ALL of these steps before marking your work as complete:**
+
+1. **Run the test suite**: `npm test` -- Set timeout to 2+ minutes. NEVER CANCEL.
+   - All tests MUST pass
+   - If tests fail, fix the issue before proceeding
+
+2. **Build at least one hardware environment**: `pio run -e esp32dev` -- Set timeout to 30+ minutes. NEVER CANCEL.
+   - Choose `esp32dev` as it's a common, representative environment
+   - See "Hardware Compilation" section above for the full list of common environments
+   - The build MUST complete successfully without errors
+   - If the build fails, fix the issue before proceeding
+   - **DO NOT skip this step** - it validates that firmware compiles with your changes
+
+3. **For web UI changes only**: Manually test the interface
+   - See "Manual Testing Scenarios" section below
+   - Verify the UI loads and functions correctly
+
+**If any of these validation steps fail, you MUST fix the issues before finishing. Do NOT mark work as complete with failing builds or tests.**
+
 ## Validation and Testing
 
 ### Web UI Testing
@@ -44,7 +65,7 @@ The build has two main phases:
 - **Code style**: Use tabs for web files (.html/.css/.js), spaces (2 per level) for C++ files
 - **C++ formatting available**: `clang-format` is installed but not in CI
 - **Always run tests before finishing**: `npm test`
-- **Always run a build for the common environment before finishing**
+- **MANDATORY: Always run a hardware build before finishing** (see "Before Finishing Work" section below)
 
 ### Manual Testing Scenarios
 After making changes to web UI, always test:
@@ -100,10 +121,16 @@ package.json           # Node.js dependencies and scripts
 
 ## Build Timing and Timeouts
 
-- **Web UI build**: 3 seconds - Set timeout to 30 seconds minimum
-- **Test suite**: 40 seconds - Set timeout to 2 minutes minimum  
-- **Hardware builds**: 15+ minutes - Set timeout to 30+ minutes minimum
-- **NEVER CANCEL long-running builds** - PlatformIO downloads and compilation can take significant time
+**IMPORTANT: Use these timeout values when running builds:**
+
+- **Web UI build** (`npm run build`): 3 seconds typical - Set timeout to 30 seconds minimum
+- **Test suite** (`npm test`): 40 seconds typical - Set timeout to 120 seconds (2 minutes) minimum  
+- **Hardware builds** (`pio run -e [target]`): 15-20 minutes typical for first build - Set timeout to 1800 seconds (30 minutes) minimum
+  - Subsequent builds are faster due to caching
+  - First builds download toolchains and dependencies which takes significant time
+- **NEVER CANCEL long-running builds** - PlatformIO downloads and compilation require patience
+
+**When validating your changes before finishing, you MUST wait for the hardware build to complete successfully. Set the timeout appropriately and be patient.**
 
 ## Troubleshooting
 
@@ -129,11 +156,17 @@ package.json           # Node.js dependencies and scripts
 - **Hardware builds require appropriate ESP32/ESP8266 development board**
 
 ## CI/CD Pipeline
-The GitHub Actions workflow:
+
+**The GitHub Actions CI workflow will:**
 1. Installs Node.js and Python dependencies
-2. Runs `npm test` to validate build system
-3. Builds web UI with `npm run build` 
-4. Compiles firmware for multiple hardware targets
+2. Runs `npm test` to validate build system (MUST pass)
+3. Builds web UI with `npm run build` (automatically run by PlatformIO)
+4. Compiles firmware for ALL hardware targets listed in `default_envs` (MUST succeed for all)
 5. Uploads build artifacts
 
-Match this workflow in your local development to ensure CI success.
+**To ensure CI success, you MUST locally:**
+- Run `npm test` and ensure it passes
+- Run `pio run -e esp32dev` (or another common environment from "Hardware Compilation" section) and ensure it completes successfully
+- If either fails locally, it WILL fail in CI
+
+**Match this workflow in your local development to ensure CI success. Do not mark work complete until you have validated builds locally.**
PATCH

echo "Gold patch applied."
