#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "skills/matlab-live-script/SKILL.md" "skills/matlab-live-script/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/matlab-live-script/SKILL.md b/skills/matlab-live-script/SKILL.md
@@ -131,15 +131,6 @@ grid on
 %---
 ```
 
-## Evaluation Command
-
-After creating a Live Script, evaluate it using:
-```matlab
-matlab.internal.liveeditor.executeAndSave('FILENAME.m')
-```
-
-This command inserts computational outputs (text and images) into the Live Script.
-
 ## Structure Pattern
 
 A typical Live Script follows this pattern:
PATCH

echo "Gold patch applied."
