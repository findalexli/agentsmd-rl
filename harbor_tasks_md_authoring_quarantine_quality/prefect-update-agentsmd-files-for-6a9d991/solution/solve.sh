#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- **`directories`** entries starting with `--` trigger a `UserWarning` but are n" "src/prefect/runner/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/runner/AGENTS.md b/src/prefect/runner/AGENTS.md
@@ -77,6 +77,15 @@ Each execution mode has a ProcessStarter implementation. To add a new execution
 
 ProcessWorker (src/prefect/workers/process.py) calls `Runner.execute_flow_run()` and `Runner.execute_bundle()` via the deprecated path, suppressing `PrefectDeprecationWarning` with `warnings.catch_warnings()`. It bypasses FlowRunExecutor, ProcessManager, and ProcessStarter entirely. This is a known migration target.
 
+## GitRepository Input Validation
+
+`GitRepository.__init__` (storage.py) enforces two non-obvious constraints:
+
+- **`commit_sha`** must match `^[0-9a-fA-F]{4,64}$` — any value that fails (including git option strings like `--upload-pack=...`) raises `ValueError`. Branch/tag names must use the `branch` parameter instead.
+- **`directories`** entries starting with `--` trigger a `UserWarning` but are not rejected. The values are passed to `git sparse-checkout set --` (with a `--` separator to prevent flag injection). The warning exists because such paths are unusual; legitimate use is allowed.
+
+These validations exist to prevent git argument injection. Do not bypass them when constructing `GitRepository` programmatically.
+
 ## Reference
 
 Full refactor design and rationale: plans/completed/2026-02-18-runner-refactor.md
PATCH

echo "Gold patch applied."
