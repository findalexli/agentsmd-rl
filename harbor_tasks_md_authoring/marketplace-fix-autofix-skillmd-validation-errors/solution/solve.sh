#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketplace

# Idempotency guard
if grep -qF "name: react-components" "skills/google-labs-code/react-components/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/google-labs-code/react-components/SKILL.md b/skills/google-labs-code/react-components/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: react:components
+name: react-components
 description: Converts Stitch designs into modular Vite and React components using system-level networking and AST-based validation.
 allowed-tools:
   - "stitch*:*"
PATCH

echo "Gold patch applied."
