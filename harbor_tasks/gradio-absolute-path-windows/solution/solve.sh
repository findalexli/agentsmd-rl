#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

cat > /tmp/patch.diff << 'PATCH'
diff --git a/gradio/utils.py b/gradio/utils.py
index d694339036..233238034a 100644
--- a/gradio/utils.py
+++ b/gradio/utils.py
@@ -1696,6 +1696,7 @@ def safe_join(directory: DeveloperPath, path: UserProvidedPath) -> str:
     if (
         any(sep in filename for sep in _os_alt_seps)
         or os.path.isabs(filename)
+        or filename.startswith("/")
         or filename == ".."
         or filename.startswith("../")
     ):
PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
