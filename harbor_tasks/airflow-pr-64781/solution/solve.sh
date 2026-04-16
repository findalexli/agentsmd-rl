#!/bin/bash
set -e

cd /workspace/airflow

# Check if patch is already applied (idempotency)
if grep -q "pre_image_commands: list\[tuple\[str, str\]\] = \[" dev/breeze/src/airflow_breeze/commands/ci_commands.py; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply --verbose <<'PATCH'
diff --git a/dev/breeze/src/airflow_breeze/commands/ci_commands.py b/dev/breeze/src/airflow_breeze/commands/ci_commands.py
index 7edf6fc2ac55c..c7cd5e2b8aece 100644
--- a/dev/breeze/src/airflow_breeze/commands/ci_commands.py
+++ b/dev/breeze/src/airflow_breeze/commands/ci_commands.py
@@ -778,17 +778,9 @@ def upgrade(
             "Commands may fail if they require authentication.[/]"
         )

-    # Build the CI image for Python 3.10 first so that subsequent steps (e.g. uv lock
-    # updates inside the image) use an up-to-date environment.
-    console_print("[info]Building CI image for Python 3.10 …[/]")
-    run_command(
-        ["breeze", "ci-image", "build", "--python", "3.10"],
-        check=False,
-        env=command_env,
-    )
-
-    # Define all upgrade commands to run (all run with check=False to continue on errors)
-    upgrade_commands: list[tuple[str, str]] = [
+    # Define upgrade commands to run before building the CI image (all run with check=False
+    # to continue on errors). These may update Dockerfiles and other build inputs.
+    pre_image_commands: list[tuple[str, str]] = [
         ("autoupdate", "prek autoupdate --cooldown-days 4 --freeze"),
         (
             "update-chart-dependencies",
@@ -798,11 +790,17 @@ def upgrade(
             "upgrade-important-versions",
             "prek --all-files --show-diff-on-failure --color always --verbose --stage manual upgrade-important-versions",
         ),
+    ]
+
+    # Define upgrade commands to run after building the CI image (they run inside the image
+    # and need an up-to-date environment).
+    post_image_commands: list[tuple[str, str]] = [
         (
             "update-uv-lock",
             "prek --all-files --show-diff-on-failure --color always --verbose update-uv-lock --stage manual",
         ),
     ]
+
     step_enabled = {
         "autoupdate": autoupdate,
         "update-chart-dependencies": update_chart_dependencies,
@@ -810,8 +808,24 @@ def upgrade(
         "update-uv-lock": update_uv_lock,
     }

-    # Execute enabled upgrade commands with the environment containing GitHub token
-    for step_name, command in upgrade_commands:
+    # Execute pre-image upgrade commands (may update Dockerfiles)
+    for step_name, command in pre_image_commands:
+        if step_enabled[step_name]:
+            run_command(command.split(), check=False, env=command_env)
+        else:
+            console_print(f"[info]Skipping {step_name} (disabled).[/]")
+
+    # Build the CI image for Python 3.10 after Dockerfiles have been updated so that
+    # subsequent steps (e.g. uv lock updates inside the image) use an up-to-date environment.
+    console_print("[info]Building CI image for Python 3.10 …[/]")
+    run_command(
+        ["breeze", "ci-image", "build", "--python", "3.10"],
+        check=False,
+        env=command_env,
+    )
+
+    # Execute post-image upgrade commands (run inside the freshly built image)
+    for step_name, command in post_image_commands:
         if step_enabled[step_name]:
             run_command(command.split(), check=False, env=command_env)
         else:
PATCH

echo "Patch applied successfully"
