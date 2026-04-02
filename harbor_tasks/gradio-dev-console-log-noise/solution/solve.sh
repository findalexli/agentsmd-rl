#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency check: if the first console.log is already gone, patch was applied
if ! grep -q 'console.log({ el, comp, runtime })' js/core/src/MountCustomComponent.svelte 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/core/src/MountCustomComponent.svelte b/js/core/src/MountCustomComponent.svelte
index c46e6f9065..16dd2d15f4 100644
--- a/js/core/src/MountCustomComponent.svelte
+++ b/js/core/src/MountCustomComponent.svelte
@@ -13,7 +13,6 @@
 	let comp;

 	$effect(() => {
-		console.log({ el, comp, runtime });
 		if (el && !comp && runtime) {
 			comp = runtime.mount(component.default, {
 				target: el,
diff --git a/js/preview/src/plugins.ts b/js/preview/src/plugins.ts
index 163a3b5e95..13bf0bd5a4 100644
--- a/js/preview/src/plugins.ts
+++ b/js/preview/src/plugins.ts
@@ -127,7 +127,6 @@
 			}

 			if (id === resolved_v_id_2) {
-				console.log("init gradio");
 				return `window.__GRADIO_DEV__ = "dev";
       window.__GRADIO__SERVER_PORT__ = ${backend_port};
       window.__GRADIO__CC__ = ${imports};
diff --git a/js/spa/src/main.ts b/js/spa/src/main.ts
index 526201b420..7b0a9d6f75 100644
--- a/js/spa/src/main.ts
+++ b/js/spa/src/main.ts
@@ -29,8 +29,6 @@
 const mode: "_NORMAL_" | "_CC_" = globalThis.__MODE__;

 async function get_index(): Promise<void> {
-	console.log("mode", mode);
-
 	if (mode === "_CC_") {
 		await import("virtual:cc-init");
 	}

PATCH

echo "Patch applied successfully."
