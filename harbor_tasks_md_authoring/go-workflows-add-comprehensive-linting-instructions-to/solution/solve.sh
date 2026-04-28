#!/usr/bin/env bash
set -euo pipefail

cd /workspace/go-workflows

# Idempotency guard
if grep -qF "The project uses golangci-lint v2 with a custom analyzer plugin for workflow cod" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -36,17 +36,49 @@ go test -timeout 120s -race -count 1 -v ./... 2>&1 | go-junit-report -set-exit-c
 ```
 
 ### Linting
+
+The project uses golangci-lint v2 with a custom analyzer plugin for workflow code validation. There are multiple ways to run the linter:
+
+#### Recommended: Using Makefile (Preferred)
 ```bash
-# Install golangci-lint
-go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
+# Run the full linter suite with custom analyzer - Takes ~12-15 seconds.
+make lint
+```
 
-# Build custom analyzer plugin - Takes ~8 seconds.
-go build -tags analyzerplugin -buildmode=plugin analyzer/plugin/plugin.go
+This will:
+- Check if golangci-lint is installed
+- Build the custom analyzer plugin
+- Run all configured linters from `.golangci.yml`
+
+#### Manual Setup
+If you need to install golangci-lint or run it manually:
+
+```bash
+# Install golangci-lint v2 (required for this project)
+go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.4.0
 
-# Run basic linting (custom analyzer has version conflicts) - Takes ~12 seconds.
-~/go/bin/golangci-lint run --disable-all --enable=gofmt,govet,ineffassign,misspell --timeout=5m
+# Run the full linter configuration - Takes ~12-15 seconds.
+golangci-lint run --timeout=5m
 ```
 
+**Note:** The project uses golangci-lint v2.4.0 configuration. Version v1.x will not work with the `.golangci.yml` configuration file.
+
+#### Workaround: Basic Linting (When Custom Analyzer Has Issues)
+If the custom analyzer has version compatibility issues:
+
+```bash
+# Run basic linting without custom analyzer - Takes ~12 seconds.
+golangci-lint run --disable-all --enable=gofmt,govet,ineffassign,misspell --timeout=5m
+```
+
+#### Available Linters
+The `.golangci.yml` configuration enables multiple linters including:
+- **Code Quality**: staticcheck, unused, ineffassign, wastedassign
+- **Bug Detection**: govet, makezero, prealloc, predeclared
+- **Style & Formatting**: gofmt, whitespace, tagalign
+- **Testing**: testifylint, tparallel
+- **Custom**: goworkflows (workflow-specific validation, currently commented out)
+
 ### Sample Applications
 ```bash
 # Simple workflow example with Redis backend (default)
@@ -94,8 +126,9 @@ Run these validation steps before committing changes:
 
 1. **Full Build:** `go build -v ./...` - Must complete without errors
 2. **Short Tests:** `go test -short -timeout 120s -race -count 1 -v ./...` - Should pass (1 known non-critical test failure in tester package)
-3. **Sample Execution:** At least one sample must run successfully
-4. **Basic Linting:** Check for obvious issues with basic linters
+3. **Linting:** `make lint` or `golangci-lint run --timeout=5m` - Should pass with no new violations
+4. **Code Formatting:** `make fmt` - Ensure code is properly formatted
+5. **Sample Execution:** At least one sample must run successfully
 
 ### Manual Testing Scenarios
 Execute these scenarios to verify workflow functionality:
PATCH

echo "Gold patch applied."
