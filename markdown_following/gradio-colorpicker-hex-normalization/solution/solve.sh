#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if normalize_color already exists in utils.ts, patch is applied
if grep -q 'normalize_color' js/colorpicker/shared/utils.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/colorpicker/shared/Colorpicker.svelte b/js/colorpicker/shared/Colorpicker.svelte
index 039028c475c..7542056c454 100644
--- a/js/colorpicker/shared/Colorpicker.svelte
+++ b/js/colorpicker/shared/Colorpicker.svelte
@@ -4,7 +4,7 @@
 	import { BlockTitle } from "@gradio/atoms";
 	import { click_outside } from "./events";
 	import { Eyedropper } from "@gradio/icons";
-	import { hsva_to_rgba, format_color } from "./utils";
+	import { hsva_to_rgba, format_color, normalize_color } from "./utils";

 	let {
 		value = $bindable(),
@@ -206,7 +206,7 @@
 						type="text"
 						bind:value={color_string}
 						onchange={(e) => {
-							value = e.currentTarget.value;
+							value = normalize_color(e.currentTarget.value);
 						}}
 						onkeydown={(e) => {
 							if (e.key === "Enter") {
diff --git a/js/colorpicker/shared/utils.ts b/js/colorpicker/shared/utils.ts
index d918dce692c..054b03b31cd 100644
--- a/js/colorpicker/shared/utils.ts
+++ b/js/colorpicker/shared/utils.ts
@@ -21,7 +21,20 @@ export function hsva_to_rgba(hsva: {
 	const green = [x, chroma, chroma, x, m, m][index];
 	const blue = [m, m, x, chroma, chroma, x][index];

-	return `rgba(${red * 255}, ${green * 255}, ${blue * 255}, ${hsva.a})`;
+	return tinycolor({
+		r: red * 255,
+		g: green * 255,
+		b: blue * 255,
+		a: hsva.a
+	}).toHexString();
+}
+
+export function normalize_color(color: string): string {
+	const tc = tinycolor(color);
+	if (tc.isValid()) {
+		return tc.toHexString();
+	}
+	return color;
 }

 export function format_color(

PATCH

echo "Patch applied successfully."
