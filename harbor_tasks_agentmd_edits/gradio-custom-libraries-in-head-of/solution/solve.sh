#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'head: str | None = None' gradio/components/html.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply patch adding head parameter to gr.HTML
git apply - <<'PATCH'
diff --git a/gradio/components/html.py b/gradio/components/html.py
index abc123..def456 100644
--- a/gradio/components/html.py
+++ b/gradio/components/html.py
@@ -80,6 +80,7 @@ class HTML(BlockContext, Component):
         autoscroll: bool = False,
         buttons: list[Button] | None = None,
         server_functions: list[Callable] | None = None,
+        head: str | None = None,
         **props: Any,
     ):
         """
@@ -104,6 +105,9 @@ class HTML(BlockContext, Component):
             server.list_files(path).then(files => ...) or `const files = await server.list_files(path)`. The `upload` async function can be used to upload a JavaScript `File` object to the Gradio server, returning a dictionary with `path` (the server-side file path) and `url` (the public URL to access the file), e.g., `const { path, url } = await upload(file)`. The `watch` function can be used to observe prop changes when the component is an output to a Python event listener: `watch('value', () => { ... })` runs the callback after the template re-renders whenever `value` changes, or `watch(['value', 'color'], () => { ... })` to watch multiple props.`.
             apply_default_css: If True, default Gradio CSS styles will be applied to the HTML component.
+            head: A raw HTML string to inject into the document `<head>` before `js_on_load` runs. Typically used for `<script>` and `<link>` tags to load third-party libraries. Scripts are deduplicated by `src` and links by `href`, so multiple components requiring the same library won't load it twice.
             every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
             inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
@@ -132,6 +136,7 @@ class HTML(BlockContext, Component):
         self.apply_default_css = apply_default_css
         self.html_template = html_template
         self.css_template = css_template
+        self.head = head
         self.js_on_load = js_on_load
         self.server_functions = server_functions
         self.preserved_by_key = preserved_by_key
@@ -154,6 +159,7 @@ class HTML(BlockContext, Component):
             "html_template": self.html_template,
             "css_template": self.css_template,
             "js_on_load": self.js_on_load,
+            "head": self.head,
             "key": self.key,
             "label": self.label,
             "likeable": self.likeable,

PATCH

echo "Patch applied successfully."
