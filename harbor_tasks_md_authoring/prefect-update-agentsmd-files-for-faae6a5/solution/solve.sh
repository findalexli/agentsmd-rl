#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "`ScheduledRunPoller` now calls `propose_pending` (Scheduled \u2192 Pending) before ha" "src/prefect/runner/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/runner/AGENTS.md b/src/prefect/runner/AGENTS.md
@@ -18,6 +18,7 @@ Thin facade over single-responsibility extracted classes. New behavior belongs i
 | DeploymentRegistry | _deployment_registry.py | Deployment/flow/storage/bundle maps |
 | ScheduledRunPoller | _scheduled_run_poller.py | Poll loop, run discovery, scheduling |
 | ProcessStarter (protocol) | _flow_run_executor.py | Strategy interface for starting processes |
+| FlowRunExecutorContext | _flow_run_executor.py | Async context manager for one-shot execution outside Runner (CLI, bundles) |
 | DirectSubprocessStarter | _starter_direct.py | Runs Flow object via run_flow_in_subprocess |
 | EngineCommandStarter | _starter_engine.py | Spawns `python -m prefect.engine` subprocess |
 | BundleExecutionStarter | _starter_bundle.py | Executes serialized bundle in SpawnProcess |
@@ -37,9 +38,11 @@ Thin facade over single-responsibility extracted classes. New behavior belongs i
 - `_flow_run_process_map` dict -- replaced by ProcessManager
 - `_kill_process()` -- replaced by ProcessManager.kill()
 - `_run_on_crashed_hooks()` / `_run_on_cancellation_hooks()` -- replaced by HookRunner
-- `execute_bundle()`'s inline lifecycle -- should use FlowRunExecutor with BundleExecutionStarter
+- `execute_flow_run()` -- deprecated (Mar 2026); use `FlowRunExecutorContext` + `EngineCommandStarter`
+- `execute_bundle()` -- deprecated (Mar 2026); use `execute_bundle()` from `prefect._experimental.bundles.execute`
+- `reschedule_current_flow_runs()` -- deprecated (Mar 2026); SIGTERM rescheduling is now handled inline by the CLI execute path
 
-These will be removed once internal callers (notably ProcessWorker) are migrated.
+These will be removed once internal callers (notably ProcessWorker) are migrated. ProcessWorker currently suppresses the deprecation warnings via `warnings.catch_warnings()`.
 
 ## AsyncExitStack LIFO Ordering
 
@@ -62,9 +65,13 @@ Each execution mode has a ProcessStarter implementation. To add a new execution
 
 `$STORAGE_BASE_PATH` in `deployment.path` comes from `RunnerDeployment.from_storage()`. For work-pool deployments, `path` is set to `None` on create and storage is serialized into `pull_steps` instead (`deployments/runner.py:407-413`). `load_flow_from_flow_run()` only does `$STORAGE_BASE_PATH` substitution when `pull_steps` is absent (`flows.py:3084`). So the CLI `prefect flow-run execute` path (worker-based, always has `pull_steps`) does not need `tmp_dir` / `PREFECT__STORAGE_BASE_PATH`. Only Runner-served deployments (no work pool) use this substitution.
 
+## State Transition Split (ScheduledRunPoller vs FlowRunExecutor)
+
+`ScheduledRunPoller` now calls `propose_pending` (Scheduled → Pending) before handing off to `FlowRunExecutor`. `FlowRunExecutor` then calls `propose_submitting` (Pending → Submitting sub-state) as step 1 of its lifecycle. These are two separate transitions — do not collapse them. The split exists so automations listening for the Pending state fire correctly before the executor begins.
+
 ## ProcessWorker Migration (Known Gap)
 
-ProcessWorker (src/prefect/workers/process.py) calls `Runner.execute_flow_run()`, which uses the legacy `_submit_run_and_capture_errors` -> `_run_process` path. It bypasses FlowRunExecutor, ProcessManager, and ProcessStarter entirely. This is a known migration target.
+ProcessWorker (src/prefect/workers/process.py) calls `Runner.execute_flow_run()` and `Runner.execute_bundle()` via the deprecated path, suppressing `PrefectDeprecationWarning` with `warnings.catch_warnings()`. It bypasses FlowRunExecutor, ProcessManager, and ProcessStarter entirely. This is a known migration target.
 
 ## Reference
 
PATCH

echo "Gold patch applied."
