#!/usr/bin/env bash
set -euo pipefail

cd /workspace/morphir

# Idempotency guard
if grep -qF "When morphir-go, morphir-python, or others are added, they will live under `ecos" "ecosystem/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ecosystem/AGENTS.md b/ecosystem/AGENTS.md
@@ -58,7 +58,7 @@ Changes inside submodules are committed in the submodule repo. The morphir repo
 
 ## Future submodules
 
-When morphir-go or others are added, they will live under `ecosystem/` with the same pattern. Document any language- or repo-specific usage in this file.
+When morphir-go, morphir-python, or others are added, they will live under `ecosystem/` with the same pattern. Document any language- or repo-specific usage in this file.
 
 ### morphir-python
 
PATCH

echo "Gold patch applied."
