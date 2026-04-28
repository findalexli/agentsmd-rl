#!/usr/bin/env bash
set -euo pipefail

cd /workspace/risingwave

# Idempotency guard
if grep -qF ".cursor/rules/coding-style.mdc" ".cursor/rules/coding-style.mdc" && grep -qF ".github/copilot-instructions.md" ".github/copilot-instructions.md" && grep -qF "RisingWave is a Postgres-compatible streaming database that offers the simplest " "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/coding-style.mdc b/.cursor/rules/coding-style.mdc
@@ -1,10 +0,0 @@
----
-description:
-globs:
-alwaysApply: true
----
-# Coding Style
-
-- Always write code comments in English.
-- Write simple, easy-to-read and easy-to-maintain code.
-- Use `cargo fmt` to format the code if needed.
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,109 +0,0 @@
-# GitHub Copilot Instructions for RisingWave
-
-This file provides guidance to GitHub Copilot when working with code in this repository.
-
-## Project Overview
-
-RisingWave is a Postgres-compatible streaming database that offers the simplest and most cost-effective way to process, analyze, and manage real-time event data — with built-in support for the Apache Iceberg™ open table format.
-
-## Code Architecture
-
-RisingWave components are developed in Rust and split into several crates:
-
-1. `config` - Default configurations for servers
-2. `prost` - Generated protobuf rust code (grpc and message definitions)
-3. `stream` - Stream compute engine
-4. `batch` - Batch compute engine for queries against materialized views
-5. `frontend` - SQL query planner and scheduler
-6. `storage` - Cloud native storage engine
-7. `meta` - Meta engine
-8. `utils` - Independent util crates
-9. `cmd` - All binaries, `cmd_all` contains the all-in-one binary `risingwave`
-10. `risedevtool` - Developer tool for RisingWave
-
-## Build, Run, Test
-
-When implementing features or fixing bugs, use these commands:
-
-- `./risedev b` - Build the project
-- `./risedev c` - Check code follows rust-clippy rules and coding styles
-- `./risedev d` - Run a RisingWave instance (builds if needed, runs in background)
-- `./risedev k` - Stop a RisingWave instance started by `./risedev d`
-- `./risedev psql -c "<your query>"` - Run SQL queries in RisingWave
-- `./risedev slt './path/to/e2e-test-file.slt'` - Run end-to-end SLT tests
-- Log files are in `.risingwave/log` folder - use `tail` to check them
-
-### Testing
-
-- Preferred testing format is SQLLogicTest (SLT)
-- Tests are located in `./e2e_test` folder
-- Integration and unit tests follow standard Rust/Tokio patterns
-- The `./risedev` command is safe to run automatically
-- Never run `git` mutation commands unless explicitly requested
-
-## Coding Style
-
-- Always write code comments in English
-- Write simple, easy-to-read and maintainable code
-- Use `cargo fmt` to format code when needed
-- Follow existing code patterns and conventions in the repository
-
-## Understanding RisingWave Macros
-
-RisingWave uses many macros to simplify development:
-
-- Use `cargo expand` to expand macros and understand generated code
-- Setup `rust-analyzer` in your editor to expand macros interactively
-- This is the preferred method for understanding code interactively
-
-### Example: Using cargo expand
-```bash
-cargo expand -p risingwave_meta > meta.rs
-cargo expand -p risingwave_expr > expr.rs
-```
-
-## Connector Development
-
-RisingWave supports many connectors (sources and sinks). Key principles:
-
-- **Environment-independent**: Easy to start cluster and run tests locally and in CI
-- **Self-contained tests**: Straightforward to run individual test cases
-- Don't use hard-coded configurations (e.g., `localhost:9092`)
-- Don't write complex logic in `ci/scripts` - keep CI scripts thin
-
-### Development Workflow
-1. Use RiseDev to manage external systems (Kafka, MySQL, etc.)
-2. Write profiles in `risedev.yml` or `risedev-profiles.user.yml`
-3. Use `risedev d my-profile` to start cluster with external systems
-4. Write e2e tests in SLT format using `system ok` commands for external interaction
-5. Use environment variables for configuration (e.g., `${RISEDEV_KAFKA_WITH_OPTIONS_COMMON}`)
-
-## Key Development Guidelines
-
-1. **Minimal Changes**: Make the smallest possible changes to achieve goals
-2. **Validation**: Always validate changes don't break existing behavior
-3. **Testing**: Run existing linters, builds, and tests before making changes
-4. **Documentation**: Update documentation when directly related to changes
-5. **Ecosystem Tools**: Use existing tools (npm, cargo, etc.) to automate tasks
-
-## Environment Setup
-
-- RisingWave uses S3 as primary storage for high performance and fast recovery
-- Supports elastic disk cache for performance optimization
-- Native Apache Iceberg™ integration for open table format compatibility
-- PostgreSQL wire protocol compatibility for seamless integration
-
-## Common Use Cases
-
-- Streaming analytics with sub-second data freshness
-- Event-driven applications for monitoring and alerting
-- Real-time data enrichment and delivery
-- Feature engineering for machine learning models
-
----
-
-For more detailed information, refer to:
-- Project README.md
-- Documentation in `docs/` directory
-- Source code documentation in `src/README.md`
-- Connector development guide in `docs/dev/src/connector/intro.md`
\ No newline at end of file
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,50 +1,70 @@
----
-description:
-globs:
-alwaysApply: true
----
-# Build, Run, Test
+# Coding Agent Instructions for RisingWave
+
+## Project Overview
+
+RisingWave is a Postgres-compatible streaming database that offers the simplest and most cost-effective way to process, analyze, and manage real-time event data — with built-in support for the Apache Iceberg™ open table format.
+
+RisingWave components are developed in Rust and split into several crates:
+
+1. `config` - Default configurations for servers
+2. `prost` - Generated protobuf rust code (grpc and message definitions)
+3. `stream` - Stream compute engine
+4. `batch` - Batch compute engine for queries against materialized views
+5. `frontend` - SQL query planner and scheduler
+6. `storage` - Cloud native storage engine
+7. `meta` - Meta engine
+8. `utils` - Independent util crates
+9. `cmd` - All binaries, `cmd_all` contains the all-in-one binary `risingwave`
+10. `risedevtool` - Developer tool for RisingWave
+
+## Coding Style
+
+- Always write code comments in English.
+- Write simple, easy-to-read and easy-to-maintain code.
+- Use `cargo fmt` to format the code if needed.
+- Follow existing code patterns and conventions in the repository.
+
+## Build, Run, Test
 
 You may need to learn how to build and test RisingWave when implementing features or fixing bugs.
 
