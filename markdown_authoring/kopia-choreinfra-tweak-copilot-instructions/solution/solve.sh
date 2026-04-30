#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kopia

# Idempotency guard
if grep -qF "11. **Trust these instructions** - These instructions have been validated by run" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -65,18 +65,14 @@ make lint
 make lint-fix
 ```
 
+Note: Linting is **NOT** run on linux/arm64 or linux/arm platforms to avoid issues.
+
 **Check code locks:**
 ```bash
 make check-locks
 ```
 **Note:** Not available on linux/arm64 or linux/arm.
 
-**Check JavaScript/TypeScript formatting (in app directory):**
-```bash
-make check-prettier
-```
-
-**Important:** Linting is **NOT** run on linux/arm64 or linux/arm platforms to avoid issues.
 
 ### Building Kopia CLI
 
@@ -120,7 +116,7 @@ make kopia-ui
 make test
 ```
 **Time:** ~2-4 minutes
-**Runs:** All unit tests with gotestsum, excludes TestIndexBlobManagerStress
+**Runs:** All unit tests with gotestsum
 **Timeout:** 1200s (20 minutes) per test
 **Format:** pkgname-and-test-fails
 
@@ -132,12 +128,6 @@ make test-with-coverage
 **Time:** ~3-5 minutes
 **Note:** Used by Code Coverage workflow. Sets KOPIA_COVERAGE_TEST=1
 
-### Index Blob Tests (Separate)
-```bash
-make test-index-blob-v0
-```
-**Runs:** TestIndexBlobManagerStress (excluded from standard tests due to duration)
-
 ### Integration Tests
 ```bash
 make build-integration-test-binary  # Build test binary first
@@ -146,6 +136,11 @@ make integration-tests
 **Time:** ~5-10 minutes
 **Requires:** KOPIA_INTEGRATION_EXE environment variable
 
+**Race Detector Tests:**
+```bash
+make test UNIT_TEST_RACE_FLAGS=-race UNIT_TESTS_TIMEOUT=1200s
+```
+
 ### CI Test Suites
 ```bash
 make ci-tests  # Runs: vet + test
@@ -157,7 +152,7 @@ make ci-integration-tests  # Runs: robustness-tool-tests + socket-activation-tes
 make provider-tests PROVIDER_TEST_TARGET=...
 ```
 **Time:** 15 minutes timeout
-**Requires:** KOPIA_PROVIDER_TEST=true, credentials for storage backend, rclone binary
+**Requires:** KOPIA_PROVIDER_TEST=true, credentials for storage backend.
 **Note:** Tests various cloud storage providers (S3, Azure, GCS, etc.)
 
 ### Other Test Types
@@ -167,11 +162,6 @@ make provider-tests PROVIDER_TEST_TARGET=...
 - `make stress-test` - Stress tests (1 hour timeout)
 - `make htmlui-e2e-test` - HTML UI end-to-end tests (10 minutes timeout)
 
-**Race Detector Tests:**
-```bash
-make test UNIT_TEST_RACE_FLAGS=-race UNIT_TESTS_TIMEOUT=1200s
-```
-
 ## Common Issues & Workarounds
 
 ### Build Issues
@@ -197,17 +187,16 @@ make test UNIT_TEST_RACE_FLAGS=-race UNIT_TESTS_TIMEOUT=1200s
 
 3. **Integration test binary:** Must build integration test binary explicitly with `make build-integration-test-binary` before running integration tests.
 
-4. **Provider tests require environment:** Provider tests need KOPIA_PROVIDER_TEST=true and rclone binary available.
+4. **Provider tests require environment:** Provider tests need KOPIA_PROVIDER_TEST=true and storage credentials.
 
 ### Environment Variables
 
 **Important variables for CI/tests:**
 - `UNIX_SHELL_ON_WINDOWS=true` - Required for Windows builds
 - `KOPIA_COVERAGE_TEST=1` - Enable coverage testing
 - `KOPIA_INTEGRATION_EXE` - Path to integration test binary
-- `TESTING_ACTION_EXE` - Path to testing action binary
 - `KOPIA_PROVIDER_TEST=true` - Enable provider tests
-- `RCLONE_EXE` - Path to rclone binary for provider tests
+
 
 ## Project Structure
 
@@ -270,9 +259,8 @@ make test UNIT_TEST_RACE_FLAGS=-race UNIT_TESTS_TIMEOUT=1200s
 ### Configuration Files
 
 - `.golangci.yml` - Linter config with 40+ enabled linters, custom rules
-- `.codecov.yml` - Code coverage reporting config
-- `.goreleaser.yml` - Release automation config
 - `.github/workflows/*.yml` - GitHub Actions workflows (19 workflow files)
+- `.codecov.yml` - Code coverage reporting config
 
 ## GitHub Actions Workflows
 
@@ -408,4 +396,7 @@ make test UNIT_TEST_RACE_FLAGS=-race UNIT_TESTS_TIMEOUT=1200s
    - node - JavaScript runtime for app builds
    - hugo - Static site generator for website
 
-10. **Trust these instructions** - These instructions have been validated by running all commands. Only search for additional information if something fails or if these instructions are incomplete or incorrect.
+10. Do not commit executables or binary artifacts to the git repository.
+    Do not modify `.gitignore` files.
+
+11. **Trust these instructions** - These instructions have been validated by running all commands. Only search for additional information if something fails or if these instructions are incomplete or incorrect.
PATCH

echo "Gold patch applied."
