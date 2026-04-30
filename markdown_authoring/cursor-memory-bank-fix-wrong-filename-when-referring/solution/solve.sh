#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cursor-memory-bank

# Idempotency guard
if grep -qF "AssessLevel -->|\"Level 4\"| L4Archive[\"LEVEL 4 ARCHIVING<br>Level4/archive-compre" ".cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc b/.cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc
@@ -20,10 +20,10 @@ graph TD
     VerifyReflect -->|"Yes"| AssessLevel{"Determine<br>Complexity Level"}
     
     %% Level-Based Archiving
-    AssessLevel -->|"Level 1"| L1Archive["LEVEL 1 ARCHIVING<br>Level1/archive-minimal.md"]
-    AssessLevel -->|"Level 2"| L2Archive["LEVEL 2 ARCHIVING<br>Level2/archive-basic.md"]
-    AssessLevel -->|"Level 3"| L3Archive["LEVEL 3 ARCHIVING<br>Level3/archive-standard.md"]
-    AssessLevel -->|"Level 4"| L4Archive["LEVEL 4 ARCHIVING<br>Level4/archive-comprehensive.md"]
+    AssessLevel -->|"Level 1"| L1Archive["LEVEL 1 ARCHIVING"]
+    AssessLevel -->|"Level 2"| L2Archive["LEVEL 2 ARCHIVING<br>Level2/archive-basic.mdc"]
+    AssessLevel -->|"Level 3"| L3Archive["LEVEL 3 ARCHIVING<br>Level3/archive-intermediate.mdc"]
+    AssessLevel -->|"Level 4"| L4Archive["LEVEL 4 ARCHIVING<br>Level4/archive-comprehensive.mdc"]
     
     %% Level 1 Archiving (Minimal)
     L1Archive --> L1Summary["Create Quick<br>Summary"]
@@ -269,4 +269,4 @@ When archiving is complete, notify user with:
 
 → Memory Bank is ready for the next task
 → To start a new task, use VAN MODE
-``` 
\ No newline at end of file
+``` 
PATCH

echo "Gold patch applied."
