#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swamp

# Idempotency guard
if grep -qF "`skill-creator` skill guidelines to ensure consistent structure and quality." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -20,6 +20,11 @@ service integrations.
 When planning new features, always use the `ddd` skill to inform the
 architecture.
 
+## Skills
+
+When creating or updating `swamp-*` skills in `.claude/skills/`, follow the
+`skill-creator` skill guidelines to ensure consistent structure and quality.
+
 ## Code Style
 
 - TypeScript strict mode, no `any` types
PATCH

echo "Gold patch applied."
