#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Check if already applied — the fix renames .image-container to .gallery-container in CSS
if grep -q '\.gallery-container {' js/gallery/shared/Gallery.svelte && \
   ! grep -q '\.image-container {' js/gallery/shared/Gallery.svelte; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/gallery/Index.svelte b/js/gallery/Index.svelte
index cbb1b9338a..18d1e7077f 100644
--- a/js/gallery/Index.svelte
+++ b/js/gallery/Index.svelte
@@ -158,9 +158,7 @@
 	scale={gradio.shared.scale}
 	min_width={gradio.shared.min_width}
 	allow_overflow={false}
-	height={typeof gradio.props.height === "number"
-		? gradio.props.height
-		: undefined}
+	height={gradio.props.height || undefined}
 	bind:fullscreen
 >
 	<StatusTracker
@@ -175,7 +173,7 @@
 			class={!gradio.props.value ||
 			(active_source && active_source.includes("webcam"))
 				? "hidden-upload-input"
-				: ""}
+				: "upload-wrapper"}
 		>
 			<BaseFileUpload
 				bind:upload_promise
@@ -328,4 +326,7 @@
 	.hidden-upload-input {
 		display: none;
 	}
+	.upload-wrapper {
+		height: 100%;
+	}
 </style>
diff --git a/js/gallery/shared/Gallery.svelte b/js/gallery/shared/Gallery.svelte
index a5e71c2980..2c078be1f3 100644
--- a/js/gallery/shared/Gallery.svelte
+++ b/js/gallery/shared/Gallery.svelte
@@ -77,7 +77,7 @@
 		value: GalleryData[] | null;
 		columns: number | number[] | undefined;
 		rows: number | number[] | undefined;
-		height: number | "auto";
+		height: number | string;
 		preview: boolean;
 		allow_preview: boolean;
 		object_fit: "contain" | "cover" | "fill" | "none" | "scale-down";
@@ -539,7 +539,11 @@
 			class:minimal={mode === "minimal"}
 			class:fixed-height={mode !== "minimal" && (!height || height == "auto")}
 			class:hidden={is_full_screen}
-			style:height={height !== "auto" ? height + "px" : null}
+			style:height={height !== "auto"
+				? typeof height === "number"
+					? height + "px"
+					: height
+				: null}
 		>
 			{#if interactive && selected_index === null}
 				<ModifyUpload
@@ -663,11 +667,11 @@
 {/if}

 <style lang="postcss">
-	.image-container {
+	.gallery-container {
 		height: 100%;
 		position: relative;
 	}
-	.image-container :global(img),
+	.gallery-container :global(img),
 	button {
 		width: var(--size-full);
 		height: var(--size-full);
diff --git a/js/gallery/types.ts b/js/gallery/types.ts
index b4d83b551b..77c00ce4aa 100644
--- a/js/gallery/types.ts
+++ b/js/gallery/types.ts
@@ -18,7 +18,7 @@ export interface GalleryProps {
 	file_types: string[] | null;
 	columns: number | number[] | undefined;
 	rows: number | number[] | undefined;
-	height: number | "auto";
+	height: number | string;
 	preview: boolean;
 	allow_preview: boolean;
 	selected_index: number | null;

PATCH

echo "Patch applied successfully."
