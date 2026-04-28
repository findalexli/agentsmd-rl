#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vercel

# Idempotency guard
if grep -qF "description: Deploy, manage, and develop projects on Vercel from the command lin" "skills/vercel-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/vercel-cli/SKILL.md b/skills/vercel-cli/SKILL.md
@@ -1,5 +1,6 @@
 ---
 name: vercel-cli
+description: Deploy, manage, and develop projects on Vercel from the command line
 ---
 
 # Vercel CLI Skill
PATCH

echo "Gold patch applied."
