#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency check: if dimensions_changed is already in brush.ts, patch was applied
if grep -q 'dimensions_changed' js/imageeditor/shared/brush/brush.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/imageeditor/shared/brush/brush-textures.ts b/js/imageeditor/shared/brush/brush-textures.ts
index dd06380ed9d..23ff1633f16 100644
--- a/js/imageeditor/shared/brush/brush-textures.ts
+++ b/js/imageeditor/shared/brush/brush-textures.ts
@@ -399,11 +399,11 @@ export class BrushTextures {
 	 * Reinitializes textures when needed (e.g., after resizing).
 	 */
 	reinitialize(): void {
+		const local_bounds =
+			this.image_editor_context.image_container.getLocalBounds();
 		if (
-			this.image_editor_context.image_container.width !==
-				this.dimensions.width ||
-			this.image_editor_context.image_container.height !==
-				this.dimensions.height
+			Math.round(local_bounds.width) !== Math.round(this.dimensions.width) ||
+			Math.round(local_bounds.height) !== Math.round(this.dimensions.height)
 		) {
 			this.initialize_textures();
 		}
diff --git a/js/imageeditor/shared/brush/brush.ts b/js/imageeditor/shared/brush/brush.ts
index b71baa37654..98549f1db30 100644
--- a/js/imageeditor/shared/brush/brush.ts
+++ b/js/imageeditor/shared/brush/brush.ts
@@ -169,7 +169,20 @@ export class BrushTool implements Tool {
 		const textures_initialized =
 			this.brush_textures?.textures_initialized ?? false;

-		if (needs_brush_tool && (mode_changed || !textures_initialized)) {
+		let dimensions_changed = false;
+		if (this.brush_textures && textures_initialized) {
+			const current_bounds =
+				this.image_editor_context.image_container.getLocalBounds();
+			const tex_dims = this.brush_textures.get_dimensions();
+			dimensions_changed =
+				Math.round(current_bounds.width) !== Math.round(tex_dims.width) ||
+				Math.round(current_bounds.height) !== Math.round(tex_dims.height);
+		}
+
+		if (
+			needs_brush_tool &&
+			(mode_changed || !textures_initialized || dimensions_changed)
+		) {
 			this.brush_textures?.initialize_textures();
 		}

PATCH

echo "Patch applied successfully."
