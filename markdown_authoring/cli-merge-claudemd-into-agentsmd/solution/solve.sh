#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "This is the Databricks CLI, a command-line interface for interacting with Databr" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,14 +1,79 @@
-Below are some general AI assistant coding rules.
+This file provides guidance to AI assistants when working with code in this repository.
 
-# General
+# Project Overview
 
-When moving code from one place to another, please don't unnecessarily change
-the code or omit parts.
+This is the Databricks CLI, a command-line interface for interacting with Databricks workspaces and managing Databricks Assets Bundles (DABs). The project is written in Go and follows a modular architecture.
 
-# Style and comments
+# General Rules
 
-Please make sure code that you author is consistent with the codebase
-and concise.
+When moving code from one place to another, please don't unnecessarily change the code or omit parts.
+
+# Development Commands
+
+### Building and Testing
+- `make build` - Build the CLI binary
+- `make test` - Run unit tests for all packages
+- `go test ./acceptance -run TestAccept/bundle/<path>/<to>/<folder> -tail -test.v` - run a single acceptance test
+- `make integration` - Run integration tests (requires environment variables)
+- `make cover` - Generate test coverage reports
+
+### Code Quality
+- `make lint` - Run linter on changed files only (uses lintdiff.py)
+- `make lintfull` - Run full linter with fixes (golangci-lint)
+- `make ws` - Run whitespace linter
+- `make fmt` - Format code (Go, Python, YAML)
+- `make checks` - Run quick checks (tidy, whitespace, links)
+
+### Specialized Commands
+- `make schema` - Generate bundle JSON schema
+- `make docs` - Generate bundle documentation
+- `make generate` - Generate CLI code from OpenAPI spec (requires universe repo)
+
+### Git Commands
+Use "git rm" to remove and "git mv" to rename files instead of directly modifying files on FS.
+
+If asked to rebase, always prefix each git command with appropriate settings so that it never launches interactive editor.
+GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true VISUAL=true GIT_PAGER=cat git fetch origin main &&
+GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true VISUAL=true GIT_PAGER=cat git rebase origin/main
+
+# Architecture
+
+### Core Components
+
+**cmd/** - CLI command structure using Cobra framework
+- `cmd/cmd.go` - Main command setup and subcommand registration
+- `cmd/bundle/` - Bundle-related commands (deploy, validate, etc.)
+- `cmd/workspace/` - Workspace API commands (auto-generated)
+- `cmd/account/` - Account-level API commands (auto-generated)
+
+**bundle/** - Core bundle functionality for Databricks Asset Bundles
+- `bundle/bundle.go` - Main Bundle struct and lifecycle management
+- `bundle/config/` - Configuration loading, validation, and schema
+- `bundle/deploy/` - Deployment logic (Terraform and direct modes)
+- `bundle/mutator/` - Configuration transformation pipeline
+- `bundle/phases/` - High-level deployment phases
+
+**libs/** - Shared libraries and utilities
+- `libs/dyn/` - Dynamic configuration value manipulation
+- `libs/filer/` - File system abstraction (local, DBFS, workspace)
+- `libs/auth/` - Databricks authentication handling
+- `libs/sync/` - File synchronization between local and remote
+
+### Key Concepts
+
+**Bundles**: Configuration-driven deployments of Databricks resources (jobs, pipelines, etc.). The bundle system uses a mutator pattern where each transformation is a separate, testable component.
+
+**Mutators**: Transform bundle configuration through a pipeline. Located in `bundle/config/mutator/` and `bundle/mutator/`. Each mutator implements the `Mutator` interface.
+
+**Direct vs Terraform Deployment**: The CLI supports two deployment modes controlled by `DATABRICKS_CLI_DEPLOYMENT` environment variable:
+- `terraform` (default) - Uses Terraform for resource management
+- `direct` - Direct API calls without Terraform
+
+# Code Style and Patterns
+
+## Go
+
+Please make sure code that you author is consistent with the codebase and concise.
 
 The code should be self-documenting based on the code and function names.
 
@@ -30,17 +95,12 @@ Use modern idiomatic Golang features (version 1.24+). Specifically:
  - Use builtin min() and max() where possible (works on any type and any number of values).
  - Do not capture the for-range variable, since go 1.22 a new copy of the variable is created for each loop iteration.
 
-# Commands
-
-Use "git rm" to remove and "git mv" to rename files instead of directly modifying files on FS.
-
-Do not run “go test ./..." in the root folder as that will start long running integration tests. To test the whole project run "go build && make lint test" in root directory. However, prefer running tests for specific packages instead.
-
-If asked to rebase, always prefix each git command with appropriate settings so that it never launches interactive editor.
-GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true VISUAL=true GIT_PAGER=cat git fetch origin main &&
-GIT_EDITOR=true GIT_SEQUENCE_EDITOR=true VISUAL=true GIT_PAGER=cat git rebase origin/main
+### Configuration Patterns
+- Bundle config uses `dyn.Value` for dynamic typing
+- Config loading supports includes, variable interpolation, and target overrides
+- Schema generation is automated from Go struct tags
 
-# Python
+## Python
 
 When writing Python scripts, we bias for conciseness. We think of Python in this code base as scripts.
  - use Python 3.11
@@ -51,7 +111,12 @@ When writing Python scripts, we bias for conciseness. We think of Python in this
  - After done, format you code with "ruff format -n <path>"
  - Use "#!/usr/bin/env python3" shebang.
 
-# Tests
+# Testing
+
+### Test Types
+- **Unit tests**: Standard Go tests alongside source files
+- **Integration tests**: `integration/` directory, requires live Databricks workspace
+- **Acceptance tests**: `acceptance/` directory, uses mock HTTP server
 
 Each file like process_target_mode_test.go should have a corresponding test file
 like process_target_mode_test.go. If you add new functionality to a file,
@@ -82,7 +147,40 @@ Notice that:
 When writing tests, please don't include an explanation in each
 test case in your responses. I am just interested in the tests.
 
-# databricks_template_schema.json
+### Acceptance Tests
+- Located in `acceptance/` with nested directory structure
+- Each test directory contains `databricks.yml`, `script`, and `output.txt`
+- Run with `go test ./acceptance -run TestAccept/bundle/<path>/<to>/<folder> -tail -test.v`
+- Use `-update` flag to regenerate expected output files
+- When you see the test fails because it has an old output, just run it one more time with an `-update` flag instead of changing the `output.txt` directly
+
+# Logging
+
+Use the following for logging:
+
+```
+import "github.com/databricks/cli/libs/log"
+
+log.Infof(ctx, "...")
+log.Debugf(ctx, "...")
+log.Warnf(ctx, "...")
+log.Errorf(ctx, "...")
+```
+
+Note that the 'ctx' variable here is something that should be passed in as
+an argument by the caller. We should not use context.Background() like we do in tests.
+
+Use cmdio.LogString to print to stdout:
+
+```
+import "github.com/databricks/cli/libs/cmdio"
+
+cmdio.LogString(ctx, "...")
+```
+
+# Specific File Guides
+
+## databricks_template_schema.json
 
 A databricks_template_schema.json file is used to configure bundle templates.
 
@@ -151,26 +249,9 @@ Notice that:
 - Helpers such as {{default_catalog}} and {{short_name}} can be used within property descriptors.
 - Properties can be referenced in messages and descriptions using {{.property_name}}. {{.project_name}} is an example.
 
-# Logging and output to the terminal
-
-Use the following for logging:
-
-```
-import "github.com/databricks/cli/libs/log"
-
-log.Infof(ctx, "...")
-log.Debugf(ctx, "...")
-log.Warnf(ctx, "...")
-log.Errorf(ctx, "...")
-```
+# Development Tips
 
-Note that the 'ctx' variable here is something that should be passed in as
-an argument by the caller. We should not use context.Background() like we do in tests.
-
-Use cmdio.LogString to print to stdout:
-
-```
-import "github.com/databricks/cli/libs/cmdio"
-
-cmdio.LogString(ctx, "...")
-```
+- Run `make checks fmt lint` before committing
+- Use `make test-update` to regenerate acceptance test outputs after changes
+- The CLI binary supports both `databricks` and `pipelines` command modes based on executable name
+- Resource definitions in `bundle/config/resources/` are auto-generated from OpenAPI specs
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,89 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-
-This is the Databricks CLI, a command-line interface for interacting with Databricks workspaces and managing Databricks Assets Bundles (DABs). The project is written in Go and follows a modular architecture.
-
-## Development Commands
-
-### Building and Testing
-- `make build` - Build the CLI binary
-- `make test` - Run unit tests for all packages
-- `go test ./acceptance -run TestAccept/bundle/<path>/<to>/<folder> -tail -test.v` - run a single acceptance test
-- `make integration` - Run integration tests (requires environment variables)
-- `make cover` - Generate test coverage reports
-
-### Code Quality
-- `make lint` - Run linter on changed files only (uses lintdiff.py)
-- `make lintfull` - Run full linter with fixes (golangci-lint)
-- `make ws` - Run whitespace linter
-- `make fmt` - Format code (Go, Python, YAML)
-- `make checks` - Run quick checks (tidy, whitespace, links)
-
-### Specialized Commands
-- `make schema` - Generate bundle JSON schema
-- `make docs` - Generate bundle documentation
-- `make generate` - Generate CLI code from OpenAPI spec (requires universe repo)
-
-## Architecture
-
-### Core Components
-
-**cmd/** - CLI command structure using Cobra framework
-- `cmd/cmd.go` - Main command setup and subcommand registration
-- `cmd/bundle/` - Bundle-related commands (deploy, validate, etc.)
-- `cmd/workspace/` - Workspace API commands (auto-generated)
-- `cmd/account/` - Account-level API commands (auto-generated)
-
-**bundle/** - Core bundle functionality for Databricks Asset Bundles
-- `bundle/bundle.go` - Main Bundle struct and lifecycle management
-- `bundle/config/` - Configuration loading, validation, and schema
-- `bundle/deploy/` - Deployment logic (Terraform and direct modes)
-- `bundle/mutator/` - Configuration transformation pipeline
-- `bundle/phases/` - High-level deployment phases
-
-**libs/** - Shared libraries and utilities
-- `libs/dyn/` - Dynamic configuration value manipulation
-- `libs/filer/` - File system abstraction (local, DBFS, workspace)
-- `libs/auth/` - Databricks authentication handling
-- `libs/sync/` - File synchronization between local and remote
-
-### Key Concepts
-
-**Bundles**: Configuration-driven deployments of Databricks resources (jobs, pipelines, etc.). The bundle system uses a mutator pattern where each transformation is a separate, testable component.
-
-**Mutators**: Transform bundle configuration through a pipeline. Located in `bundle/config/mutator/` and `bundle/mutator/`. Each mutator implements the `Mutator` interface.
-
-**Direct vs Terraform Deployment**: The CLI supports two deployment modes controlled by `DATABRICKS_CLI_DEPLOYMENT` environment variable:
-- `terraform` (default) - Uses Terraform for resource management
-- `direct` - Direct API calls without Terraform
-
-## Testing
-
-### Test Types
-- **Unit tests**: Standard Go tests alongside source files
-- **Integration tests**: `integration/` directory, requires live Databricks workspace
-- **Acceptance tests**: `acceptance/` directory, uses mock HTTP server
-
-### Acceptance Tests
-- Located in `acceptance/` with nested directory structure
-- Each test directory contains `databricks.yml`, `script`, and `output.txt`
-- Run with `go test ./acceptance -run TestAccept/bundle/<path>/<to>/<folder> -tail -test.v`
-- Use `-update` flag to regenerate expected output files
-- When you see the test fails because it has an old output, just run it one more time with an `-update` flag instead of changing the `output.txt` directly
-
-## Code Patterns
-
-### Configuration
-- Bundle config uses `dyn.Value` for dynamic typing
-- Config loading supports includes, variable interpolation, and target overrides
-- Schema generation is automated from Go struct tags
-
-## Development Tips
-
-- Run `make checks fmt lint` before committing
-- Use `make test-update` to regenerate acceptance test outputs after changes
-- The CLI binary supports both `databricks` and `pipelines` command modes based on executable name
-- Resource definitions in `bundle/config/resources/` are auto-generated from OpenAPI specs
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
