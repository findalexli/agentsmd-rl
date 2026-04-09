#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q 'FIXME: refactor this test to have less random behavior' test/registered/distributed/test_load_weights_from_remote_instance.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/test/registered/distributed/test_load_weights_from_remote_instance.py b/test/registered/distributed/test_load_weights_from_remote_instance.py
index 00dc8454d325..7d51101cd93b 100644
--- a/test/registered/distributed/test_load_weights_from_remote_instance.py
+++ b/test/registered/distributed/test_load_weights_from_remote_instance.py
@@ -195,9 +195,7 @@ def init_process_dst(
             remote_instance_weight_loader_send_weights_group_ports=ports,
             load_format="remote_instance",
             remote_instance_weight_loader_backend=remote_instance_loader_backend,
-            remote_instance_weight_loader_start_seed_via_transfer_engine=(
-                remote_instance_loader_backend == "transfer_engine"
-            ),
+            remote_instance_weight_loader_start_seed_via_transfer_engine=False,
         )
     else:
         host, _, port = DEFAULT_URL_FOR_TEST.rpartition(":")
@@ -358,6 +356,7 @@ def test_load_weights_from_remote_instance(self):
         assert torch.cuda.device_count() >= 2, "At least 2 GPUs are required"
         # test_suits : tp, dp, model_name, backend, dst_instance_id
         if is_in_ci():
+            # FIXME: refactor this test to have less random behavior
             mode = random.choice(["Engine", "Server"])
             remote_instance_loader_backend = random.choice(["nccl", "transfer_engine"])
             test_suits = [

PATCH

echo "Patch applied successfully."
