#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if watch_fn already appears in shared/HTML.svelte, patch is applied
if grep -q 'watch_fn' js/html/shared/HTML.svelte 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/components/html.py b/gradio/components/html.py
index d2a9f28d077..2d477c2d001 100644
--- a/gradio/components/html.py
+++ b/gradio/components/html.py
@@ -84,7 +84,7 @@ class HTML(Component):
             label: The label for this component. Is used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
             html_template: A string representing the HTML template for this component as a JS template string and Handlebars template. The `${value}` tag will be replaced with the `value` parameter, and all other tags will be filled in with the values from `props`. This element can have children when used in a `with gr.HTML(...):` context, and the children will be rendered to replace `@children` substring, which cannot be nested inside any HTML tags.
             css_template: A string representing the CSS template for this component as a JS template string and Handlebars template. The CSS will be automatically scoped to this component, and rules outside a block will target the component's root element. The `${value}` tag will be replaced with the `value` parameter, and all other tags will be filled in with the values from `props`.
-            js_on_load: A string representing the JavaScript code that will be executed when the component is loaded. The `element` variable refers to the HTML element of this component, and can be used to access children such as `element.querySelector()`. The `trigger` function can be used to trigger events, such as `trigger('click')`. The value and other props can be edited through `props`, e.g. `props.value = "new value"` which will re-render the HTML template. If `server_functions` is provided, a `server` object is also available in `js_on_load`, where each function is accessible as an async method, e.g. `server.list_files(path).then(files => ...)` or `const files = await server.list_files(path)`. The `upload` async function can be used to upload a JavaScript `File` object to the Gradio server, returning a dictionary with `path` (the server-side file path) and `url` (the public URL to access the file), e.g. `const { path, url } = await upload(file)`.
+            js_on_load: A string representing the JavaScript code that will be executed when the component is loaded. The `element` variable refers to the HTML element of this component, and can be used to access children such as `element.querySelector()`. The `trigger` function can be used to trigger events, such as `trigger('click')`. The value and other props can be edited through `props`, e.g. `props.value = "new value"` which will re-render the HTML template. If `server_functions` is provided, a `server` object is also available in `js_on_load`, where each function is accessible as an async method, e.g. `server.list_files(path).then(files => ...)` or `const files = await server.list_files(path)`. The `upload` async function can be used to upload a JavaScript `File` object to the Gradio server, returning a dictionary with `path` (the server-side file path) and `url` (the public URL to access the file), e.g. `const { path, url } = await upload(file)`. The `watch` function can be used to observe prop changes when the component is an output to a Python event listener: `watch('value', () => { ... })` runs the callback after the template re-renders whenever `value` changes, or `watch(['value', 'color'], () => { ... })` to watch multiple props.`.
             apply_default_css: If True, default Gradio CSS styles will be applied to the HTML component.
             every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
             inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
diff --git a/js/html/Index.svelte b/js/html/Index.svelte
index 92ac3b47b14..8a9423d94c7 100644
--- a/js/html/Index.svelte
+++ b/js/html/Index.svelte
@@ -19,7 +19,7 @@
 	const gradio = new Gradio<HTMLEvents, HTMLProps>(props);

 	let _props = $derived({
-		value: gradio.props.value || "",
+		value: gradio.props.value ?? "",
 		label: gradio.shared.label,
 		visible: gradio.shared.visible,
 		...gradio.props.props
@@ -33,6 +33,30 @@
 		}
 	});

+	type WatchEntry = { props: string[]; callback: () => void };
+	let watch_entries: WatchEntry[] = [];
+
+	function watch(propOrProps: string | string[], callback: () => void): void {
+		const prop_list = Array.isArray(propOrProps) ? propOrProps : [propOrProps];
+		watch_entries.push({ props: prop_list, callback });
+	}
+
+	function fire_watchers(changed_keys: string[]): void {
+		const seen = new Set<WatchEntry>();
+		for (const entry of watch_entries) {
+			if (entry.props.some((k) => changed_keys.includes(k))) {
+				seen.add(entry);
+			}
+		}
+		for (const entry of seen) {
+			try {
+				entry.callback();
+			} catch (e) {
+				console.error("Error in watch callback:", e);
+			}
+		}
+	}
+
 	async function upload(file: File): Promise<{ path: string; url: string }> {
 		try {
 			const file_data = await prepare_files([file]);
@@ -112,6 +136,8 @@
 			component_class_name={gradio.props.component_class_name}
 			{upload}
 			server={gradio.shared.server}
+			watch_fn={watch}
+			{fire_watchers}
 			on:event={(e) => {
 				gradio.dispatch(e.detail.type, e.detail.data);
 			}}
diff --git a/js/html/shared/HTML.svelte b/js/html/shared/HTML.svelte
index 9904f6724ff..f0c6cad8407 100644
--- a/js/html/shared/HTML.svelte
+++ b/js/html/shared/HTML.svelte
@@ -1,5 +1,5 @@
 <script lang="ts">
-	import { createEventDispatcher, tick } from "svelte";
+	import { createEventDispatcher } from "svelte";
 	import Handlebars from "handlebars";
 	import type { Snippet } from "svelte";

@@ -16,6 +16,8 @@
 		component_class_name = "HTML",
 		upload = null,
 		server = {},
+		watch_fn = (_propOrProps: string | string[], _callback: () => void) => {},
+		fire_watchers = (_changedKeys: string[]) => {},
 		children
 	}: {
 		elem_classes: string[];
@@ -29,6 +31,8 @@
 		component_class_name: string;
 		upload: ((file: File) => Promise<{ path: string; url: string }>) | null;
 		server: Record<string, (...args: any[]) => Promise<any>>;
+		watch_fn?: (propOrProps: string | string[], callback: () => void) => void;
+		fire_watchers?: (changedKeys: string[]) => void;
 		children?: Snippet;
 	} = $props();

@@ -420,9 +424,10 @@
 						"props",
 						"server",
 						"upload",
+						"watch",
 						js_on_load
 					);
-					func(element, trigger, reactiveProps, server, upload_func);
+					func(element, trigger, reactiveProps, server, upload_func, watch_fn);
 				} catch (error) {
 					console.error("Error executing js_on_load:", error);
 				}
@@ -430,19 +435,23 @@
 		})();
 	});

-	// Props update effect
 	$effect(() => {
 		if (
 			reactiveProps &&
 			props &&
 			JSON.stringify(old_props) !== JSON.stringify(props)
 		) {
+			const changedKeys: string[] = [];
 			for (const key in props) {
-				if (reactiveProps[key] !== props[key]) {
-					reactiveProps[key] = props[key];
+				if (JSON.stringify(reactiveProps[key]) !== JSON.stringify(props[key])) {
+					changedKeys.push(key);
 				}
+				reactiveProps[key] = props[key];
 			}
 			old_props = props;
+			if (changedKeys.length > 0) {
+				queueMicrotask(() => fire_watchers(changedKeys));
+			}
 		}
 	});
 </script>

PATCH

echo "Patch applied successfully."
