#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if defaultdict is already imported, patch is applied
if grep -q 'from collections import defaultdict' utils/check_bad_commit.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Strip trailing whitespace so patch context lines match exactly
sed -i 's/[[:space:]]*$//' .github/workflows/check_failed_tests.yml

git apply - <<'PATCH'
diff --git a/.github/workflows/check_failed_tests.yml b/.github/workflows/check_failed_tests.yml
index 1c77aa0f292c..b8209157b122 100644
--- a/.github/workflows/check_failed_tests.yml
+++ b/.github/workflows/check_failed_tests.yml
@@ -24,6 +24,10 @@ on:
       pr_number:
         required: false
         type: string
+      max_num_runners:
+        required: false
+        type: number
+        default: 4
     outputs:
       is_check_failures_ok:
         description: "Whether the failure checking infrastructure succeeded"
@@ -43,15 +47,82 @@ env:


 jobs:
+  setup_check_new_failures:
+    name: "Setup matrix for finding commits"
+    runs-on: ubuntu-22.04
+    outputs:
+      matrix: ${{ steps.set-matrix.outputs.matrix }}
+      n_runners: ${{ steps.set-matrix.outputs.n_runners }}
+      process: ${{ steps.set-matrix.outputs.process }}
+    steps:
+      - uses: actions/download-artifact@v4
+        continue-on-error: true
+        with:
+          name: ci_results_${{ inputs.job }}
+          path: ci_results_${{ inputs.job }}
+
+      - name: Set matrix
+        id: set-matrix
+        env:
+          job: ${{ inputs.job }}
+          max_num_runners: ${{ inputs.max_num_runners }}
+        run: |
+          python3 - << 'EOF'
+          import json, os, math
+
+          print("Script started")
+
+          job = os.environ["job"]
+          filepath = f"ci_results_{job}/new_failures.json"
+
+          print(f"Looking for file: {filepath}")
+          print(f"File exists: {os.path.isfile(filepath)}")
+
+          if not os.path.isfile(filepath):
+              print("File not found, setting process=false")
+              with open(os.environ["GITHUB_OUTPUT"], "a") as f:
+                  f.write("process=false\n")
+              exit(0)
+
+          with open(filepath) as f:
+              reports = json.load(f)
+
+          print(f"Loaded reports with {len(reports)} models")
+
+          n_tests = sum(
+              len(model_data.get("failures", model_data).get("single-gpu", []))
+              for model_data in reports.values()
+          )
+
+          print(f"n_tests: {n_tests}")
+
+          max_num_runners = int(os.environ["max_num_runners"])
+
+          TESTS_PER_RUNNER = 10
+          n_runners = max(1, min(max_num_runners, math.ceil(n_tests / TESTS_PER_RUNNER)))
+
+          print(f"n_runners: {n_runners}")
+
+          with open(os.environ["GITHUB_OUTPUT"], "a") as f:
+              f.write(f"matrix={json.dumps(list(range(n_runners)))}\n")
+              f.write(f"n_runners={n_runners}\n")
+              f.write("process=true\n")
+
+          print("Done")
+          EOF
+
+
   check_new_failures:
     name: "Find commits for new failing tests"
+    needs: setup_check_new_failures
+    if: needs.setup_check_new_failures.outputs.process == 'true'
     strategy:
       matrix:
-        run_idx: [1]
+        run_idx: ${{ fromJson(needs.setup_check_new_failures.outputs.matrix) }}
     runs-on:
       group: aws-g5-4xlarge-cache
     outputs:
-      process: ${{ steps.check_file.outputs.process }}
+      process: ${{ needs.setup_check_new_failures.outputs.process }}
     container:
       image: ${{ inputs.docker }}
       options: --gpus all --shm-size "16gb" --ipc host -v /mnt/cache/.cache/huggingface:/mnt/cache/
@@ -61,31 +132,13 @@ jobs:
           name: ci_results_${{ inputs.job }}
           path: /transformers/ci_results_${{ inputs.job }}

-      - name: Check file
-        id: check_file
-        working-directory: /transformers
-        env:
-          job: ${{ inputs.job }}
-        run: |
-          if [ -f "ci_results_${job}/new_failures.json" ]; then
-            echo "\`ci_results_${job}/new_failures.json\` exists, continue ..."
-            echo "process=true" >> $GITHUB_ENV
-            echo "process=true" >> $GITHUB_OUTPUT
-          else
-            echo "\`ci_results_${job}/new_failures.json\` doesn't exist, abort."
-            echo "process=false" >> $GITHUB_ENV
-            echo "process=false" >> $GITHUB_OUTPUT
-          fi
-
       - uses: actions/download-artifact@v4
-        if: ${{ env.process == 'true' }}
         with:
           pattern: setup_values*
           path: setup_values
           merge-multiple: true

       - name: Prepare some setup values
-        if: ${{ env.process == 'true' }}
         run: |
           if [ -f setup_values/prev_workflow_run_id.txt ]; then
             echo "PREV_WORKFLOW_RUN_ID=$(cat setup_values/prev_workflow_run_id.txt)" >> $GITHUB_ENV
