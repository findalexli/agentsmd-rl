#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "skills/youtube-summarizer/SKILL.md" "skills/youtube-summarizer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/youtube-summarizer/SKILL.md b/skills/youtube-summarizer/SKILL.md
@@ -330,6 +330,7 @@ echo "[████████████████████] 100% - Step
 ## 📌 Conclusion
 
 [Final synthesis and takeaways]
+```
 
 
 ### **Example 2: Missing Dependency**
PATCH

echo "Gold patch applied."
