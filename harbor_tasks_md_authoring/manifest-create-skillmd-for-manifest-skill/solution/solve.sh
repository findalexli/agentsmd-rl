#!/usr/bin/env bash
set -euo pipefail

cd /workspace/manifest

# Idempotency guard
if grep -qF "Placeholder for Manifest skill" "skills/manifest/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/manifest/SKILL.md b/skills/manifest/SKILL.md
@@ -0,0 +1,3 @@
+# Manifest Skill
+
+Placeholder for Manifest skill
PATCH

echo "Gold patch applied."
