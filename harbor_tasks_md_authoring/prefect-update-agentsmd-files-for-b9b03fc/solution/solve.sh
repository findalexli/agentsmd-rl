#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "- `workers/` \u2192 Work-pool-based execution layer: polls for flow runs, dispatches " "src/prefect/AGENTS.md" && grep -qF "- `ProcessWorker` calls the deprecated `Runner.execute_flow_run()` / `Runner.exe" "src/prefect/workers/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/AGENTS.md b/src/prefect/AGENTS.md
@@ -50,5 +50,6 @@ Use `get_logger()` from `prefect.logging` instead of raw `logging.getLogger()` 
 - `deployments/` → YAML-driven deployment lifecycle: project init, build/push/pull steps, and triggering remote flow runs (see deployments/AGENTS.md)
 - `utilities/` → Cross-cutting helpers: async utils, schema hydration, callables introspection, and more (see utilities/AGENTS.md)
 - `blocks/` → Server-persisted configuration objects for external service credentials and settings (see blocks/AGENTS.md)
+- `workers/` → Work-pool-based execution layer: polls for flow runs, dispatches to infrastructure (see workers/AGENTS.md)
 - `docker/` → `DockerImage` class for building and pushing Docker images during deployment
 - `telemetry/` → OS-level resource metric collection and run telemetry
diff --git a/src/prefect/workers/AGENTS.md b/src/prefect/workers/AGENTS.md
@@ -0,0 +1,42 @@
+# Workers
+
+Work-pool-based execution layer that polls for flow runs and submits them to infrastructure.
+
+## Purpose & Scope
+
+Workers are long-running processes that pull scheduled flow runs from a work pool and dispatch them to infrastructure (processes, Docker, Kubernetes, cloud VMs, etc.). Each worker type subclasses `BaseWorker` and provides a `BaseJobConfiguration` subclass plus a `run()` method.
+
+This module does NOT manage the Runner execution model (no work pool) — see `runner/AGENTS.md` for that.
+
+## Key Classes
+
+- `BaseWorker` — abstract base; handles heartbeating, polling, cancellation, and attribution env vars
+- `BaseJobConfiguration` — Pydantic model for per-run infrastructure config; `prepare_for_flow_run()` stamps attribution variables into `env`
+- `ProcessWorker` (`process.py`) — runs flow runs as local subprocesses via `Runner.execute_bundle()`
+- `BaseWorkerResult` — result returned by `run()`; wraps infrastructure status codes
+
+## Attribution Env Vars
+
+Workers stamp two env vars into `os.environ` for their own process, so all API requests include attribution headers:
+
+- `PREFECT__WORKER_NAME` — set in `setup()` immediately
+- `PREFECT__WORKER_ID` — set in `sync_with_backend()` after the first successful heartbeat returns a backend ID
+
+**Teardown guard**: `teardown()` only removes these vars if they still match the current worker instance (`os.environ.get("PREFECT__WORKER_NAME") == self.name`). This prevents a second worker sharing the same process from having its vars cleared.
+
+These are separate from the per-flow-run attribution vars injected into the child process environment by `prepare_for_flow_run(worker_name=..., worker_id=...)`.
+
+## Anti-Patterns
+
+- Do not set `PREFECT__WORKER_NAME` / `PREFECT__WORKER_ID` in `os.environ` from outside `BaseWorker` — setup/teardown own this lifecycle.
+- Do not call `prepare_for_flow_run()` without passing `worker_name` and `worker_id` — omitting them silently drops attribution from child-process API requests.
+
+## Pitfalls
+
+- `backend_id` is `None` until the first heartbeat succeeds; `PREFECT__WORKER_ID` is not set until then. Code that reads `self.backend_id` early in the lifecycle may get `None`.
+- `ProcessWorker` calls the deprecated `Runner.execute_flow_run()` / `Runner.execute_bundle()` paths (suppressing `PrefectDeprecationWarning` with `warnings.catch_warnings()`). It bypasses `FlowRunExecutor` and `ProcessStarter` — this is a known migration gap (see `runner/AGENTS.md`).
+
+## Related
+
+- `runner/AGENTS.md` — Runner execution model (no work pool, local deployments)
+- `src/prefect/client/AGENTS.md` — attribution headers set from these env vars
PATCH

echo "Gold patch applied."
