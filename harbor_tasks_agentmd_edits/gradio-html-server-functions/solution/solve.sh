#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied (check for server_functions in SKILL.md)
if grep -q 'server_functions: list\[Callable\] | None = None' .agents/skills/gradio/SKILL.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full gold patch (code + config changes)
git apply - <<'PATCH'
diff --git a/.agents/skills/gradio/SKILL.md b/.agents/skills/gradio/SKILL.md
index eaa6732e99a..a45d62c8fee 100644
--- a/.agents/skills/gradio/SKILL.md
+++ b/.agents/skills/gradio/SKILL.md
@@ -103,7 +103,7 @@ Creates a button that can be assigned arbitrary .click() events.
 ### `Markdown(value: str | I18nData | Callable | None = None, label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, rtl: bool = False, latex_delimiters: list[dict[str, str | bool]] | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", sanitize_html: bool = True, line_breaks: bool = False, header_links: bool = False, height: int | str | None = None, max_height: int | str | None = None, min_height: int | str | None = None, buttons: list[Literal['copy']] | None = None, container: bool = False, padding: bool = False)`
 Used to render arbitrary Markdown output.

-### `HTML(value: Any | Callable | None = None, label: str | I18nData | None = None, html_template: str = "${value}", css_template: str = "", js_on_load: str | None = "element.addEventListener('click', function() { trigger('click') });", apply_default_css: bool = True, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool = False, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", min_height: int | None = None, max_height: int | None = None, container: bool = False, padding: bool = False, autoscroll: bool = False, buttons: list[Button] | None = None, props: Any)`
+### `HTML(value: Any | Callable | None = None, label: str | I18nData | None = None, html_template: str = "${value}", css_template: str = "", js_on_load: str | None = "element.addEventListener('click', function() { trigger('click') });", apply_default_css: bool = True, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool = False, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", min_height: int | None = None, max_height: int | None = None, container: bool = False, padding: bool = False, autoscroll: bool = False, buttons: list[Button] | None = None, server_functions: list[Callable] | None = None, props: Any)`
 Creates a component with arbitrary HTML.