@@ -95,7 +148,6 @@ jobs:

       - name: Update clone
         working-directory: /transformers
-        if: ${{ env.process == 'true' }}
         env:
           commit_sha: ${{ inputs.commit_sha || github.sha }}
         run: |
@@ -103,7 +155,6 @@ jobs:

       - name: Get `START_SHA`
         working-directory: /transformers/utils
-        if: ${{ env.process == 'true' }}
         env:
           commit_sha: ${{ inputs.commit_sha || github.sha }}
         run: |
@@ -112,7 +163,7 @@ jobs:
       # This is used if the CI is triggered from a pull request `self-comment-ci.yml` (after security check is verified)
       - name: Extract the base commit on `main` (of the merge commit created by Github) if it is a PR
         id: pr_info
-        if: ${{ env.process == 'true' && inputs.pr_number != '' }}
+        if: ${{ inputs.pr_number != '' }}
         uses: actions/github-script@v6
         with:
           script: |
@@ -134,7 +185,7 @@ jobs:
       # (This is why we don't need to specify `workflow_id` which would be fetched automatically in the python script.)
       - name: Get `END_SHA` from previous CI runs of the same workflow
         working-directory: /transformers/utils
-        if: ${{ env.process == 'true' && inputs.pr_number == '' }}
+        if: ${{ inputs.pr_number == '' }}
         env:
           ACCESS_TOKEN: ${{ secrets.ACCESS_REPO_INFO_TOKEN }}
         run: |
@@ -144,7 +195,7 @@ jobs:
       # parent commit (on `main`) of the `merge_commit` (dynamically created by GitHub). In this case, the goal is to
       # see if a reported failing test is actually ONLY failing on the `merge_commit`.
       - name: Set `END_SHA`
-        if: ${{ env.process == 'true' && inputs.pr_number != '' }}
+        if: ${{ inputs.pr_number != '' }}
         env:
           merge_commit_base_sha: ${{ steps.pr_info.outputs.merge_commit_base_sha }}
         run: |
@@ -152,41 +203,35 @@ jobs:

       - name: Reinstall transformers in edit mode (remove the one installed during docker image build)
         working-directory: /transformers
-        if: ${{ env.process == 'true' }}
         run: python3 -m pip uninstall -y transformers && python3 -m pip install -e .

       - name: NVIDIA-SMI
-        if: ${{ env.process == 'true' }}
         run: |
           nvidia-smi

       - name: Environment
         working-directory: /transformers
-        if: ${{ env.process == 'true' }}
         run: |
           python3 utils/print_env.py

       - name: Install pytest-flakefinder
-        if: ${{ env.process == 'true' }}
         run: python3 -m pip install pytest-flakefinder

       - name: Show installed libraries and their versions
         working-directory: /transformers
-        if: ${{ env.process == 'true' }}
         run: pip freeze

       - name: Check failed tests
         working-directory: /transformers
-        if: ${{ env.process == 'true' }}
         env:
           job: ${{ inputs.job }}
+          n_runners: ${{ needs.setup_check_new_failures.outputs.n_runners }}
           run_idx: ${{ matrix.run_idx }}
           pr_number: ${{ inputs.pr_number }}
         run: python3 utils/check_bad_commit.py --start_commit "$START_SHA" --end_commit "$END_SHA" --file "ci_results_${job}/new_failures.json" --output_file "new_failures_with_bad_commit_${job}_${run_idx}.json"

       - name: Show results
         working-directory: /transformers
-        if: ${{ env.process == 'true' }}
         env:
           job: ${{ inputs.job }}
           run_idx: ${{ matrix.run_idx }}
@@ -237,7 +282,45 @@ jobs:
         env:
           job: ${{ inputs.job }}
         run: |
-          cp "/transformers/new_failures_with_bad_commit_${job}/new_failures_with_bad_commit_${job}_1.json" new_failures_with_bad_commit.json
+          python3 - << 'EOF'
+          import json
+          import glob
+          import os
+
+          job = os.environ["job"]
+          pattern = f"/transformers/new_failures_with_bad_commit_{job}/new_failures_with_bad_commit_{job}_*.json"
+          files = sorted(glob.glob(pattern))
+
+          if not files:
+              print(f"No files found matching: {pattern}")
+              exit(1)
+
+          print(f"Found {len(files)} file(s) to merge: {files}")
+
+          merged = {}
+          for filepath in files:
+              with open(filepath) as f:
+                  data = json.load(f)
+
+              for model, model_results in data.items():
+                  if model not in merged:
+                      merged[model] = {}
+                  for gpu_type, failures in model_results.items():
+                      if gpu_type not in merged[model]:
+                          merged[model][gpu_type] = []
+                      merged[model][gpu_type].extend(failures)
+
+              print(f"filepath: {filepath}")
+              print(len(data))
+
+          output_path = "/transformers/new_failures_with_bad_commit.json"
+          with open(output_path, "w") as f:
+              json.dump(merged, f, indent=4)
+
+          print(f"Merged {len(files)} file(s) into {output_path}")
+          print(f"n_items: {len(merged)}")
+          print(merged)
+          EOF

       - name: Update clone
         working-directory: /transformers
