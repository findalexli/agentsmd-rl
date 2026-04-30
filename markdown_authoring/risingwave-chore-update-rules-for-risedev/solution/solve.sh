#!/usr/bin/env bash
set -euo pipefail

cd /workspace/risingwave

# Idempotency guard
if grep -qF "* Failed run may leave some objects in the database that interfere with next run" ".cursor/rules/build-run-test.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/build-run-test.mdc b/.cursor/rules/build-run-test.mdc
@@ -7,19 +7,43 @@ alwaysApply: true
 
 You may need to learn how to build and test RisingWave when implementing features or fixing bugs.
 
+## Build & Check
+
 - Use `./risedev b` to build the project.
 - Use `./risedev c` to check if the code follow rust-clippy rules, coding styles, etc.
-- Use `./risedev d` to run a RisingWave instance. If the project is not built, this will build the project before running. The instance will run in background, so you don't need to start a new terminal to run this command. You can connect to the instance right after this command is finished. When you see errors like
-  `psql: error: connection to server at "127.0.0.1", port 4566 failed: Connection refused`, just rerun `./risedev d` to start the instance.
+
+## Unit Test
+
+- Integration tests and unit tests are valid Rust/Tokio tests, you can locate and run those related in a standard Rust way.
+- Parser tests: use `./risedev update-parser-test` to regenerate expected output.
+- Planner tests: use `./risedev run-planner-test [name]` to run and `./risedev do-apply-planner-test` (or `./risedev dapt`) to update expected output.
+
+## End-to-End Test
+
+- Use `./risedev d` to run a RisingWave instance in the background via tmux.
+  * It builds first if needed, and kills the previous instance if exists.
+  * Optionally pass a profile name (see `risedev.yml`) to choose external services or components. By default it uses `default`.
+  * This runs in the background so you do not need a separate terminal.
+  * You can connect right after the command finishes.
+  * Logs are written to files in `.risingwave/log` folder.
 - Use `./risedev k` to stop a RisingWave instance started by `./risedev d`.
-- The log files of a running RisingWave are located in `.risingwave/log` folder in the workspace. You can check them (`tail` is suggested because they can be quite long) if things go wrong.
 - When a RisingWave instance is running, you can use `./risedev psql -c "<your query>"` to run SQL queries in RW.
-- When a RisingWave instance is running, you can use `./risedev slt './path/to/e2e-test-file.slt'` to run end-to-end SLT tests. File globs like `/**/*.slt` is allowed.
-- Integration tests and unit tests are valid Rust/Tokio tests, you can locate and run those related in a standard Rust way.
+- When a RisingWave instance is running, you can use `./risedev slt './path/to/e2e-test-file.slt'` to run end-to-end SLT tests.
+  * File globs like `/**/*.slt` is allowed.
+  * Failed run may leave some objects in the database that interfere with next run. Use `./risedev slt-clean ./path/to/e2e-test-file.slt` to reset the database before running tests.
+- The preferred way to write tests is to write tests in SQLLogicTest format.
+- Tests are put in `./e2e_test` folder.
+
+## Misc
+
 - `./risedev` command is safe to run automatically.
 - Never run `git` mutation command (`git add`, `git rebase`, `git commit`, `git push`, etc) unless user explicitly asks for it.
 
-## Testing
+## Sandbox escalation
+
+When sandboxing is enabled, these commands need `require_escalated` because they bind or connect to local TCP sockets:
 
-The preferred way to write tests is to write tests in SQLLogicTest format.
-Tests are put in `./e2e_test` folder.
+- `./risedev d` and `./risedev p` (uses local ports and tmux sockets)
+- `./risedev psql ...` or direct `psql -h localhost -p 4566 ...` (local TCP connection)
+- `./risedev slt './path/to/e2e-test-file.slt'` (connects to local TCP via psql protocol)
+- Any command that checks running services via local TCP (for example, health checks or custom SQL clients)
PATCH

echo "Gold patch applied."