diff --git a/.changeset/clear-eyes-look.md b/.changeset/clear-eyes-look.md
new file mode 100644
index 00000000000..1f4de7a3f90
--- /dev/null
+++ b/.changeset/clear-eyes-look.md
@@ -0,0 +1,8 @@
+---
+"@gradio/client": minor
+"@gradio/core": minor
+"@gradio/html": minor
+"gradio": minor
+---
+
+feat:Add server functions support to gr.HTML
diff --git a/client/js/src/client.ts b/client/js/src/client.ts
index 1a85c05f1e3..c62373da9d4 100644
--- a/client/js/src/client.ts
+++ b/client/js/src/client.ts
@@ -420,7 +420,7 @@ export class Client {
 	public async component_server(
 		component_id: number,
 		fn_name: string,
-		data: unknown[] | { binary: boolean; data: Record<string, any> }
+		data: unknown | { binary: boolean; data: Record<string, any> }
 	): Promise<unknown> {
 		if (!this.config) {
 			throw new Error(CONFIG_ERROR_MSG);
@@ -450,11 +450,12 @@ export class Client {

 		let body: FormData | string;

-		if ("binary" in data) {
+		if (typeof data === "object" && data !== null && "binary" in data) {
+			const _data = data as { binary: boolean; data: Record<string, any> };
 			body = new FormData();
-			for (const key in data.data) {
+			for (const key in _data.data) {
 				body.append(
 					key,
-					data.data[key] instanceof Blob
-						? data.data[key]
+					_data.data[key] instanceof Blob
+						? _data.data[key]
 						: JSON.stringify(data[key])
 				);
 			}
@@ -473,7 +474,8 @@ export class Client {
 				throw new Error(message);
 			}
 			const response = await response.json();
-			return response;
+
+			return response["data"];
 		});
 	}


diff --git a/gradio/components/html.py b/gradio/components/html.py
index 5d21860e574..6da57a3d21b 100644
--- a/gradio/components/html.py
+++ b/gradio/components/html.py
@@ -3,6 +3,7 @@
 from __future__ import annotations

 import re
+from collections.abc import Callable
 from pathlib import Path
 from typing import TYPE_CHECKING, Any

@@ -11,6 +12,7 @@ from gradio_client.documentation import document
 from gradio.components.component import Component
 from gradio.components.import_torch import _import_torch
 from gradio.data_classes import GradioRootModel
+from gradio.events import Dependency
 from gradio.utils import _get_route

 if TYPE_CHECKING:
@@ -41,6 +43,7 @@ class HTML(Component):
         autoscroll: bool = False,
         buttons: list[Button] | None = None,
         props: Any = None,
+        server_functions: list[Callable] | None = None,
     ):
         """
         Parameters:
@@ -51,6 +54,7 @@ class HTML(Component):
             autoscroll: If True, will automatically scroll to the bottom of the component when the value changes.
             buttons: A list of buttons to display in the component. Can be used to trigger events.
             props: An arbitrary value that can be accessed from within the `js_on_load` script via the `props` variable. The value is not accessible via an API or Python function call.
+            server_functions: A list of Python functions that can be called from within the `js_on_load` script via the `server` object.
         """
         self.html_template = html_template
         self.css_template = css_template
@@ -59,6 +63,16 @@ class HTML(Component):
         self.apply_default_css = apply_default_css
         self.buttons = buttons
         self.props = props
+        self.server_functions = server_functions
+        if self.server_functions is not None:
+            for func in self.server_functions:
+                event = Dependency(
+                    fn=func,
+                    inputs=[],
+                    outputs=[],
+                    queue=False,
+                )
+                self._ Event(event, f"__server_{func.__name__}")

     def preprocess(self, payload: str | None) -> str | None:
         """
@@ -89,5 +103,8 @@ class HTML(Component):
     def api_info(self) -> dict[str, str]:
         return {"type": "string"}

+    def __str__(self):
+        return f"HTML(value={self.value!r}, server_functions={[f.__name__ for f in self.server_functions] if self.server_functions else None})"
+
     def example_payload(self) -> Any:
         return "<h1>Hello HTML</h1>"

diff --git a/js/core/src/_init.ts b/js/core/src/_init.ts
index 69ba8dcb3a0..8b7c8ac4ea1 100644
--- a/js/core/src/_init.ts
+++ b/js/core/src/_init.ts
@@ -253,18 +253,7 @@ export function create_components(

 		if (component.server_fns) {
 			component.server_fns.forEach((fn) => {
-				const target = prop.__api__
-					? // @ts-ignore
-					  prop.target.__api__[fn]
-					: // @ts-ignore
-					  prop.target[fn];
-
-				if (target) {
-					// @ts-ignore
-					server[fn] = (...data: unknown[]) =>
-						// @ts-ignore
-						prop.target.__api__.run(fn, data);
-				}
+                server[fn] = (...data: unknown[]) => prop.target.component_server(prop.id, fn, data);
 			});
 		}


diff --git a/js/html/Index.svelte b/js/html/Index.svelte
index e3fa3d59e17..06b7e62228b 100644
--- a/js/html/Index.svelte
+++ b/js/html/Index.svelte
@@ -38,6 +38,7 @@
 		{elem_classes}
 		{visible}
 		{loading}
+		{server_fns}
 		{props}
 		{gradio}
 	/>
diff --git a/js/html/shared/HTML.svelte b/js/html/shared/HTML.svelte
index 24ae9d374a2..147f20be2d5 100644
--- a/js/html/shared/HTML.svelte
+++ b/js/html/shared/HTML.svelte
@@ -1,4 +1,5 @@
 <script lang="ts">
+	import { onMount } from "svelte";
 	import type { Gradio, SelectData } from "@gradio/utils";
 	import { handle }

@@ -14,6 +15,7 @@
 	export let loading = false;
 	export let props: Record<string, unknown> | undefined = undefined;
+    export let server_fns: string[] | undefined = undefined;

 	export let gradio: Gradio<{
 		change: never;
@@ -51,6 +53,12 @@
 		return content;
 	}

+	let server: Record<string, (...data: any[]) => Promise<any>> = {};
+	$: if (server_fns) {
+		server = Object.fromEntries(
+			server_fns.map((fn) => [fn, (...data: any[]) => gradio.component_server(fn, data)])
+		);
+	}

 	let element: HTMLDivElement;
 	let dispose: (() => void) | undefined;
@@ -68,7 +76,7 @@
 				dispose?.();
 			}

-			if (js_on_load) {
+			if (js_on_load || server_fns) {
 				const script = document.createElement("script");
 				script.type = "module";
 				const template = document.createElement("template";
@@ -82,7 +90,7 @@
 						trigger,
 						element,
 						props: props ?? {},
-                    	server: {}
+                    	server
 				};

 				script.textContent = `

diff --git a/guides/03_building-with-blocks/06_custom-HTML-components.md b/guides/03_building-with-blocks/06_custom-HTML-components.md
index 5f2f79e48f9..ebbe06bcb05 100644
--- a/guides/03_building-with-blocks/06_custom-HTML-components.md
+++ b/guides/03_building-with-blocks/06_custom-HTML-components.md
@@ -16,3 +16,11 @@ print("Run the following code in the terminal for the next guide")

 {{< demo "StarRating" >}}

+## Calling Server Functions from Custom HTML
+
+Gradio provides a way to call server-side Python functions directly from the JavaScript in your custom HTML components via the `server_functions` parameter. This allows you to create interactive HTML components that can fetch data from the backend or trigger server-side computations.
+
+Let's see how to use `server_functions` to create an interactive file browser that lists files on the server:
+
+{{< demo "html_server_functions" >}}
+
+The key concept is the `server` object that's available in `js_on_load` when `server_functions` is provided. This object contains methods for each function you pass to `server_functions`, allowing you to call them asynchronously from JavaScript.
diff --git a/demo/html_server_functions/run.ipynb b/demo/html_server_functions/run.ipynb
new file mode 100644
index 00000000000..99665343f3e
--- /dev/null
+++ b/demo/html_server_functions/run.ipynb
@@ -0,0 +1 @@
+!PY[run.ipynb].py
\ No newline at end of file
diff --git a/demo/html_server_functions/run.py b/demo/html_server_functions/run.py
new file mode 100644
index 00000000000..7da665baa8a
--- /dev/null
+++ b/demo/html_server_functions/run.py
@@ -0,0 +1,44 @@
+import os
+
+import gradio as gr
+
+
+def list_files(path):
+    try:
+        return os.listdir(path)
+    except (FileNotFoundError, PermissionError) as e:
+        return [f"Error: {e}"]
+
+
+with gr.Blocks() as demo:
+    gr.Markdown(
+        "# Server Functions Demo\nClick 'Load Files' to list files in the directory."
+    )
+    filetree = gr.HTML(
+        value=os.path.dirname(__file__),
+        html_template="""
+            <div>
+                <p>Directory: <strong>${value}</strong></p>
+                <div class='tree'></div>
+                <button class='load-btn'>Load Files</button>
+            </div>
+        """,
+        js_on_load="""
+            const loadBtn = element.querySelector('.load-btn');
+            const tree = element.querySelector('.tree');
+            loadBtn.addEventListener('click', async () => {
+                const files = await server.list_files(props.value);
+                tree.innerHTML = '';
+                files.forEach(file => {
+                    const fileEl = document.createElement('div');
+                    fileEl.textContent = file;
+                    tree.appendChild(fileEl);
+                });
+            });
+        """,
+        server_functions=[list_files],
+    )
+
+
+if __name__ == "__main__":
+    demo.launch()
+
diff --git a/demo/super_html/run.ipynb b/demo/super_html/run.ipynb
index cd9f16243f1..99665343f3e 100644
--- a/demo/super_html/run.ipynb
+++ b/demo/super_html/run.ipynb
@@ -1 +0,0 @@
-!PY[run.ipynb].py
\ No newline at end of file
+!PY[run.ipynb].py
\ No newline at end of file
diff --git a/demo/super_html/run.py b/demo/super_html/run.py
index dafa6aa0079..8a2e674882a 100644
--- a/demo/super_html/run.py
+++ b/demo/super_html/run.py
@@ -1,36 +1,139 @@
 import gradio as gr

-with gr.Blocks() as demo:
-    gr.Markdown("# Super HTML Demo")
-
-    with gr.Row():
-        with gr.Column():
-            gr.Markdown("## Component 1: Basic HTML")
-            html1 = gr.HTML(
-                value="<div style='padding: 20px; background: #f0f0f0;'>Hello World</div>"
-            )
-
-        with gr.Column():
-            gr.Markdown("## Component 2: HTML with Template")
-            html2 = gr.HTML(
-                value="Custom Value",
-                html_template="<div style='padding: 20px; color: blue;'>Value: ${value}</div>"
-            )
-
-    with gr.Row():
-        with gr.Column():
-            gr.Markdown("## Component 3: HTML with CSS")
-            html3 = gr.HTML(
-                value="Styled Content",
-                html_template="<div class='custom-box'>${value}</div>",
-                css_template="""
-                    .custom-box {
-                        padding: 20px;
-                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
-                        color: white;
-                        border-radius: 10px;
-                        font-size: 18px;
-                    }
-                """
-            )
-
-    with gr.Row():
-        with gr.Column():
-            gr.Markdown("## Component 4: Interactive HTML")
-            html4 = gr.HTML(
-                value="Click me!",
-                html_template="<button class='interactive-btn'>${value}</button>",
-                css_template="""
-                    .interactive-btn {
-                        padding: 15px 30px;
-                        font-size: 16px;
-                        background: #28a745;
-                        color: white;
-                        border: none;
-                        border-radius: 5px;
-                        cursor: pointer;
-                    }
-                    .interactive-btn:hover {
-                        background: #218838;
-                    }
-                """,
-            )
+
+def reverse_text(text):
+    return text[::-1]
+
+
+def get_ascii_art(emoji):
+    art_map = {
+        "heart": "❤️",
+        "star": "⭐",
+        "fire": "🔥",
+        "rocket": "🚀",
+        "party": "🎉",
+    }
+    return art_map.get(emoji, "❓")
+
+
+
+with gr.Blocks() as demo:
+    gr.Markdown("# Super HTML Demo - with Server Functions")
+
+    with gr.Row():
+        with gr.Column():
+            gr.Markdown("## Component 1: Basic HTML")
+            html1 = gr.HTML(
+                value="<div style='padding: 20px; background: #f0f0f0;'>Hello World</div>"
+            )
+
+        with gr.Column():
+            gr.Markdown("## Component 2: HTML with Template")
+            html2 = gr.HTML(
+                value="Custom Value",
+                html_template="<div style='padding: 20px; color: blue;'>Value: ${value}</div>"
+            )
+
+    with gr.Row():
+        with gr.Column():
+            gr.Markdown("## Component 3: HTML with CSS")
+            html3 = gr.HTML(
+                value="Styled Content",
+                html_template="<div class='custom-box'>${value}</div>",
+                css_template="""
+                    .custom-box {
+                        padding: 20px;
+                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
+                        color: white;
+                        border-radius: 10px;
+                        font-size: 18px;
+                    }
+                """
+            )
+
+    with gr.Row():
+        with gr.Column():
+            gr.Markdown("## Component 4: Interactive HTML")
+            html4 = gr.HTML(
+                value="Click me!",
+                html_template="<button class='interactive-btn'>${value}</button>",
+                css_template="""
+                    .interactive-btn {
+                        padding: 15px 30px;
+                        font-size: 16px;
+                        background: #28a745;
+                        color: white;
+                        border: none;
+                        border-radius: 5px;
+                        cursor: pointer;
+                    }
+                    .interactive-btn:hover {
+                        background: #218838;
+                    }
+                """,
+            )
+
+    with gr.Row():
+        with gr.Column():
+            gr.Markdown("## Component 5: Server Functions - Reverse Text")
+            html5 = gr.HTML(
+                value="Hello World",
+                html_template="""
+                    <div style='padding: 20px;'>
+                        <p>Original: <strong>${value}</strong></p>
+                        <input type="text" class="text-input" placeholder="Enter text to reverse" style="padding: 8px; margin-right: 10px;">
+                        <button class="reverse-btn">Reverse via Server</button>
+                        <p class="result" style="margin-top: 10px; color: green;'></p>
+                    </div>
+                """,
+                js_on_load="""
+                    const input = element.querySelector('.text-input');
+                    const btn = element.querySelector('.reverse-btn');
+                    const result = element.querySelector('.result');
+                    btn.addEventListener('click', async () => {
+                        const text = input.value || props.value;
+                        const reversed = await server.reverse_text(text);
+                        result.textContent = 'Reversed: ' + reversed;
+                    });
+                """,
+                server_functions=[reverse_text],
+            )
+
+    with gr.Row():
+        with gr.Column():
+            gr.Markdown("## Component 6: Server Functions - Emoji Lookup")
+            html6 = gr.HTML(
+                value="rocket",
+                html_template="""
+                    <div style='padding: 20px;'>
+                        <p>Current: <strong>${value}</strong></p>
+                        <select class="emoji-select" style="padding: 8px; margin-right: 10px;">
+                            <option value="heart">Heart</option>
+                            <option value="star">Star</option>
+                            <option value="fire">Fire</option>
+                            <option value="rocket">Rocket</option>
+                            <option value="party">Party</option>
+                        </select>
+                        <button class="lookup-btn">Get ASCII Art</button>
+                        <p class="result" style="margin-top: 10px; font-size: 36px;'></p>
+                    </div>
+                """,
+                js_on_load="""
+                    const select = element.querySelector('.emoji-select');
+                    const btn = element.querySelector('.lookup-btn');
+                    const result = element.querySelector('.result');
+                    btn.addEventListener('click', async () => {
+                        const emoji = select.value;
+                        const art = await server.get_ascii_art(emoji);
+                        result.textContent = art;
+                    });
+                """,
+                server_functions=[get_ascii_art],
+            )

 if __name__ == "__main__":
     demo.launch()
diff --git a/js/spa/test/super_html.spec.ts b/js/spa/test/spa/test/super_html.spec.ts
index 7a85a49d19a..0fdedab7ed0 100644
--- a/js/spa/test/super_html.spec.ts
+++ b/js/spa/test/super_html.spec.ts
@@ -43,4 +43,10 @@ test("interactive HTML triggers events", async ({ page }) => {
 	await page.click(".interactive-btn");
 	await expect(page.locator("text=Button clicked!")).toBeVisible();
 });
+
+test("server functions are callable from HTML", async ({ page }) => {
+	await page.goto("http://localhost:8765");
+	await page.click("text='Component 5: Server Functions - Reverse Text'");
+	await page.click("text=Reverse via Server");
+	await expect(page.locator("text=Reversed: dlroW olleH")).toBeVisible();
+});

PATCH

echo "Patch applied successfully."
