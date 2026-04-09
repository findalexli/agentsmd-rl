#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied (check for server_functions parameter)
if grep -q 'server_functions: list\[Callable\]' gradio/components/html.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Patch 1: gradio/components/html.py — add server_functions support
git apply - <<'PATCH1'
diff --git a/gradio/components/html.py b/gradio/components/html.py
index 5c0b7ab355e..bc7a35b0da4 100644
--- a/gradio/components/html.py
+++ b/gradio/components/html.py
@@ -11,7 +11,7 @@
 from gradio_client.documentation import document

 from gradio.blocks import BlockContext
-from gradio.components.base import Component
+from gradio.components.base import Component, server
 from gradio.components.button import Button
 from gradio.events import all_events
 from gradio.i18n import I18nData
@@ -74,6 +74,7 @@ def __init__(
         padding: bool = False,
         autoscroll: bool = False,
         buttons: list[Button] | None = None,
+        server_functions: list[Callable] | None = None,
         **props: Any,
     ):
         """
@@ -82,7 +83,7 @@ def __init__(
             label: The label for this component. Is used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
             html_template: A string representing the HTML template for this component as a JS template string and Handlebars template. The `${value}` tag will be replaced with the `value` parameter, and all other tags will be filled in with the values from `props`. This element can have children when used in a `with gr.HTML(...):` context, and the children will be rendered to replace `@children` substring, which cannot be nested inside any HTML tags.
             css_template: A string representing the CSS template for this component as a JS template string and Handlebars template. The CSS will be automatically scoped to this component, and rules outside a block will target the component's root element. The `${value}` tag will be replaced with the `value` parameter, and all other tags will be filled in with the values from `props`.
-            js_on_load: A string representing the JavaScript code that will be executed when the component is loaded. The `element` variable refers to the HTML element of this component, and can be used to access children such as `element.querySelector()`. The `trigger` function can be used to trigger events, such as `trigger('click')`. The value and other props can be edited through `props`, e.g. `props.value = "new value"` which will re-render the HTML template.
+            js_on_load: A string representing the JavaScript code that will be executed when the component is loaded. The `element` variable refers to the HTML element of this component, and can be used to access children such as `element.querySelector()`. The `trigger` function can be used to trigger events, such as `trigger('click')`. The value and other props can be edited through `props`, e.g. `props.value = "new value"` which will re-render the HTML template. If `server_functions` is provided, a `server` object is also available in `js_on_load`, where each function is accessible as an async method, e.g. `server.list_files(path).then(files => ...)` or `const files = await server.list_files(path)`.
             apply_default_css: If True, default Gradio CSS styles will be applied to the HTML component.
             every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
             inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
@@ -99,6 +100,7 @@ def __init__(
             padding: If True, the HTML component will have a certain padding (set by the `--block-padding` CSS variable) in all directions. Default is False.
             autoscroll: If True, will automatically scroll to the bottom of the component when the content changes, unless the user has scrolled up. If False, will not scroll to the bottom when the content changes.
             buttons: A list of gr.Button() instances to show in the top right corner of the component. Custom buttons will appear in the toolbar with their configured icon and/or label, and clicking them will trigger any .click() events registered on the button.
+            server_functions: A list of Python functions that can be called from `js_on_load` via the `server` object. For example, if you pass `server_functions=[my_func]`, you can call `server.my_func(arg1, arg2)` in your `js_on_load` code. Each function becomes an async method that sends the call to the Python backend and returns the result.
             props: Additional keyword arguments to pass into the HTML and CSS templates for rendering.
         """
         self.html_template = html_template
@@ -136,6 +138,12 @@ def __init__(
             container=container,
         )
         self.buttons = set_default_buttons(buttons, None)
+        if server_functions:
+            for fn in server_functions:
+                decorated = server(fn)
+                fn_name = getattr(fn, "__name__", str(fn))
+                setattr(self, fn_name, decorated)
+                self.server_fns.append(decorated)

     def example_payload(self) -> Any:
         return "<p>Hello</p>"
PATCH1

# Patch 2: js/html/Index.svelte — pass server to shared component
git apply - <<'PATCH2'
diff --git a/js/html/Index.svelte b/js/html/Index.svelte
index d522fbd4ac7..cd529a2df87 100644
--- a/js/html/Index.svelte
+++ b/js/html/Index.svelte
@@ -89,6 +89,7 @@
 			autoscroll={gradio.shared.autoscroll}
 			apply_default_css={gradio.props.apply_default_css}
 			component_class_name={gradio.props.component_class_name}
