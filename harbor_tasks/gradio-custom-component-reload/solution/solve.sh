#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

git apply - <<'PATCH'
diff --git a/js/core/src/MountComponents.svelte b/js/core/src/MountComponents.svelte
index 09bf8152cf..58c7fc71e6 100644
--- a/js/core/src/MountComponents.svelte
+++ b/js/core/src/MountComponents.svelte
@@ -3,8 +3,6 @@
 	import MountCustomComponent from "./MountCustomComponent.svelte";
 	let { node, ...rest } = $props();

-	$inspect(node);
-
 	let component = $derived(await node.component);
 </script>

diff --git a/js/core/src/MountCustomComponent.svelte b/js/core/src/MountCustomComponent.svelte
index 16dd2d15f4..f4450f293a 100644
--- a/js/core/src/MountCustomComponent.svelte
+++ b/js/core/src/MountCustomComponent.svelte
@@ -1,35 +1,37 @@
 <script lang="ts">
-	import { onMount, onDestroy } from "svelte";
 	let { node, children, ...rest } = $props();

 	let component = $derived(await node.component);
 	let runtime = $derived(
 		(await node.runtime) as {
 			mount: typeof import("svelte").mount;
-			umount: typeof import("svelte").unmount;
+			unmount: typeof import("svelte").unmount;
 		}
 	);
 	let el: HTMLElement = $state(null);
-	let comp;

 	$effect(() => {
-		if (el && !comp && runtime) {
-			comp = runtime.mount(component.default, {
-				target: el,
+		if (!el || !runtime || !component) return;

-				props: {
-					shared_props: node.props.shared_props,
-					props: node.props.props,
-					children
-				}
-			});
-		}
-	});
+		// Read prop references so the effect re-runs when the node is
+		// replaced during a dev reload (new objects are created by
+		// app_tree.reload).
+		const _shared_props = node.props.shared_props;
+		const _props = node.props.props;
+		const _runtime = runtime;

-	onDestroy(() => {
-		if (comp) {
-			runtime.umount(comp);
-		}
+		const mounted = _runtime.mount(component.default, {
+			target: el,
+			props: {
+				shared_props: _shared_props,
+				props: _props,
+				children
+			}
+		});
+
+		return () => {
+			_runtime.unmount(mounted);
+		};
 	});
 </script>

PATCH
