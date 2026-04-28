#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ralph

# Idempotency guard
if grep -qF "This lets users respond with \"1A, 2C, 3B\" for quick iteration. Remember to inden" "skills/prd/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/prd/SKILL.md b/skills/prd/SKILL.md
@@ -52,7 +52,7 @@ Ask only critical questions where the initial prompt is ambiguous. Focus on:
    D. Just the UI
 ```
 
-This lets users respond with "1A, 2C, 3B" for quick iteration.
+This lets users respond with "1A, 2C, 3B" for quick iteration. Remember to indent the options.
 
 ---
 
PATCH

echo "Gold patch applied."
