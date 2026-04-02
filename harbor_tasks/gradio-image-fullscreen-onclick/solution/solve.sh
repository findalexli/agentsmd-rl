#!/usr/bin/env bash
set -euo pipefail

FILE="js/image/shared/ImagePreview.svelte"

# Idempotency: check if already patched (onclick handler present on FullscreenButton)
if grep -q 'onclick.*is_fullscreen' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/image/shared/ImagePreview.svelte b/js/image/shared/ImagePreview.svelte
index 70642a0fe5..1640cde784 100644
--- a/js/image/shared/ImagePreview.svelte
+++ b/js/image/shared/ImagePreview.svelte
@@ -62,7 +62,13 @@
 			{on_custom_button_click}
 		>
 			{#if buttons.some((btn) => typeof btn === "string" && btn === "fullscreen")}
-				<FullscreenButton {fullscreen} on:fullscreen />
+				<FullscreenButton
+					{fullscreen}
+					onclick={(is_fullscreen) => {
+						fullscreen = is_fullscreen;
+						dispatch("fullscreen", is_fullscreen);
+					}}
+				/>
 			{/if}
 			{#if buttons.some((btn) => typeof btn === "string" && btn === "download")}
 				<DownloadLink href={value.url} download={value.orig_name || "image"}>

PATCH

echo "Patch applied successfully."
