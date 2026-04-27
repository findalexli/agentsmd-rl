#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanostack

# Idempotency guard
if grep -qF "All skills reference scripts as `bin/save-artifact.sh`, `bin/find-artifact.sh`, " "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -57,6 +57,23 @@ Skills `/review`, `/security`, and `/qa` support intensity modes:
 
 Skills auto-suggest a mode based on the diff, but the user always decides.
 
+## Script Resolution
+
+All skills reference scripts as `bin/save-artifact.sh`, `bin/find-artifact.sh`, etc. These paths are **relative to the nanostack skill root**, not to the user's project directory.
+
+Before running any `bin/` script, resolve the nanostack root:
+
+```bash
+# Find nanostack installation directory
+NANOSTACK_ROOT="$(dirname "$(readlink -f "$(which claude 2>/dev/null)" 2>/dev/null)")/../../skills/nanostack" 2>/dev/null
+[ ! -d "$NANOSTACK_ROOT" ] && NANOSTACK_ROOT="$HOME/.claude/skills/nanostack"
+[ ! -d "$NANOSTACK_ROOT" ] && NANOSTACK_ROOT="$(find "$HOME/.claude" -name "nanostack" -type d -path "*/skills/*" 2>/dev/null | head -1)"
+```
+
+Then prefix all script calls: `"$NANOSTACK_ROOT/bin/save-artifact.sh"` instead of `bin/save-artifact.sh`.
+
+If the nanostack root cannot be found, skip the script call and proceed with the skill. Never fail a skill because a helper script is missing.
+
 ## Artifact Persistence
 
 Skills automatically save their output to `.nanostack/` after every run:
PATCH

echo "Gold patch applied."
