#!/bin/bash
set -e

cd /workspace/sglang

# Idempotency check: already applied
if grep -q 'api": "nemo-skills"' python/sglang/test/accuracy_test_runner.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply gold patch
patch -p1 <<'PATCH'
diff --git a/python/sglang/test/accuracy_test_runner.py b/python/sglang/test/accuracy_test_runner.py
index c35dba6497b4..ac9da2382099 100644
--- a/python/sglang/test/accuracy_test_runner.py
+++ b/python/sglang/test/accuracy_test_runner.py
@@ -8,6 +8,7 @@
     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
     DEFAULT_URL_FOR_TEST,
     ModelLaunchSettings,
+    dump_metric,
     popen_launch_server,
     write_github_step_summary,
 )
@@ -421,6 +422,12 @@ def _run_nemo_skills_eval(
         if score is None:
             return False, "Could not parse accuracy from ns eval output", None

+        dump_metric(
+            f"{dataset}_score",
+            score,
+            labels={"model": model.model_path, "eval": dataset, "api": "nemo-skills"},
+        )
+
         return True, None, {"score": score}

     except subprocess.TimeoutExpired:
diff --git a/python/sglang/test/kits/lm_eval_kit.py b/python/sglang/test/kits/lm_eval_kit.py
index e2c1f2249570..5a96c5816c28 100644
--- a/python/sglang/test/kits/lm_eval_kit.py
+++ b/python/sglang/test/kits/lm_eval_kit.py
@@ -12,6 +12,8 @@
 import requests
 import yaml

+from sglang.test.test_utils import dump_metric
+

 @contextmanager
 def scoped_env_vars(new_env: dict[str, str] | None):
@@ -69,6 +71,15 @@ def test_lm_eval(self):
                     f"ground_truth={ground_truth:.3f} | "
                     f"measured={measured_value:.3f} | rtol={rtol}"
                 )
+                dump_metric(
+                    f"{task['name']}_{metric['name']}",
+                    measured_value,
+                    labels={
+                        "model": eval_config.get("model_name", ""),
+                        "eval": "lm-eval",
+                        "task": task["name"],
+                    },
+                )
                 success = success and np.isclose(
                     ground_truth, measured_value, rtol=rtol
                 )
diff --git a/python/sglang/test/kits/mmmu_vlm_kit.py b/python/sglang/test/kits/mmmu_vlm_kit.py
index cb4e5fceaa5b..61ea70804652 100644
--- a/python/sglang/test/kits/mmmu_vlm_kit.py
+++ b/python/sglang/test/kits/mmmu_vlm_kit.py
@@ -13,6 +13,7 @@
     DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
     DEFAULT_URL_FOR_TEST,
     CustomTestCase,
+    dump_metric,
     popen_launch_server,
 )

@@ -216,6 +217,12 @@ def test_mmmu(self: CustomTestCase):
             mmmu_accuracy = result["results"]["mmmu_val"]["mmmu_acc,none"]
             print(f"Model {self.model} achieved accuracy: {mmmu_accuracy:.4f}")

+            dump_metric(
+                "mmmu_score",
+                mmmu_accuracy,
+                labels={"model": self.model, "eval": "mmmu", "api": "lmms-eval"},
+            )
+
             # Assert performance meets expected threshold
             self.assertGreaterEqual(
                 mmmu_accuracy,
@@ -403,6 +410,12 @@ def _run_vlm_mmmu_test(
                 f"Model {model.model} achieved accuracy{test_name}: {mmmu_accuracy:.4f}"
             )

+            dump_metric(
+                "mmmu_score",
+                mmmu_accuracy,
+                labels={"model": model.model, "eval": "mmmu", "api": "lmms-eval"},
+            )
+
             # Capture server output if requested
             if capture_output and process:
                 server_output = self._read_output_from_files()
PATCH

echo "Patch applied successfully"
