#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibesec-skill

# Idempotency guard
if grep -qF "name: Vibe-Security-Skill" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: Vibe Security Skill
+name: Vibe-Security-Skill
 description: This skill helps Claude write secure web applications. Use when working on any web application to ensure security best practices are followed.
 ---
 
PATCH

echo "Gold patch applied."