diff --git a/utils/check_bad_commit.py b/utils/check_bad_commit.py
index 6766d99f606d..dfcfec6df83d 100644
--- a/utils/check_bad_commit.py
+++ b/utils/check_bad_commit.py
@@ -19,6 +19,7 @@
 import os
 import re
 import subprocess
+from collections import defaultdict

 import git
 import requests
@@ -314,6 +315,9 @@ def get_commit_info(commit, pr_number=None):
     parser.add_argument("--output_file", type=str, required=True, help="The path of the output file.")
     args = parser.parse_args()

+    run_idx = os.environ.get("run_idx")
+    n_runners = os.environ.get("n_runners")
+
     print(f"start_commit: {args.start_commit}")
     print(f"end_commit: {args.end_commit}")

@@ -336,6 +340,8 @@ def get_commit_info(commit, pr_number=None):
         with open(args.file, "r", encoding="UTF-8") as fp:
             reports = json.load(fp)

+        model_with_failures = []
+
         for model in reports:
             # We change the format of "new_failures.json" in PR #XXXXX, let's handle both formats for a few weeks.
             if "failures" in reports[model]:
@@ -351,42 +357,49 @@ def get_commit_info(commit, pr_number=None):
             reports[model].pop("multi-gpu", None)
             failed_tests = reports[model].get("single-gpu", [])

-            failed_tests_with_bad_commits = []
-            for failure in failed_tests:
-                test = failure["line"]
-                bad_commit_info = find_bad_commit(
-                    target_test=test, start_commit=args.start_commit, end_commit=args.end_commit
-                )
-                info = {"test": test}
-                info.update(bad_commit_info)
-
-                bad_commit = bad_commit_info["bad_commit"]
-
-                if bad_commit in commit_info_cache:
-                    commit_info = commit_info_cache[bad_commit]
-                else:
-                    commit_info = get_commit_info(bad_commit)
-                    commit_info_cache[bad_commit] = commit_info
-
-                commit_info_copied = copy.deepcopy(commit_info)
-                commit_info_copied.pop("commit")
-                commit_info_copied.update({"workflow_commit": args.start_commit, "base_commit": args.end_commit})
-                info.update(commit_info_copied)
-                # put failure message toward the end
-                info = {k: v for k, v in info.items() if not k.startswith(("failure_at_", "job_link"))} | {
-                    k: v for k, v in info.items() if k.startswith(("failure_at_", "job_link"))
-                }
-
-                failed_tests_with_bad_commits.append(info)
-
-            # If no single-gpu test failures, remove the key
-            if len(failed_tests_with_bad_commits) > 0:
-                reports[model]["single-gpu"] = failed_tests_with_bad_commits
+            model_with_failures.extend([(model, test) for test in failed_tests])
+
+        if run_idx is not None:
+            run_idx = int(run_idx)
+            n_runners = int(n_runners)
+
+            num_failed_tests_to_run = len(model_with_failures) // n_runners
+
+            start_idx = num_failed_tests_to_run * run_idx
+            end_idx = num_failed_tests_to_run * (run_idx + 1) if run_idx < n_runners - 1 else len(model_with_failures)
+
+            model_with_failures_to_check = model_with_failures[start_idx:end_idx]
+            model_with_failures = model_with_failures_to_check
+
+        failed_tests_with_bad_commits = defaultdict(list)
+        for model, failure in model_with_failures:
+            test = failure["line"]
+            bad_commit_info = find_bad_commit(
+                target_test=test, start_commit=args.start_commit, end_commit=args.end_commit
+            )
+            info = {"test": test}
+            info.update(bad_commit_info)
+
+            bad_commit = bad_commit_info["bad_commit"]
+
+            if bad_commit in commit_info_cache:
+                commit_info = commit_info_cache[bad_commit]
             else:
-                reports[model].pop("single-gpu", None)
+                commit_info = get_commit_info(bad_commit)
+                commit_info_cache[bad_commit] = commit_info
+
+            commit_info_copied = copy.deepcopy(commit_info)
+            commit_info_copied.pop("commit")
+            commit_info_copied.update({"workflow_commit": args.start_commit, "base_commit": args.end_commit})
+            info.update(commit_info_copied)
+            # put failure message toward the end
+            info = {k: v for k, v in info.items() if not k.startswith(("failure_at_", "job_link"))} | {
+                k: v for k, v in info.items() if k.startswith(("failure_at_", "job_link"))
+            }
+
+            failed_tests_with_bad_commits[model].append(info)

-        # remove the models without any test failure
-        reports = {k: v for k, v in reports.items() if len(v) > 0}
+        reports = {model: {"single-gpu": tests} for model, tests in failed_tests_with_bad_commits.items() if tests}

         with open(args.output_file, "w", encoding="UTF-8") as fp:
             json.dump(reports, fp, ensure_ascii=False, indent=4)

PATCH

echo "Patch applied successfully."
