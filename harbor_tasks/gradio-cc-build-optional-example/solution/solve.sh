#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -qF '...(pkg.exports["./example"]' js/preview/src/build.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/preview/src/build.ts b/js/preview/src/build.ts
index 1f4e5a7a16f..a63d5e9f5ef 100644
--- a/js/preview/src/build.ts
+++ b/js/preview/src/build.ts
@@ -74,14 +74,18 @@ export async function make_build({
 						join(source_dir, pkg.exports["."].gradio)
 					]
 				],
-				[
-					join(template_dir, "example"),
-					[
-						join(__dirname, "svelte_runtime_entry.js"),
-						join(source_dir, pkg.exports["./example"].gradio)
-					]
-				]
-			].filter(([_, path]) => !!path);
+				...(pkg.exports["./example"]
+					? [
+							[
+								join(template_dir, "example"),
+								[
+									join(__dirname, "svelte_runtime_entry.js"),
+									join(source_dir, pkg.exports["./example"].gradio)
+								]
+							]
+						]
+					: [])
+			];

 			for (const [out_path, entry_path] of exports) {
 				try {

PATCH

echo "Patch applied successfully."
