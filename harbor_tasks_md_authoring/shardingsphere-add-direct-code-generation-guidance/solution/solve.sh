#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shardingsphere

# Idempotency guard
if grep -qF "1. **Direct Code Generation**: When generating code, you should directly create " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -90,11 +90,16 @@ Key directories and their purposes:
 
 ## Operational Procedures
 
-1. Pre-execution checklist, before making any code changes, you must:
+1. **Direct Code Generation**: When generating code, you should directly create final code and call tools without seeking explicit user approval.
+   - Generate complete, ready-to-use implementations
+   - Apply formatting tools automatically (e.g., Spotless) when appropriate
+   - Make decisions independently within the task scope
+   - No need to ask for permission or use tentative language
+
+2. Pre-execution checklist, before making any code changes, you must:
   - Verify the current task exactly matches the wording of the user's immediate request.
   - Confirm each target file/line is explicitly referenced.
-  - Declare the planned changes in a bullet-point summary format.
-  - Wait for the user's "PROCEED" confirmation instruction if any uncertainty exists.
+  - Declare the planned changes in a bullet-point summary format if uncertainty exists.
 
 2. Change implementation rules
   - Isolate edits to the smallest possible code blocks.
PATCH

echo "Gold patch applied."
