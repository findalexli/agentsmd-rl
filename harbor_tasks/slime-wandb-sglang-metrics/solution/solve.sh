#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

if grep -q "reinit_wandb_primary_with_open_metrics" slime/utils/wandb_utils.py 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index b3f85508a..a584e7e29 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -378,10 +378,7 @@ def __init__(self, args, pg):
             init_http_client(args)
             self.servers = start_rollout_servers(args, pg)
 
-        # Initialize W&B secondary *after* servers are launched so the router
-        # address is available for scraping SGLang Prometheus metrics.
-        router_addr = self._get_metrics_router_addr()
-        init_tracking(args, primary=False, router_addr=router_addr)
+        init_tracking(args, primary=False)
         self.rollout_engine_lock = Lock.options(num_cpus=1, num_gpus=0).remote()
         self.rollout_id = -1
 
@@ -416,6 +413,10 @@ def _get_metrics_router_addr(self) -> str | None:
             return None
         return f"http://{srv.router_ip}:{srv.router_port}"
 
+    def get_metrics_router_addr(self) -> str | None:
+        """Public wrapper for remote calls from the driver process."""
+        return self._get_metrics_router_addr()
+
     def _try_ci_fault_injection(self):
         """Try to inject fault during generate (when health monitor is running)."""
         if not self._ci_fault_injection_pending:
PATCH
