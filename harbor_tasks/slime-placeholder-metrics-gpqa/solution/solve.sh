#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/slime"
cd "$REPO"

# Idempotency: check if GPQA already has 10 letters
if grep -q 'ascii_uppercase\[:10\]' slime/rollout/rm_hub/gpqa.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index 33b988eee6..c422db53a9 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -49,7 +49,7 @@ class ServerGroup:
     all_engines: list
     num_gpus_per_engine: int
     num_new_engines: int
-    worker_type: str = "regular"  # "regular", "prefill", or "decode"
+    worker_type: str = "regular"  # "regular", "prefill", "decode", or "placeholder"
     rank_offset: int = 0  # cumulative engine count before this group
     gpu_offset: int = 0  # cumulative GPU count before this group
     sglang_overrides: dict = dataclasses.field(default_factory=dict)
@@ -260,7 +260,7 @@ def engine_gpu_offsets(self) -> list[int]:
     @property
     def nodes_per_engine(self):
         """Nodes per engine.  Only valid when all active groups share the same value."""
-        values = {g.nodes_per_engine for g in self.server_groups}
+        values = {g.nodes_per_engine for g in self.server_groups if g.worker_type != "placeholder"}
         if len(values) != 1:
             raise ValueError(f"Heterogeneous nodes_per_engine across groups: {values}")
         return values.pop()
@@ -355,8 +355,6 @@ def __init__(self, args, pg):
         self.pg = pg
         self.args = args

-        init_tracking(args, primary=False)
-
         data_source_cls = load_function(self.args.data_source_path)
         self.data_source = data_source_cls(args)

@@ -378,6 +376,11 @@ def __init__(self, args, pg):
         else:
             init_http_client(args)
             self.servers = start_rollout_servers(args, pg)
+
+        # Initialize W&B secondary *after* servers are launched so the router
+        # address is available for scraping SGLang Prometheus metrics.
+        router_addr = self._get_metrics_router_addr()
+        init_tracking(args, primary=False, router_addr=router_addr)
         self.rollout_engine_lock = Lock.options(num_cpus=1, num_gpus=0).remote()
         self.rollout_id = -1

@@ -390,6 +393,30 @@ def __init__(self, args, pg):
                     self._health_monitors.append(monitor)
             self._ci_fault_injection_pending = self.args.ci_test  # Flag for CI fault injection

+    def _get_metrics_router_addr(self) -> str | None:
+        """Return the router address for scraping SGLang engine metrics.
+
+        The sglang_router gateway exposes ``/engine_metrics`` on its main port,
+        which aggregates Prometheus metrics from all backend sglang servers.
+        Returns ``http://{ip}:{port}`` for the first server, or ``None`` when
+        metrics are disabled or no servers are running.
+
+        Note: the ``use_slime_router`` path does not expose ``/engine_metrics``;
+        metrics forwarding to W&B requires the sglang_router gateway.
+        """
+        if not getattr(self.args, "sglang_enable_metrics", False):
+            return None
+        if getattr(self.args, "use_slime_router", False):
+            logger.warning(
+                "SGLang metrics forwarding to W&B is not supported with --use-slime-router. "
+                "Use the default sglang_router gateway for /engine_metrics aggregation."
+            )
+            return None
+        srv = self.server
+        if srv is None or srv.router_ip is None:
+            return None
+        return f"http://{srv.router_ip}:{srv.router_port}"
+
     def _try_ci_fault_injection(self):
         """Try to inject fault during generate (when health monitor is running)."""
         if not self._ci_fault_injection_pending:
diff --git a/slime/rollout/rm_hub/gpqa.py b/slime/rollout/rm_hub/gpqa.py
index df2e3c0b91..affb7a22ad 100644
--- a/slime/rollout/rm_hub/gpqa.py
+++ b/slime/rollout/rm_hub/gpqa.py
@@ -2,7 +2,7 @@
 import string
 from collections.abc import Iterable

-DEFAULT_VALID_LETTERS = list(string.ascii_uppercase[:8])
+DEFAULT_VALID_LETTERS = list(string.ascii_uppercase[:10])


 def _strip_chain_of_thought(text: str) -> str:
diff --git a/slime/router/router.py b/slime/router/router.py
index bde130b037..05f1b989ae 100644
--- a/slime/router/router.py
+++ b/slime/router/router.py
@@ -20,6 +20,7 @@ class WorkerType(str, Enum):
     REGULAR = "regular"
     PREFILL = "prefill"
     DECODE = "decode"
+    PLACEHOLDER = "placeholder"


 class WorkerInfo:

PATCH

echo "Patch applied successfully."
