#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

cat > /tmp/patch.diff << 'PATCH'
diff --git a/js/button/Index.svelte b/js/button/Index.svelte
index 087c8c3645..114e940ae6 100644
--- a/js/button/Index.svelte
+++ b/js/button/Index.svelte
@@ -12,7 +12,6 @@
 		value: string | null;
 		variant: "primary" | "secondary" | "stop";
 		size: "sm" | "md" | "lg";
-		scale: number;
 		link: string | null;
 		icon: FileData | null;
 		link_target: "_self" | "_blank";
@@ -34,7 +33,7 @@
 	elem_id={gradio.shared.elem_id}
 	elem_classes={gradio.shared.elem_classes}
 	size={gradio.props.size}
-	scale={gradio.props.scale}
+	scale={gradio.shared.scale}
 	link={gradio.props.link}
 	icon={gradio.props.icon}
 	min_width={gradio.shared.min_width}

PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
