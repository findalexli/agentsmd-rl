#!/bin/bash
# Gold solution: apply the production-code fix from PR #21356 to
# src/prefect/cli/deploy/_actions.py.
set -euo pipefail

cd /workspace/prefect

# Idempotency: only apply once.
if grep -q "Check if user has a custom image in job_variables but no build step" \
        src/prefect/cli/deploy/_actions.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/prefect/cli/deploy/_actions.py b/src/prefect/cli/deploy/_actions.py
index 9e8fefda5d47..9ab80e284227 100644
--- a/src/prefect/cli/deploy/_actions.py
+++ b/src/prefect/cli/deploy/_actions.py
@@ -240,6 +240,44 @@ async def _generate_default_pull_action(
                 console, deploy_config, auto=False
             )
     else:
+        # Check if user has a custom image in job_variables but no build step.
+        # In this case, the local cwd won't exist inside the container, so we
+        # need to use a container-appropriate working directory instead.
+        custom_image = (
+            deploy_config.get("work_pool", {}).get("job_variables", {}).get("image")
+        )
+        if custom_image:
+            if is_interactive():
+                dir_name = os.path.basename(os.getcwd())
+                pull_step = prompt(
+                    "What is the working directory in your Docker image"
+                    " where your flow code lives?",
+                    default=f"/opt/prefect/{dir_name}",
+                    console=console,
+                )
+                return [
+                    {
+                        "prefect.deployments.steps.set_working_directory": {
+                            "directory": pull_step
+                        }
+                    }
+                ]
+            else:
+                console.print(
+                    "[yellow]Warning: Using default working directory"
+                    " '/opt/prefect' for your Docker image. If your flow"
+                    " code is in a different location, add an explicit"
+                    " set_working_directory pull step to your"
+                    " prefect.yaml.[/yellow]"
+                )
+                return [
+                    {
+                        "prefect.deployments.steps.set_working_directory": {
+                            "directory": "/opt/prefect"
+                        }
+                    }
+                ]
+
         entrypoint_path, _ = deploy_config["entrypoint"].split(":")
         console.print(
             "Your Prefect workers will attempt to load your flow from:"
PATCH

echo "Patch applied."
