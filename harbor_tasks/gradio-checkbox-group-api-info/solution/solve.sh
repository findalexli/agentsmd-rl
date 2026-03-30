#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

cat > /tmp/patch.diff << 'PATCH'
diff --git a/gradio/components/custom_html_components/colored_checkbox_group.py b/gradio/components/custom_html_components/colored_checkbox_group.py
index 3a8d551eb2..daabdca71f 100644
--- a/gradio/components/custom_html_components/colored_checkbox_group.py
+++ b/gradio/components/custom_html_components/colored_checkbox_group.py
@@ -62,7 +62,7 @@ def __init__(

     def api_info(self):
         return {
-            "items": {"enum": self.choices, "type": "string"},  # type: ignore
+            "items": {"enum": self.props["choices"], "type": "string"},  # type: ignore
             "title": "Checkbox Group",
             "type": "array",
         }
PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
