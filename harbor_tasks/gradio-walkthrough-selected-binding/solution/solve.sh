#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if already fixed
if grep -q 'bind:selected={gradio.props.selected}' js/tabs/Index.svelte &&
   ! grep -qP '^\s+selected=\{gradio\.props\.selected\}$' js/tabs/Index.svelte; then
    echo "Already patched."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/tabs/Index.svelte b/js/tabs/Index.svelte
index 7241392662..b35d459286 100644
--- a/js/tabs/Index.svelte
+++ b/js/tabs/Index.svelte
@@ -34,7 +34,7 @@
 		visible={gradio.shared.visible}
 		elem_id={gradio.shared.elem_id}
 		elem_classes={gradio.shared.elem_classes}
-		selected={gradio.props.selected}
+		bind:selected={gradio.props.selected}
 		on:change={() => gradio.dispatch("change")}
 		on:select={(e) => {
 			gradio.dispatch("select", e.detail);

PATCH

echo "Patch applied."
