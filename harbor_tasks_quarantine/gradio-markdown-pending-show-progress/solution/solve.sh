#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if already patched, exit
if grep -q 'show_progress.*!==.*"hidden"' js/markdown/Index.svelte 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/markdown/Index.svelte b/js/markdown/Index.svelte
index 139ad9e36a..808f18c17a 100644
--- a/js/markdown/Index.svelte
+++ b/js/markdown/Index.svelte
@@ -62,7 +62,8 @@
 	<div
 		bind:this={wrapper}
 		class:padding={gradio.props.padding}
-		class:pending={gradio.shared.loading_status?.status === "pending"}
+		class:pending={gradio.shared.loading_status?.status === "pending" &&
+			gradio.shared.loading_status?.show_progress !== "hidden"}
 	>
 		<Markdown
 			value={gradio.props.value}

PATCH

echo "Patch applied successfully."
