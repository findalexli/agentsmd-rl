#!/bin/bash
set -e

REPO="/workspace/langchain"
cd "$REPO"

# Idempotency check: if the fix is already applied, skip
if grep -q "resolved_path = save_path.resolve()" libs/core/langchain_core/prompts/base.py 2>/dev/null; then
    echo "Fix already applied, skipping..."
    exit 0
fi

# Apply the gold patch (from repo root, strip level 1 for a/ prefix)
patch -p1 <<'PATCH'
diff --git a/libs/core/langchain_core/prompts/base.py b/libs/core/langchain_core/prompts/base.py
index 7aa7ea58d9afe..c96c936d80f16 100644
--- a/libs/core/langchain_core/prompts/base.py
+++ b/libs/core/langchain_core/prompts/base.py
@@ -389,11 +389,12 @@ def save(self, file_path: Path | str) -> None:
         directory_path = save_path.parent
         directory_path.mkdir(parents=True, exist_ok=True)

-        if save_path.suffix == ".json":
-            with save_path.open("w", encoding="utf-8") as f:
+        resolved_path = save_path.resolve()
+        if resolved_path.suffix == ".json":
+            with resolved_path.open("w", encoding="utf-8") as f:
                 json.dump(prompt_dict, f, indent=4)
-        elif save_path.suffix.endswith((".yaml", ".yml")):
-            with save_path.open("w", encoding="utf-8") as f:
+        elif resolved_path.suffix.endswith((".yaml", ".yml")):
+            with resolved_path.open("w", encoding="utf-8") as f:
                 yaml.dump(prompt_dict, f, default_flow_style=False)
         else:
             msg = f"{save_path} must be json or yaml"
PATCH

echo "Patch applied successfully"
