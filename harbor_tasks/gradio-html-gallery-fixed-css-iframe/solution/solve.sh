#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if needs_iframe already exists in utils.ts, patch is applied
if grep -q 'needs_iframe' js/_website/src/routes/custom-components/html-gallery/utils.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.changeset/fluffy-cows-happen.md b/.changeset/fluffy-cows-happen.md
new file mode 100644
index 0000000000..050c892abc
--- /dev/null
+++ b/.changeset/fluffy-cows-happen.md
@@ -0,0 +1,5 @@
+---
+"website": patch
+---
+
+fix:HTML Gallery Tweaks + Docs
diff --git a/guides/03_building-with-blocks/06_custom-HTML-components.md b/guides/03_building-with-blocks/06_custom-HTML-components.md
index 71e6389f28..02f236eda1 100644
--- a/guides/03_building-with-blocks/06_custom-HTML-components.md
+++ b/guides/03_building-with-blocks/06_custom-HTML-components.md
@@ -162,6 +162,41 @@ class MyComponent(gr.HTML):

 Use `GradioModel` when your data is a dictionary with named fields, or `GradioRootModel` when your data is a simple type (string, list, etc.) that doesn't need to be wrapped in a dictionary. By defining a `data_model`, your component automatically implements API methods.

+## Sharing Components with `push_to_hub`
+
+Once you've built a custom HTML component, you can share it with the community by pushing it to the [HTML Components Gallery](https://www.gradio.app/custom-components/html-gallery). The gallery lets anyone browse, interact with, and copy the Python code for community-contributed components.
+
+Call `push_to_hub` on any `gr.HTML` instance or subclass:
+
+```python
+star_rating = StarRating()
+star_rating.push_to_hub(
+    name="Star Rating",
+    description="Interactive 5-star rating with click-to-rate",
+    author="your-hf-username",
+    tags=["input", "rating"],
+    repo_url="https://github.com/your-username/your-repo",
+)
+```
+
+This opens a pull request on the gallery's HuggingFace dataset repo. Once approved, your component will appear in the gallery for others to discover and use.
+
+Tip: The  `push_to_hub` method has a `head` parameter that deserves special attention. If your component uses an external library loaded via the `head` parameter of `launch` (e.g. `head='<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'`), pass the same `head` string to `push_to_hub` so that the gallery can load those scripts when rendering your component.
+
+### Authentication
+
+You need a HuggingFace **write token** to push components. Either pass it directly:
+
+```python
+star_rating.push_to_hub(..., token="hf_xxxxx")
+```
+
+Or log in beforehand with the HuggingFace CLI, and the cached token will be used automatically:
+
+```bash
+huggingface-cli login
+```
+
 ## Security Considerations

 Keep in mind that using `gr.HTML` to create custom components involves injecting raw HTML and JavaScript into your Gradio app. Be cautious about using untrusted user input into `html_template` and `js_on_load`, as this could lead to cross-site scripting (XSS) vulnerabilities.
@@ -170,4 +205,6 @@ You should also expect that any Python event listeners that take your `gr.HTML`

 ## Next Steps

