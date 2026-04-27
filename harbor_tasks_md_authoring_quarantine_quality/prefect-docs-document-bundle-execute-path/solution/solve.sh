#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "**Two callers set `propose_submitting=False`** via `FlowRunExecutorContext.creat" "src/prefect/runner/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/runner/AGENTS.md b/src/prefect/runner/AGENTS.md
@@ -96,7 +96,11 @@ Each execution mode has a ProcessStarter implementation. To add a new execution
 
 `ScheduledRunPoller` now calls `propose_pending` (Scheduled → Pending) before handing off to `FlowRunExecutor`. `FlowRunExecutor` then calls `propose_submitting` (Pending → Submitting sub-state) as step 1 of its lifecycle **when `propose_submitting=True` (the default)**. These are two separate transitions — do not collapse them. The split exists so automations listening for the Pending state fire correctly before the executor begins.
 
-**Exception: `prefect flow-run execute` CLI path sets `propose_submitting=False`** via `FlowRunExecutorContext.create_executor(propose_submitting=False)`. The CLI is invoked by a worker that has already advanced the flow run past the Pending state, so proposing Submitting again would be wrong. The cancelling precheck (step 1a) still runs unconditionally even when `propose_submitting=False`.
+**Two callers set `propose_submitting=False`** via `FlowRunExecutorContext.create_executor(propose_submitting=False)` — both have already advanced the flow run past the Pending state, so proposing Submitting again would be wrong:
+- `prefect flow-run execute` CLI path (invoked by a worker)
+- `execute_bundle()` in `prefect._experimental.bundles.execute` (invoked by bundle dispatch)
+
+The cancelling precheck (step 1a) still runs unconditionally even when `propose_submitting=False`.
 
 ## ProcessWorker Migration (Known Gap)
 
PATCH

echo "Gold patch applied."
