#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'self.head = head' gradio/components/html.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix <<'PATCH'
diff --git a/gradio/components/html.py b/gradio/components/html.py
index 2d477c2d001..803129b4ee2 100644
--- a/gradio/components/html.py
+++ b/gradio/components/html.py
@@ -75,6 +75,7 @@ def __init__(
         padding: bool = False,
         autoscroll: bool = False,
         buttons: list[Button] | None = None,
+        head: str | None = None,
         server_functions: list[Callable] | None = None,
         **props: Any,
     ):
@@ -86,6 +87,7 @@ def __init__(
             css_template: A string representing the CSS template for this component as a JS template string and Handlebars template. The CSS will be automatically scoped to this component, and rules outside a block will target the component's root element. The `${value}` tag will be replaced with the `value` parameter, and all other tags will be filled in with the values from `props`.
             js_on_load: A string representing the JavaScript code that will be executed when the component is loaded. The `element` variable refers to the HTML element of this component, and can be used to access children such as `element.querySelector()`. The `trigger` function can be used to trigger events, such as `trigger('click')`. The value and other props can be edited through `props`, e.g. `props.value = "new value"` which will re-render the HTML template. If `server_functions` is provided, a `server` object is also available in `js_on_load`, where each function is accessible as an async method, e.g. `server.list_files(path).then(files => ...)` or `const files = await server.list_files(path)`. The `upload` async function can be used to upload a JavaScript `File` object to the Gradio server, returning a dictionary with `path` (the server-side file path) and `url` (the public URL to access the file), e.g. `const { path, url } = await upload(file)`. The `watch` function can be used to observe prop changes when the component is an output to a Python event listener: `watch('value', () => { ... })` runs the callback after the template re-renders whenever `value` changes, or `watch(['value', 'color'], () => { ... })` to watch multiple props.`.
             apply_default_css: If True, default Gradio CSS styles will be applied to the HTML component.
+            head: A raw HTML string to inject into the document `<head>` before `js_on_load` runs. Typically used for `<script>` and `<link>` tags to load third-party libraries. Scripts are deduplicated by `src` and links by `href`, so multiple components requiring the same library won't load it twice.
             every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
             inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
             show_label: If True, the label will be displayed. If False, the label will be hidden.
@@ -108,6 +110,7 @@ def __init__(
         self.css_template = css_template
         self.js_on_load = js_on_load
         self.apply_default_css = apply_default_css
+        self.head = head
         self.min_height = min_height
         self.max_height = max_height
         self.padding = padding
@@ -261,7 +264,7 @@ def _to_publish_format(
             "js_on_load": self.js_on_load or "",
             "default_props": default_props,
             "python_code": python_code,
-            "head": head or "",
+            "head": head or self.head or "",
         }
         if repo_url:
             result["repo_url"] = repo_url
@@ -300,7 +303,7 @@ def push_to_hub(

         data = self._to_publish_format(
             name=name,
-            head=head,
+            head=head or self.head,
             description=description,
             author=author,
             tags=tags,
diff --git a/.agents/skills/gradio/SKILL.md b/.agents/skills/gradio/SKILL.md
index 78a53d584c6..35a0262ecdd 100644
--- a/.agents/skills/gradio/SKILL.md
+++ b/.agents/skills/gradio/SKILL.md
@@ -103,7 +103,7 @@ Creates a button that can be assigned arbitrary .click() events.
 ### `Markdown(value: str | I18nData | Callable | None = None, label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, rtl: bool = False, latex_delimiters: list[dict[str, str | bool]] | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", sanitize_html: bool = True, line_breaks: bool = False, header_links: bool = False, height: int | str | None = None, max_height: int | str | None = None, min_height: int | str | None = None, buttons: list[Literal['copy']] | None = None, container: bool = False, padding: bool = False)`
 Used to render arbitrary Markdown output.

-### `HTML(value: Any | Callable | None = None, label: str | I18nData | None = None, html_template: str = "${value}", css_template: str = "", js_on_load: str | None = "element.addEventListener('click', function() { trigger('click') });", apply_default_css: bool = True, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool = False, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", min_height: int | None = None, max_height: int | None = None, container: bool = False, padding: bool = False, autoscroll: bool = False, buttons: list[Button] | None = None, server_functions: list[Callable] | None = None, props: Any)`
+### `HTML(value: Any | Callable | None = None, label: str | I18nData | None = None, html_template: str = "${value}", css_template: str = "", js_on_load: str | None = "element.addEventListener('click', function() { trigger('click') });", apply_default_css: bool = True, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool = False, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", min_height: int | None = None, max_height: int | None = None, container: bool = False, padding: bool = False, autoscroll: bool = False, buttons: list[Button] | None = None, head: str | None = None, server_functions: list[Callable] | None = None, props: Any)`
 Creates a component with arbitrary HTML.

diff --git a/guides/03_building-with-blocks/06_custom-HTML-components.md b/guides/03_building-with-blocks/06_custom-HTML-components.md
index ee9cbfeb88c..bb9ebf1cd40 100644
--- a/guides/03_building-with-blocks/06_custom-HTML-components.md
+++ b/guides/03_building-with-blocks/06_custom-HTML-components.md
@@ -118,6 +118,27 @@ watch(['value', 'color'], () => {
 });
 ```

+## Loading Third-Party Scripts with `head`
+
+The `head` parameter lets you load external JavaScript or CSS libraries directly on the component. The `head` content is injected and loaded **before** `js_on_load` runs, so your code can immediately use the library.
+
+```python
+gr.HTML(
+    value=[30, 70, 45, 90, 60],
+    html_template="<canvas id='chart'></canvas>",
+    js_on_load="""
+        new Chart(element.querySelector('#chart'), {
+            type: 'bar',
+            data: {
+                labels: props.value.map((_, i) => 'Item ' + (i + 1)),
+                datasets: [{ label: 'Values', data: props.value }]
+            }
+        });
+    """,
+    head='<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
+)
+```
+
 ## Server Functions

PATCH

echo "Patch applied successfully."