+			server={gradio.shared.server}
 			on:event={(e) => {
 				gradio.dispatch(e.detail.type, e.detail.data);
 			}}
PATCH2

# Patch 3: js/html/shared/HTML.svelte — add server to js_on_load
git apply - <<'PATCH3'
diff --git a/js/html/shared/HTML.svelte b/js/html/shared/HTML.svelte
index df62146da00..f800f4fa067 100644
--- a/js/html/shared/HTML.svelte
+++ b/js/html/shared/HTML.svelte
@@ -14,6 +14,7 @@
 		autoscroll = false,
 		apply_default_css = true,
 		component_class_name = "HTML",
+		server = {},
 		children
 	}: {
 		elem_classes: string[];
@@ -25,6 +26,7 @@
 		autoscroll: boolean;
 		apply_default_css: boolean;
 		component_class_name: string;
+		server: Record<string, (...args: any[]) => Promise<any>>;
 		children?: Snippet;
 	} = $props();

@@ -405,8 +407,14 @@
 			}
 			if (js_on_load && element) {
 				try {
-					const func = new Function("element", "trigger", "props", js_on_load);
-					func(element, trigger, reactiveProps);
+					const func = new Function(
+						"element",
+						"trigger",
+						"props",
+						"server",
+						js_on_load
+					);
+					func(element, trigger, reactiveProps, server);
 				} catch (error) {
 					console.error("Error executing js_on_load:", error);
 				}
PATCH3

# Patch 4: .agents/skills/gradio/SKILL.md — document server_functions
git apply - <<'PATCH4'
diff --git a/.agents/skills/gradio/SKILL.md b/.agents/skills/gradio/SKILL.md
index eaa6732e99a..c45d62c8fee 100644
--- a/.agents/skills/gradio/SKILL.md
+++ b/.agents/skills/gradio/SKILL.md
@@ -103,7 +103,7 @@ Creates a button that can be assigned arbitrary .click() events.
 ### `Markdown(value: str | I18nData | Callable | None = None, label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, rtl: bool = False, latex_delimiters: list[dict[str, str | bool]] | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", sanitize_html: bool = True, line_breaks: bool = False, header_links: bool = False, height: int | str | None = None, max_height: int | str | None = None, min_height: int | str | None = None, buttons: list[Literal['copy']] | None = None, container: bool = False, padding: bool = False)`
 Used to render arbitrary Markdown output.

-### `HTML(value: Any | Callable | None = None, label: str | I18nData | None = None, html_template: str = "${value}", css_template: str = "", js_on_load: str | None = "element.addEventListener('click', function() { trigger('click') });", apply_default_css: bool = True, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool = False, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", min_height: int | None = None, max_height: int | str | None = None, container: bool = False, padding: bool = False, autoscroll: bool = False, buttons: list[Button] | None = None, props: Any)`
+### `HTML(value: Any | Callable | None = None, label: str | I18nData | None = None, html_template: str = "${value}", css_template: str = "", js_on_load: str | None = "element.addEventListener('click', function() { trigger('click') });", apply_default_css: bool = True, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool = False, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", min_height: int | None = None, max_height: int | str | None = None, container: bool = False, padding: bool = False, autoscroll: bool = False, buttons: list[Button] | None = None, server_functions: list[Callable] | None = None, props: Any)`
 Creates a component with arbitrary HTML.
@@ -476,3 +476,57 @@ class StarRating(gr.HTML):
         super().__init__(value=value, label=label, html_template=html_template, css_template=css_template, js_on_load=js_on_load, **kwargs)

     def api_info(self):
         return {"type": "integer", "minimum": 0, "maximum": 5}
+
+
+## Server Functions
+
+You can call Python functions directly from your `js_on_load` code using the `server_functions` parameter. Pass a list of Python functions to `server_functions`, and they become available as async methods on a `server` object inside `js_on_load`.
+
+Example:
+```python
+import os
+import gradio as gr
+
+def list_files(path):
+    try:
+        return os.listdir(path)
+    except (FileNotFoundError, PermissionError) as e:
+        return [f"Error: {e}"]
+
+with gr.Blocks() as demo:
+    gr.Markdown("# Server Functions Demo")
+    filetree = gr.HTML(
+        value=os.path.abspath(''),
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
+if __name__ == "__main__":
+    demo.launch()
+```
+
+Each function in `server_functions` becomes an async method on the `server` object:
+- Function name becomes the method name
+- Arguments are passed to the Python function
+- Returns a Promise that resolves with the function's return value
+- Use `await server.func_name(args)` or `server.func_name(args).then(result => ...)`
PATCH4

echo "Patch applied successfully."
