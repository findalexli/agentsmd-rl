#!/usr/bin/env bash
set -euo pipefail

FILE="tests/v1/engine/test_abort_final_step.py"

# Idempotency: check if fix is already applied (unique string from the patch)
if grep -q 'Timeout waiting for KV connector' "$FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/v1/engine/test_abort_final_step.py b/tests/v1/engine/test_abort_final_step.py
index 560c5c2b1e30..81a120d151d6 100644
--- a/tests/v1/engine/test_abort_final_step.py
+++ b/tests/v1/engine/test_abort_final_step.py
@@ -259,8 +259,25 @@ async def generate():
                 # Wait for generation to complete
                 await gen_task

-                # Give the scheduler a moment to finish cleanup
-                await asyncio.sleep(0.1)
+                # Poll for the KV connector to record the finish status
+                timeout = 5.0
+                start = time.time()
+                captured_statuses = []
+                while time.time() - start < timeout:
+                    with open(status_file) as f4:
+                        status_lines = f4.read().strip().split("\n")
+                        captured_statuses = [
+                            line
+                            for line in status_lines
+                            if line and line.startswith("FINISHED_")
+                        ]
+                    if captured_statuses:
+                        break
+                    await asyncio.sleep(0.05)
+                else:
+                    raise TimeoutError(
+                        "Timeout waiting for KV connector to record finish status."
+                    )

                 # Verify we got output
                 assert len(outputs) > 0, "Should have received at least one output"
@@ -275,15 +292,6 @@ async def generate():
                     f"'{final_output.outputs[0].finish_reason}'. "
                 )

-                with open(status_file) as f4:
-                    status_lines = f4.read().strip().split("\n")
-                    # Filter for actual finish statuses (not INIT or empty lines)
-                    captured_statuses = [
-                        line
-                        for line in status_lines
-                        if line and line.startswith("FINISHED_")
-                    ]
-
                 assert len(captured_statuses) >= 1, (
                     f"Expected at least 1 captured finish status, got "
                     f"{len(captured_statuses)}. File content: {status_lines}"

PATCH

echo "Patch applied successfully."
