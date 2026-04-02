#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotency check: if slime_router_pd_disaggregation is already referenced, patch is applied
if grep -q 'slime_router_pd_disaggregation' slime/ray/rollout.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/ray/rollout.py b/slime/ray/rollout.py
index 7ea0d12b56..86ecb9064c 100644
--- a/slime/ray/rollout.py
+++ b/slime/ray/rollout.py
@@ -907,7 +907,6 @@ def _start_router(args, *, has_pd_disaggregation: bool = False, force_new: bool
             router_port = find_available_port(random.randint(3000, 4000))

     if args.use_slime_router:
-        assert not has_pd_disaggregation, "slime router does not support PD disaggregation."
         import copy

         from slime.router.router import run_router
@@ -915,6 +914,8 @@ def _start_router(args, *, has_pd_disaggregation: bool = False, force_new: bool
         router_args = copy.copy(args)
         router_args.sglang_router_ip = router_ip
         router_args.sglang_router_port = router_port
+        if has_pd_disaggregation:
+            router_args.slime_router_pd_disaggregation = True

     else:
         from sglang_router.launch_router import RouterArgs
@@ -930,6 +931,10 @@ def _start_router(args, *, has_pd_disaggregation: bool = False, force_new: bool

         if has_pd_disaggregation:
             router_args.pd_disaggregation = True
+            # Disable circuit breaker to prevent RDMA transfer timeouts from
+            # marking decode workers as dead. Timeouts are transient (PCIe
+            # contention under high load) and do not indicate a dead server.
+            router_args.disable_circuit_breaker = True

         logger.info(f"Launch router with args: {router_args}")

PATCH

echo "Patch applied successfully."