-## Build & Check
+### Build & Check
 
 - Use `./risedev b` to build the project.
 - Use `./risedev c` to check if the code follow rust-clippy rules, coding styles, etc.
 
-## Unit Test
+### Unit Test
 
 - Integration tests and unit tests are valid Rust/Tokio tests, you can locate and run those related in a standard Rust way.
 - Parser tests: use `./risedev update-parser-test` to regenerate expected output.
 - Planner tests: use `./risedev run-planner-test [name]` to run and `./risedev do-apply-planner-test` (or `./risedev dapt`) to update expected output.
 
-## End-to-End Test
+### End-to-End Test
 
 - Use `./risedev d` to run a RisingWave instance in the background via tmux.
-  * It builds RisingWave binaries if necessary. The build process can take up to 10 minutes, depending on the incremental build results. Use a large timeout for this step, and be patient.
-  * It kills the previous instance, if exists.
-  * Optionally pass a profile name (see `risedev.yml`) to choose external services or components. By default it uses `default`.
-  * This runs in the background so you do not need a separate terminal.
-  * You can connect right after the command finishes.
-  * Logs are written to files in `.risingwave/log` folder.
+  - It builds RisingWave binaries if necessary. The build process can take up to 10 minutes, depending on the incremental build results. Use a large timeout for this step, and be patient.
+  - It kills the previous instance, if exists.
+  - Optionally pass a profile name (see `risedev.yml`) to choose external services or components. By default it uses `default`.
+  - This runs in the background so you do not need a separate terminal.
+  - You can connect right after the command finishes.
+  - Logs are written to files in `.risingwave/log` folder.
 - Use `./risedev k` to stop a RisingWave instance started by `./risedev d`.
 - Only when a RisingWave instance is running, you can use `./risedev psql -c "<your query>"` to run SQL queries in RW.
 - Only when a RisingWave instance is running, you can use `./risedev slt './path/to/e2e-test-file.slt'` to run end-to-end SLT tests.
-  * File globs like `/**/*.slt` is allowed.
-  * Failed run may leave some objects in the database that interfere with next run. Use `./risedev slt-clean ./path/to/e2e-test-file.slt` to reset the database before running tests.
+  - File globs like `/**/*.slt` is allowed.
+  - Failed run may leave some objects in the database that interfere with next run. Use `./risedev slt-clean ./path/to/e2e-test-file.slt` to reset the database before running tests.
 - The preferred way to write tests is to write tests in SQLLogicTest format.
 - Tests are put in `./e2e_test` folder.
 
-## Misc
-
-- `./risedev` command is safe to run automatically.
-- Never run `git` mutation command (`git add`, `git rebase`, `git commit`, `git push`, etc) unless user explicitly asks for it.
-
-## Sandbox escalation
+### Sandbox escalation
 
 When sandboxing is enabled, these commands need `require_escalated` because they bind or connect to local TCP sockets:
 
 - `./risedev d` and `./risedev p` (uses local ports and tmux sockets)
 - `./risedev psql ...` or direct `psql -h localhost -p 4566 ...` (local TCP connection)
 - `./risedev slt './path/to/e2e-test-file.slt'` (connects to local TCP via psql protocol)
 - Any command that checks running services via local TCP (for example, health checks or custom SQL clients)
+
+## Connector Development
+
+See `docs/dev/src/connector/intro.md`.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,18 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code when working with code in this repository.
-
-## Project Overview
-
-RisingWave is a Postgres-compatible streaming database.
-
-## Code Architecture
-
-@src/README.md
-
-## Build, Run, Test
-
-@.cursor/rules/build-run-test.mdc
-
-### Develop Connectors
-@docs/dev/src/connector/intro.md
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
