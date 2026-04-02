#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if the fix is already applied (test_command parameter in find_workflow_run_url)
if grep -q 'test_command=test_command' scripts/ci/utils/slash_command_handler.py 2>/dev/null; then
    echo "Fix already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/workflows/rerun-ut.yml b/.github/workflows/rerun-ut.yml
index f58fb6b00dc3..8cb6fc1a10dc 100644
--- a/.github/workflows/rerun-ut.yml
+++ b/.github/workflows/rerun-ut.yml
@@ -1,5 +1,5 @@
 name: Rerun UT
-run-name: ${{ inputs.pr_head_sha && format('[rerun-ut] {0}', inputs.pr_head_sha) || '[rerun-ut]' }}
+run-name: ${{ inputs.pr_head_sha && format('[rerun-ut] {0} {1}', inputs.test_command, inputs.pr_head_sha) || format('[rerun-ut] {0}', inputs.test_command) }}

 on:
   workflow_dispatch:
diff --git a/scripts/ci/utils/slash_command_handler.py b/scripts/ci/utils/slash_command_handler.py
index 0b2e4535b47b..7d74601721bb 100644
--- a/scripts/ci/utils/slash_command_handler.py
+++ b/scripts/ci/utils/slash_command_handler.py
@@ -22,6 +22,7 @@ def find_workflow_run_url(
     dispatch_time,
     pr_head_sha=None,
     max_wait=30,
+    test_command=None,
 ):
     """
     Poll for the workflow run URL after dispatch.
@@ -43,12 +44,14 @@ def find_workflow_run_url(
     Returns:
         The workflow run URL if found, None otherwise.
     """
-    # Build expected display_title pattern based on workflow's run-name
-    # Format: "[stage-name] sha" for fork PRs, "[stage-name]" for non-fork
+    # Build expected display_title based on workflow's run-name.
+    # rerun-ut includes test_command: "[rerun-ut] <test_command> [<sha>]"
+    # Other workflows: "[stage-name] [<sha>]"
+    suffix = f" {test_command}" if test_command else ""
     if pr_head_sha:
-        expected_title = f"[{target_stage}] {pr_head_sha}"
+        expected_title = f"[{target_stage}]{suffix} {pr_head_sha}"
     else:
-        expected_title = f"[{target_stage}]"
+        expected_title = f"[{target_stage}]{suffix}"

     print(f"Looking for workflow run with display_title: {expected_title}")

@@ -374,11 +377,7 @@ def handle_rerun_stage(
             print(f"Successfully triggered workflow for stage '{stage_name}'")
             if react_on_success:
                 comment.create_reaction("+1")
-                pr.create_issue_comment(
-                    f"✅ Triggered `{stage_name}` to run independently (skipping dependencies)."
-                )

-                # Poll for the workflow run URL and post follow-up comment
                 run_url = find_workflow_run_url(
                     gh_repo,
                     target_workflow.id,
@@ -390,9 +389,15 @@ def handle_rerun_stage(
                     max_wait=30,
                 )
                 if run_url:
-                    pr.create_issue_comment(f"🔗 [View workflow run]({run_url})")
+                    pr.create_issue_comment(
+                        f"✅ Triggered `{stage_name}` to run independently"
+                        f" (skipping dependencies)."
+                        f" [View workflow run]({run_url})"
+                    )
                 else:
                     pr.create_issue_comment(
+                        f"✅ Triggered `{stage_name}` to run independently"
+                        f" (skipping dependencies).\n"
                         f"⚠️ Could not retrieve workflow run URL. "
                         f"Check the [Actions tab](https://github.com/{gh_repo.full_name}/actions) for progress."
                     )
@@ -640,11 +645,9 @@ def handle_rerun_ut(gh_repo, pr, comment, user_perms, test_spec, token):
         if success:
             print(f"Successfully triggered rerun-ut: {test_command}")
             comment.create_reaction("+1")
-            pr.create_issue_comment(
-                f"✅ Triggered `/rerun-ut` on `{runner_label}` runner:\n"
-                f"```\ncd test/ && python3 {test_command}\n```"
-            )

+            # Include test_command in expected title to distinguish
+            # concurrent /rerun-ut dispatches (run-name includes test_command)
             run_url = find_workflow_run_url(
                 gh_repo,
                 target_workflow.id,
@@ -654,11 +657,18 @@ def handle_rerun_ut(gh_repo, pr, comment, user_perms, test_spec, token):
                 dispatch_time,
                 pr_head_sha=pr_head_sha,
                 max_wait=30,
+                test_command=test_command,
             )
             if run_url:
-                pr.create_issue_comment(f"🔗 [View workflow run]({run_url})")
+                pr.create_issue_comment(
+                    f"✅ Triggered `/rerun-ut` on `{runner_label}` runner:"
+                    f" [View workflow run]({run_url})\n"
+                    f"```\ncd test/ && python3 {test_command}\n```"
+                )
             else:
                 pr.create_issue_comment(
+                    f"✅ Triggered `/rerun-ut` on `{runner_label}` runner:\n"
+                    f"```\ncd test/ && python3 {test_command}\n```\n"
                     f"⚠️ Could not retrieve workflow run URL. "
                     f"Check the [Actions tab](https://github.com/{gh_repo.full_name}/actions) for progress."
                 )

PATCH

echo "Patch applied successfully."
