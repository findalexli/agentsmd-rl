#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied
if grep -q '"--soft-watchdog-timeout"' test/registered/8-gpu-models/test_ring_2_5_1t.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/test/registered/8-gpu-models/test_ring_2_5_1t.py b/test/registered/8-gpu-models/test_ring_2_5_1t.py
index 71b2a4f2609e..29c64160cf96 100644
--- a/test/registered/8-gpu-models/test_ring_2_5_1t.py
+++ b/test/registered/8-gpu-models/test_ring_2_5_1t.py
@@ -5,8 +5,7 @@ from sglang.test.accuracy_test_runner import AccuracyTestParams
 from sglang.test.run_combined_tests import run_combined_tests
 from sglang.test.test_utils import ModelLaunchSettings

-# register_cuda_ci(est_time=1000, suite="nightly-8-gpu-common", nightly=True)
-register_cuda_ci(est_time=1000, suite="stage-c-test-8-gpu-h200")
+register_cuda_ci(est_time=1800, suite="nightly-8-gpu-common", nightly=True)

 RING_2_5_1T_MODEL_PATH = "inclusionAI/Ring-2.5-1T"

@@ -25,6 +24,8 @@ class TestRing2_5_1T(unittest.TestCase):
             '{"enable_multithread_load": true, "num_threads": 64}',
             "--watchdog-timeout",
             "1800",
+            "--soft-watchdog-timeout",
+            "1800",
         ]

         variants = [

PATCH

echo "Patch applied successfully."
