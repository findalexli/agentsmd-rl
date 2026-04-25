#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (files already moved to test/manual/)
if [ -f "test/manual/test_qwen3_235b.py" ]; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch: move files from test/registered/8-gpu-models/ to test/manual/
# and remove register_cuda_ci() calls
git apply - <<'PATCH'
diff --git a/test/registered/8-gpu-models/test_deepseek_v31.py b/test/manual/test_deepseek_v31.py
similarity index 92%
rename from test/registered/8-gpu-models/test_deepseek_v31.py
rename to test/manual/test_deepseek_v31.py
index b6cc7e5c471e..8025e47c4e2b 100644
--- a/test/registered/8-gpu-models/test_deepseek_v31.py
+++ b/test/manual/test_deepseek_v31.py
@@ -1,14 +1,10 @@
 import unittest

 from sglang.test.accuracy_test_runner import AccuracyTestParams
-from sglang.test.ci.ci_register import register_cuda_ci
 from sglang.test.performance_test_runner import PerformanceTestParams
 from sglang.test.run_combined_tests import run_combined_tests
 from sglang.test.test_utils import ModelLaunchSettings

-# Runs on both H200 and B200 via nightly-8-gpu-common suite
-register_cuda_ci(est_time=5400, suite="nightly-8-gpu-common", nightly=True)
-
 DEEPSEEK_V31_MODEL_PATH = "deepseek-ai/DeepSeek-V3.1"


diff --git a/test/registered/8-gpu-models/test_glm_46_fp8.py b/test/manual/test_glm_46_fp8.py
similarity index 90%
rename from test/registered/8-gpu-models/test_glm_46_fp8.py
rename to test/manual/test_glm_46_fp8.py
index 435763e01447..94fb724b75b8 100644
--- a/test/registered/8-gpu-models/test_glm_46_fp8.py
+++ b/test/manual/test_glm_46_fp8.py
@@ -1,14 +1,10 @@
 import unittest

 from sglang.test.accuracy_test_runner import AccuracyTestParams
-from sglang.test.ci.ci_register import register_cuda_ci
 from sglang.test.performance_test_runner import PerformanceTestParams
 from sglang.test.run_combined_tests import run_combined_tests
 from sglang.test.test_utils import ModelLaunchSettings

-# Runs on both H200 and B200 via nightly-8-gpu-common suite
-register_cuda_ci(est_time=1800, suite="nightly-8-gpu-common", nightly=True)
-
 GLM_4_6_FP8_MODEL_PATH = "zai-org/GLM-4.6-FP8"


diff --git a/test/registered/8-gpu-models/test_qwen3_235b.py b/test/manual/test_qwen3_235b.py
similarity index 94%
rename from test/registered/8-gpu-models/test_qwen3_235b.py
rename to test/manual/test_qwen3_235b.py
index 70420bbed64a..f0e4f03996ce 100644
--- a/test/registered/8-gpu-models/test_qwen3_235b.py
+++ b/test/manual/test_qwen3_235b.py
@@ -1,14 +1,10 @@
 import unittest

 from sglang.test.accuracy_test_runner import AccuracyTestParams
-from sglang.test.ci.ci_register import register_cuda_ci
 from sglang.test.performance_test_runner import PerformanceTestParams
 from sglang.test.run_combined_tests import run_combined_tests
 from sglang.test.test_utils import ModelLaunchSettings, is_blackwell_system

-# Runs on both H200 and B200 via nightly-8-gpu-common suite
-register_cuda_ci(est_time=1800, suite="nightly-8-gpu-common", nightly=True)
-
 QWEN3_235B_FP8_MODEL_PATH = "Qwen/Qwen3-235B-A22B-Instruct-2507-FP8"
 QWEN3_235B_EAGLE3_MODEL_PATH = (
     "lmsys/SGLang-EAGLE3-Qwen3-235B-A22B-Instruct-2507-SpecForge-Meituan"

PATCH

echo "Patch applied successfully."
