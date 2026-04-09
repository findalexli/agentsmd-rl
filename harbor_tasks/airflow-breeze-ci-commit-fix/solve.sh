#!/bin/bash
set -e

cd /workspace/airflow

# Apply the gold patch for CI command fix
cat <<'PATCH' | git apply -v
diff --git a/dev/breeze/src/airflow_breeze/commands/ci_commands.py b/dev/breeze/src/airflow_breeze/commands/ci_commands.py
index a011f7ba6d3de..b8d4138371345 100644
--- a/dev/breeze/src/airflow_breeze/commands/ci_commands.py
+++ b/dev/breeze/src/airflow_breeze/commands/ci_commands.py
@@ -849,7 +849,23 @@ def upgrade(

         run_command(["git", "checkout", "-b", branch_name])
         run_command(["git", "add", "."])
-        run_command(["git", "commit", "-m", f"[{target_branch}] CI: Upgrade important CI environment"])
+        try:
+            run_command(
+                ["git", "commit", "--message", f"[{target_branch}] CI: Upgrade important CI environment"]
+            )
+        except subprocess.CalledProcessError:
+            console_print("[info]Commit failed, assume some auto-fixes might have been made...[/]")
+            run_command(["git", "add", "."])
+            run_command(
+                [
+                    "git",
+                    "commit",
+                    # postpone pre-commit checks to CI, not to fail in automation if e.g. mypy changes force code checks
+                    "--no-verify",
+                    "--message",
+                    f"[{target_branch}] CI: Upgrade important CI environment",
+                ]
+            )

         # Push the branch to origin (use detected origin or fallback to 'origin')
         push_remote = origin_remote_name if origin_remote_name else "origin"
PATCH

# Idempotency check - verify the distinctive line exists
grep -q "postpone pre-commit checks to CI" dev/breeze/src/airflow_breeze/commands/ci_commands.py \
    && echo "Patch applied successfully" \
    || (echo "Patch not applied correctly" && exit 1)