-Check out some examples of custom components that you can build in [this directory](https://github.com/gradio-app/gradio/tree/main/gradio/components/custom_html_components).
\ No newline at end of file
+- Browse the [HTML Components Gallery](https://www.gradio.app/custom-components/html-gallery) to see what the community has built and copy components into your own apps.
+- Check out more examples in [this directory](https://github.com/gradio-app/gradio/tree/main/gradio/components/custom_html_components).
+- Share your own components with `push_to_hub` to help others!
\ No newline at end of file
diff --git a/js/_website/src/routes/custom-components/html-gallery/+page.svelte b/js/_website/src/routes/custom-components/html-gallery/+page.svelte
index ce02759e14..36d69d3f77 100644
--- a/js/_website/src/routes/custom-components/html-gallery/+page.svelte
+++ b/js/_website/src/routes/custom-components/html-gallery/+page.svelte
@@ -2,6 +2,7 @@
 	import "$lib/assets/theme.css";
 	import MetaTags from "$lib/components/MetaTags.svelte";
 	import BaseHTML from "@gradio/html/base";
+	import { BaseButton } from "@gradio/button";
 	import CopyButton from "$lib/icons/CopyButton.svelte";
 	import { highlight } from "$lib/prism";
 	import { page } from "$app/stores";
@@ -9,9 +10,11 @@
 	import { tick, onMount } from "svelte";
 	import ComponentEntry from "./ComponentEntry.svelte";
 	import type { ManifestEntry, HTMLComponentEntry } from "./types";
+	import { needs_iframe, build_srcdoc } from "./utils";
+	import { theme } from "$lib/stores/theme";

 	const BASE_URL =
-		"https://huggingface.co/datasets/gradio/custom-html-gallery/resolve/main";
+		"https://huggingface.co/datasets/gradio/custom-html-gallery/resolve/refs%2Fpr%2F4";

 	let manifest: ManifestEntry[] = [];
 	let component_cache: Record<string, HTMLComponentEntry> = {};
@@ -133,6 +136,23 @@
 	$: maximized_highlighted = maximized_component
 		? highlight(maximized_component.python_code, "python")
 		: "";
+	$: maximized_use_iframe = maximized_component
+		? needs_iframe(maximized_component.css_template)
+		: false;
+
+	let modal_iframe_el: HTMLIFrameElement;
+	$: if (
+		browser &&
+		modal_iframe_el &&
+		maximized_component &&
+		maximized_use_iframe
+	) {
+		modal_iframe_el.srcdoc = build_srcdoc(
+			maximized_component,
+			maximized_props,
+			$theme === "dark"
+		);
+	}

 	async function open_maximized(comp: HTMLComponentEntry) {
 		maximized_component = comp;
@@ -271,14 +291,47 @@
 						</div>
 					{:else}
 						<div class="modal-component-container">
-							<BaseHTML
-								props={maximized_props}
-								html_template={maximized_component.html_template}
-								css_template={maximized_component.css_template}
-								js_on_load={maximized_component.js_on_load}
-								head={maximized_component.head || null}
-								apply_default_css={true}
-							/>
+							{#if maximized_use_iframe}
+								<iframe
+									bind:this={modal_iframe_el}
+									class="modal-iframe"
+									title="{maximized_component.name} preview"
+									sandbox="allow-scripts"
+								></iframe>
+							{:else if maximized_component.html_template.includes("@children")}
+								<BaseHTML
+									props={maximized_props}
+									html_template={maximized_component.html_template}
+									css_template={maximized_component.css_template}
+									js_on_load={maximized_component.js_on_load}
+									head={maximized_component.head || null}
+									apply_default_css={true}
+								>
+									<BaseButton
+										variant="primary"
+										size="md"
+										value={null}
+										visible={true}
+										link={null}
+										link_target="_self"
+										icon={null}
+										disabled={false}
+										scale={null}
+										min_width={undefined}
+										elem_id={null}
+										elem_classes={[]}>Click Me</BaseButton
+									>
+								</BaseHTML>
+							{:else}
+								<BaseHTML
+									props={maximized_props}
+									html_template={maximized_component.html_template}
+									css_template={maximized_component.css_template}
+									js_on_load={maximized_component.js_on_load}
+									head={maximized_component.head || null}
+									apply_default_css={true}
+								/>
+							{/if}
 						</div>
 					{/if}
 				</div>
@@ -457,6 +510,13 @@
 		width: 100%;
 	}

+	.modal-iframe {
+		width: 100%;
+		height: 600px;
+		border: none;
+		border-radius: 8px;
+	}
+
 	.modal-component-container :global(.prose),
 	.modal-component-container :global(.prose > div) {
 		max-width: 100% !important;
diff --git a/js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte b/js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte
index 52c857ed42..cb29c4a737 100644
--- a/js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte
+++ b/js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte
@@ -1,8 +1,12 @@
 <script lang="ts">
 	import BaseHTML from "@gradio/html/base";
+	import { BaseButton } from "@gradio/button";
 	import CopyButton from "$lib/icons/CopyButton.svelte";
 	import { highlight } from "$lib/prism";
+	import { browser } from "$app/environment";
+	import { theme } from "$lib/stores/theme";
 	import type { ManifestEntry, HTMLComponentEntry } from "./types";
+	import { needs_iframe, build_srcdoc } from "./utils";

 	export let manifest: ManifestEntry;
 	export let full_data: HTMLComponentEntry | null = null;
@@ -18,6 +22,15 @@
 	$: highlighted_html = component
 		? highlight(component.python_code, "python")
 		: "";
+	$: use_iframe = component ? needs_iframe(component.css_template) : false;
+	$: has_children_slot =
+		component?.html_template?.includes("@children") ?? false;
+	$: is_dark = $theme === "dark";
+
+	let iframe_el: HTMLIFrameElement;
+	$: if (browser && iframe_el && component && use_iframe) {
+		iframe_el.srcdoc = build_srcdoc(component, initial_props, is_dark);
+	}

 	function handle_maximize() {
 		if (component) {
@@ -131,14 +144,47 @@
 			{/if}
 		{:else if component}
 			<div class="component-container">
-				<BaseHTML
-					props={initial_props}
-					html_template={component.html_template}
-					css_template={component.css_template}
-					js_on_load={component.js_on_load}
-					head={component.head || null}
-					apply_default_css={true}
-				/>
+				{#if use_iframe}
+					<iframe
+						bind:this={iframe_el}
+						class="component-iframe"
+						title="{manifest.name} preview"
+						sandbox="allow-scripts"
+					></iframe>
+				{:else if has_children_slot}
+					<BaseHTML
+						props={initial_props}
+						html_template={component.html_template}
+						css_template={component.css_template}
+						js_on_load={component.js_on_load}
+						head={component.head || null}
+						apply_default_css={true}
+					>
+						<BaseButton
+							variant="primary"
+							size="md"
+							value={null}
+							visible={true}
+							link={null}
+							link_target="_self"
+							icon={null}
+							disabled={false}
+							scale={null}
+							min_width={undefined}
+							elem_id={null}
+							elem_classes={[]}>Click Me</BaseButton
+						>
+					</BaseHTML>
+				{:else}
+					<BaseHTML
+						props={initial_props}
+						html_template={component.html_template}
+						css_template={component.css_template}
+						js_on_load={component.js_on_load}
+						head={component.head || null}
+						apply_default_css={true}
+					/>
+				{/if}
 			</div>
 		{:else}
 			<div class="loading-placeholder">
@@ -291,6 +337,13 @@
 		color: var(--body-text-color);
 	}

+	.component-iframe {
+		width: 100%;
+		height: 280px;
+		border: none;
+		border-radius: 4px;
+	}
+
 	.component-container :global(.prose) {
 		--tw-prose-body: var(--body-text-color);
 		--tw-prose-headings: var(--body-text-color);
diff --git a/js/_website/src/routes/custom-components/html-gallery/utils.ts b/js/_website/src/routes/custom-components/html-gallery/utils.ts
index de6ed92743..4e122f2a2b 100644
--- a/js/_website/src/routes/custom-components/html-gallery/utils.ts
+++ b/js/_website/src/routes/custom-components/html-gallery/utils.ts
@@ -1,3 +1,5 @@
+import themeCSS from "$lib/assets/theme.css?raw";
+
 export function clickOutside(
 	element: HTMLDivElement,
 	callbackFunction: () => void
@@ -19,3 +21,90 @@ export function clickOutside(
 		}
 	};
 }
+
+/**
+ * Returns true if the component's CSS uses `position: fixed`,
+ * meaning it needs iframe isolation to render correctly in the gallery.
+ */
+export function needs_iframe(css_template: string | undefined): boolean {
+	if (!css_template) return false;
+	return /position\s*:\s*fixed/i.test(css_template);
+}
+
+/**
+ * Render a component's template string (Handlebars + JS template literals)
+ * the same way BaseHTML does, but synchronously in the parent page.
+ */
+function render_template(template: string, props: Record<string, any>): string {
+	try {
+		const keys = Object.keys(props);
+		const values = Object.values(props);
+		const fn = new Function(...keys, `return \`${template}\``);
+		return fn(...values);
+	} catch (e) {
+		console.error("Template rendering error:", e);
+		return "";
+	}
+}
+
+/**
+ * Build a self-contained HTML document string for rendering a component
+ * inside an iframe. Includes theme CSS, component CSS, rendered HTML,
+ * and js_on_load with a reactive props proxy.
+ */
+export function build_srcdoc(
+	component: {
+		html_template: string;
+		css_template: string;
+		js_on_load?: string | null;
+		head?: string | null;
+		default_props: Record<string, any>;
+	},
+	props: Record<string, any>,
+	dark: boolean = false
+): string {
+	const html = render_template(component.html_template, props);
+	const css = render_template(component.css_template, props);
+
+	// Escape </script in JS content to prevent premature script tag closure
+	const safe_props = JSON.stringify(props).replace(/<\/script/gi, "<\\/script");
+	const safe_js = (component.js_on_load || "").replace(
+		/<\/script/gi,
+		"<\\/script"
+	);
+
+	return `<!DOCTYPE html>
+<html class="${dark ? "dark" : ""}">
+<head>
+<meta charset="utf-8">
+<style>${themeCSS}</style>
+<style>
+html, body {
+	margin: 0;
+	padding: 0;
+	height: 100%;
+	background: var(--background-fill-primary, #0b0f19);
+	color: var(--body-text-color, #c5c7cb);
+	font-family: var(--font, system-ui, -apple-system, sans-serif);
+}
+#comp { ${css} }
+</style>
+${component.head || ""}
+</head>
+<body>
+<div id="comp">${html}</div>
+<script>
+(function(){
+var element = document.getElementById("comp");
+var props = new Proxy(${safe_props}, {
+	set: function(t, k, v) { t[k] = v; return true; }
+});
+function trigger() {}
+${safe_js}
+})();
+<\/script>
+</body>
+</html>`;
+}
+
+export { themeCSS };

PATCH

echo "Patch applied successfully."
