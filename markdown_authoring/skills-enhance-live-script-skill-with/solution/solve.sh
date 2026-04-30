#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "%[text] | Column A | Column B |" "skills/matlab-live-script/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/matlab-live-script/SKILL.md b/skills/matlab-live-script/SKILL.md
@@ -66,6 +66,19 @@ Bulleted lists must have a backslash on the last item:
 %[text] - bullet 3 \
 ```
 
+
+### Tables
+
+```matlab
+%[text:table]
+%[text] | Column A | Column B |
+%[text] | --- | --- |
+%[text] | Value 1 | Value 2 |
+%[text] | Value 3 | Value 4 |
+%[text:table]
+```
+
+
 ### LaTeX Equations
 Format equations with double backslashes:
 
PATCH

echo "Gold patch applied."
