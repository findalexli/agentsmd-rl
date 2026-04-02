#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency: check if fix is already applied
if grep -q "Only get .tests_hub., which means" utils/tests_fetcher.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/utils/tests_fetcher.py b/utils/tests_fetcher.py
index 8c8fd685f80a..c47143bd0564 100644
--- a/utils/tests_fetcher.py
+++ b/utils/tests_fetcher.py
@@ -1106,16 +1106,29 @@ def parse_commit_message(commit_message: str) -> dict[str, bool]:
 def create_test_list_from_filter(full_test_list, out_path):
     os.makedirs(out_path, exist_ok=True)
     all_test_files = "\n".join(full_test_list)
+
+    # Collect info: job_name, file_name and files_to_test, so we can process after the loop
+    to_output = []
     for job_name, _filter in JOB_TO_TEST_FILE.items():
         file_name = os.path.join(out_path, f"{job_name}_test_list.txt")
         if job_name == "tests_hub":
             files_to_test = ["tests"]
         else:
             files_to_test = list(re.findall(_filter, all_test_files))
-        print(job_name, file_name)
+
+        print(job_name, file_name, len(files_to_test))
+
         if len(files_to_test) > 0:  # No tests -> no file with test list
-            with open(file_name, "w") as f:
-                f.write("\n".join(files_to_test))
+            to_output.append((job_name, file_name, files_to_test))
+
+    # Only get `tests_hub`, which means we have 0 test file for all other jobs --> No job at all to run.
+    if len(to_output) == 1:
+        print("No test file found for any job, skipping `tests_hub` as well.")
+        to_output = []
+
+    for _, file_name, files_to_test in to_output:
+        with open(file_name, "w") as f:
+            f.write("\n".join(files_to_test))


 if __name__ == "__main__":

PATCH

echo "Patch applied successfully."
