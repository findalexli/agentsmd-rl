#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if css_weight is already in fonts.py, patch was applied
if grep -q 'css_weight' gradio/themes/utils/fonts.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/themes/utils/fonts.py b/gradio/themes/utils/fonts.py
index 7a9b3be574..95f63e3093 100644
--- a/gradio/themes/utils/fonts.py
+++ b/gradio/themes/utils/fonts.py
@@ -86,21 +86,22 @@ def stylesheet(self) -> dict:
         css_template = textwrap.dedent("""
             @font-face {{
                 font-family: '{name}';
-                src: url('static/fonts/{file_name}/{file_name}-{weight}.woff2') format('woff2');
-                font-weight: {weight};
+                src: url('static/fonts/{file_name}/{file_name}-{file_weight}.woff2') format('woff2');
+                font-weight: {css_weight};
                 font-style: normal;
             }}
             """)
         css_rules = []
         for weight in self.weights:
-            weight_name = (
+            file_weight = (
                 "Regular" if weight == 400 else "Bold" if weight == 700 else str(weight)
             )
             css_rules.append(
                 css_template.format(
                     name=self.name,
                     file_name=self.name.replace(" ", ""),
-                    weight=weight_name,
+                    file_weight=file_weight,
+                    css_weight=weight,
                 )
             )
         return {"url": None, "css": "\n".join(css_rules)}
diff --git a/scripts/generate_theme.py b/scripts/generate_theme.py
index e4b8cc901c..e3738f5580 100644
--- a/scripts/generate_theme.py
+++ b/scripts/generate_theme.py
@@ -11,9 +11,15 @@
 parser.add_argument(
     "--theme", choices=["default", "glass", "monochrome", "soft"], default="default"
 )
+parser.add_argument(
+    "--website", action="store_true", help="Adjust paths for SvelteKit website"
+)
 args = parser.parse_args()

 ThemeClass = getattr(themes, args.theme.capitalize())
 css = ThemeClass()._get_theme_css()

+if args.website:
+    css = css.replace("url('static/", "url('/")
+
 args.outfile.write(css)
diff --git a/js/_website/package.json b/js/_website/package.json
index ac14eaa5eb..e5ad8c2809 100644
--- a/js/_website/package.json
+++ b/js/_website/package.json
@@ -3,7 +3,7 @@
 	"version": "0.71.1",
 	"private": true,
 	"scripts": {
-		"dev": "pip install boto3 markdown && python generate_jsons/generate.py && python ../../scripts/generate_theme.py --outfile ./src/lib/assets/theme.css && vite dev",
+		"dev": "pip install boto3 markdown && python generate_jsons/generate.py && python ../../scripts/generate_theme.py --website --outfile ./src/lib/assets/theme.css && vite dev",
 		"build": "vite build",
 		"preview": "vite preview",
 		"check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",

PATCH

echo "Patch applied successfully."
