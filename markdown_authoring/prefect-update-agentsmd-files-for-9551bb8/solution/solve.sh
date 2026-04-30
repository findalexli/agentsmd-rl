#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "`Runner.add_flow()` explicitly assigns `deployment.work_pool_name = None` and `d" "src/prefect/runner/AGENTS.md" && grep -qF "- **`update_deployment` uses `model_fields_set` to distinguish explicit `None` f" "src/prefect/server/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/runner/AGENTS.md b/src/prefect/runner/AGENTS.md
@@ -65,6 +65,10 @@ This ordering is a hard constraint. Getting it wrong causes ClosedResourceError
 
 Each execution mode has a ProcessStarter implementation. To add a new execution mode, implement the ProcessStarter protocol and inject it into FlowRunExecutor -- do not add a new code path to Runner.
 
+## Work Pool Clearing in `add_flow`
+
+`Runner.add_flow()` explicitly assigns `deployment.work_pool_name = None` and `deployment.work_queue_name = None` *after* the `RunnerDeployment` is constructed, not via constructor kwargs. This is intentional: post-construction assignment adds the fields to Pydantic's `model_fields_set`, which `server/models/deployments.py:update_deployment` checks to detect "explicitly cleared" vs. "not provided." Constructing with `work_pool_name=None` in kwargs does *not* trigger clearing — `RunnerDeployment` factory methods now omit `None`-valued work pool fields from the constructor. If you ever need another field to signal "clear this on the server side," follow the same post-construction-assignment pattern.
+
 ## Storage Base Path Scoping
 
 `$STORAGE_BASE_PATH` in `deployment.path` comes from `RunnerDeployment.from_storage()`. For work-pool deployments, `path` is set to `None` on create and storage is serialized into `pull_steps` instead (`deployments/runner.py:407-413`). `load_flow_from_flow_run()` only does `$STORAGE_BASE_PATH` substitution when `pull_steps` is absent (`flows.py:3084`). So the CLI `prefect flow-run execute` path (worker-based, always has `pull_steps`) does not need `tmp_dir` / `PREFECT__STORAGE_BASE_PATH`. Only Runner-served deployments (no work pool) use this substitution.
diff --git a/src/prefect/server/AGENTS.md b/src/prefect/server/AGENTS.md
@@ -39,6 +39,8 @@ alembic_revision("description")      # Create a new migration
 
 - **Pydantic v2 treats null JSON fields as explicitly set.** When a worker sends a state update with `field: null`, Pydantic v2 sets that field to `None`, silently overwriting any existing value. To preserve `state_details` fields across transitions (e.g. `deployment_concurrency_lease_id`), add a `FlowRunUniversalTransform` to `CoreFlowPolicy` that copies the field forward when the proposed state has `None`. See `PreserveDeploymentConcurrencyLeaseId` in `orchestration/core_policy.py` as the canonical pattern. Any new field added to `state_details` that workers may omit faces this same risk.
 
+- **`update_deployment` uses `model_fields_set` to distinguish explicit `None` from "not provided" for `work_pool_name`.** In `models/deployments.py`, when `deployment.work_pool_name is None` AND `"work_pool_name" in deployment.model_fields_set`, the work queue association is cleared (`work_queue_id = None`). If `work_pool_name` is simply absent from `model_fields_set`, the existing work pool association is left intact. This is the intentional counterpart to the Pydantic v2 null-overwrite pitfall above — here the explicit `model_fields_set` entry signals *desired* clearing. `RunnerDeployment` factory methods omit `None`-valued work pool fields from constructor kwargs; `Runner.add_flow()` then post-assigns `None` to opt into clearing. Follow this same pattern for any future field that should distinguish "clear it" from "leave it alone."
+
 ## Main Subsystems
 
 - `api/` — FastAPI REST endpoints
PATCH

echo "Gold patch applied."
