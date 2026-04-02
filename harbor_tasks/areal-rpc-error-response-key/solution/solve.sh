#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

# Idempotent: skip if already applied (check if rpc_server.py /configure uses "error" not "detail")
if ! grep -q '"detail"' areal/infra/rpc/rpc_server.py 2>/dev/null; then
    exit 0
fi

git apply - <<'PATCH'
diff --git a/areal/infra/rpc/rpc_server.py b/areal/infra/rpc/rpc_server.py
index 0fb84cef5..7d5298dae 100644
--- a/areal/infra/rpc/rpc_server.py
+++ b/areal/infra/rpc/rpc_server.py
@@ -431,15 +431,15 @@ def configure():
     try:
         data = request.get_json()
         if data is None:
-            return jsonify({"detail": "Invalid JSON in request body"}), 400
+            return jsonify({"error": "Invalid JSON in request body"}), 400

         config = data.get("config")
         if config is None:
-            return jsonify({"detail": "Missing 'config' field in request"}), 400
+            return jsonify({"error": "Missing 'config' field in request"}), 400

         rank = data.get("rank")
         if rank is None:
-            return jsonify({"detail": "Missing 'rank' field in request"}), 400
+            return jsonify({"error": "Missing 'rank' field in request"}), 400

         config = deserialize_value(config)
         config: BaseExperimentConfig
diff --git a/areal/infra/scheduler/local.py b/areal/infra/scheduler/local.py
index f74bb6c2a..0dd1f5474 100644
--- a/areal/infra/scheduler/local.py
+++ b/areal/infra/scheduler/local.py
@@ -866,10 +866,10 @@ def _configure_worker(self, worker_info: WorkerInfo, worker_rank: int):
                 logger.info(f"Configuration successfully on worker '{worker_id}'")
                 return
             elif response.status_code == 400:
-                error_detail = response.json().get("detail", "Unknown error")
+                error_detail = response.json().get("error", "Unknown error")
                 raise WorkerConfigurationError(worker_id, error_detail, str(400))
             elif response.status_code == 500:
-                error_detail = response.json().get("detail", "Unknown error")
+                error_detail = response.json().get("error", "Unknown error")
                 raise WorkerConfigurationError(worker_id, error_detail, str(500))
             else:
                 raise WorkerConfigurationError(
@@ -1118,7 +1118,7 @@ async def create_engine(
                     elif response.status == 400:
                         # Import error or bad request
                         error_detail = (await response.json()).get(
-                            "detail", "Unknown error"
+                            "error", "Unknown error"
                         )
                         if "Failed to import" in error_detail:
                             raise EngineImportError(engine, error_detail)
@@ -1127,7 +1127,7 @@ async def create_engine(
                     elif response.status == 500:
                         # Engine initialization failed
                         error_detail = (await response.json()).get(
-                            "detail", "Unknown error"
+                            "error", "Unknown error"
                         )
                         raise EngineCreationError(worker_id, error_detail, 500)
                     else:
@@ -1399,7 +1399,7 @@ async def async_call_engine(
                         elif response.status == 400:
                             # Bad request (e.g., method doesn't exist) - don't retry
                             error_detail = (await response.json()).get(
-                                "detail", "Unknown error"
+                                "error", "Unknown error"
                             )
                             raise EngineCallError(
                                 worker_id, method, error_detail, attempt
@@ -1407,7 +1407,7 @@ async def async_call_engine(
                         elif response.status == 500:
                             # Engine method failed - don't retry
                             error_detail = (await response.json()).get(
-                                "detail", "Unknown error"
+                                "error", "Unknown error"
                             )
                             raise EngineCallError(
                                 worker_id, method, error_detail, attempt
@@ -1492,11 +1492,11 @@ def _handle_call_response(
             return deserialized_result, False, None
         elif response.status_code == 400:
             # Bad request (e.g., method doesn't exist) - don't retry
-            error_detail = response.json().get("detail", "Unknown error")
+            error_detail = response.json().get("error", "Unknown error")
             raise EngineCallError(worker_id, method, error_detail, attempt)
         elif response.status_code == 500:
             # Engine method failed - don't retry
-            error_detail = response.json().get("detail", "Unknown error")
+            error_detail = response.json().get("error", "Unknown error")
             raise EngineCallError(worker_id, method, error_detail, attempt)
         elif response.status_code == 503:
             # Service unavailable - retry
diff --git a/areal/infra/scheduler/slurm.py b/areal/infra/scheduler/slurm.py
index 4bf516547..e2d1b296d 100644
--- a/areal/infra/scheduler/slurm.py
+++ b/areal/infra/scheduler/slurm.py
@@ -309,10 +309,10 @@ def _configure_worker(self, worker_info: SlurmWorkerInfo, worker_rank: int) -> N
                 logger.info(f"Configuration successful on worker '{worker_id}'")
                 return
             elif response.status_code == 400:
-                error_detail = response.json().get("detail", "Unknown error")
+                error_detail = response.json().get("error", "Unknown error")
                 raise WorkerConfigurationError(worker_id, error_detail, str(400))
             elif response.status_code == 500:
-                error_detail = response.json().get("detail", "Unknown error")
+                error_detail = response.json().get("error", "Unknown error")
                 raise WorkerConfigurationError(worker_id, error_detail, str(500))
             else:
                 raise WorkerConfigurationError(
@@ -1329,7 +1329,7 @@ async def create_engine(
                         return result.get("result")
                     elif response.status == 400:
                         error_detail = (await response.json()).get(
-                            "detail", "Unknown error"
+                            "error", "Unknown error"
                         )
                         if "Failed to import" in error_detail:
                             raise EngineImportError(engine, error_detail)
@@ -1337,7 +1337,7 @@ async def create_engine(
                             raise EngineCreationError(worker_id, error_detail, 400)
                     elif response.status == 500:
                         error_detail = (await response.json()).get(
-                            "detail", "Unknown error"
+                            "error", "Unknown error"
                         )
                         raise EngineCreationError(worker_id, error_detail, 500)
                     else:
@@ -1439,7 +1439,7 @@ def call_engine(
                     result = response.json()
                     return deserialize_value(result.get("result"))
                 elif response.status_code == 500:
-                    error_detail = response.json().get("detail", "Unknown error")
+                    error_detail = response.json().get("error", "Unknown error")
                     # Check if retryable
                     if attempt < max_retries and "timeout" in error_detail.lower():
                         last_error = f"Engine method timeout: {error_detail}"
@@ -1457,7 +1457,7 @@ def call_engine(
                         f"Worker temporarily unavailable, retry {attempt}/{max_retries}"
                     )
                 else:
-                    error_detail = response.json().get("detail", "Unknown error")
+                    error_detail = response.json().get("error", "Unknown error")
                     raise EngineCallError(
                         worker_id,
                         method,
@@ -1580,7 +1580,7 @@ async def async_call_engine(
                             return deserialize_value(result.get("result"))
                         elif response.status == 500:
                             error_detail = (await response.json()).get(
-                                "detail", "Unknown error"
+                                "error", "Unknown error"
                             )
                             if (
                                 attempt < max_retries
@@ -1601,7 +1601,7 @@ async def async_call_engine(
                             )
                         else:
                             error_detail = (await response.json()).get(
-                                "detail", "Unknown error"
+                                "error", "Unknown error"
                             )
                             raise EngineCallError(
                                 worker_id,

PATCH
