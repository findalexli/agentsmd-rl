#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

git apply - <<'PATCH'
diff --git a/js/dropdown/shared/Dropdown.svelte b/js/dropdown/shared/Dropdown.svelte
index 1a0bef8676..05349551d6 100644
--- a/js/dropdown/shared/Dropdown.svelte
+++ b/js/dropdown/shared/Dropdown.svelte
@@ -55,28 +55,29 @@
 	let show_options = $derived.by(() => {
 		return is_browser && filter_input === document.activeElement;
 	});
-	let choices_names: string[] = $derived.by(() => {
-		return choices.map((c) => c[0]);
-	});
-	let choices_values: (string | number)[] = $derived.by(() => {
-		return choices.map((c) => c[1]);
-	});
-	let [input_text, selected_index] = $derived.by(() => {
+	let choices_names = $derived(choices.map((c) => c[0]));
+	let choices_values = $derived(choices.map((c) => c[1]));
+	let input_text = $state("");
+	let selected_index: number | null = $state(null);
+
+	$effect(() => {
 		if (
 			value === undefined ||
 			value === null ||
 			(Array.isArray(value) && value.length === 0)
 		) {
-			return ["", null];
+			input_text = "";
+			selected_index = null;
 		} else if (choices_values.includes(value as string | number)) {
-			return [
-				choices_names[choices_values.indexOf(value as string | number)],
-				choices_values.indexOf(value as string | number)
-			];
+			input_text =
+				choices_names[choices_values.indexOf(value as string | number)];
+			selected_index = choices_values.indexOf(value as string | number);
 		} else if (allow_custom_value) {
-			return [value as string, null];
+			input_text = value as string;
+			selected_index = null;
 		} else {
-			return ["", null];
+			input_text = "";
+			selected_index = null;
 		}
 	});
 	// Use last_typed_value to track when the user has typed
@@ -88,6 +89,9 @@
 	// All of these are indices with respect to the choices array
 	let filtered_indices = $state(choices.map((_, i) => i));
 	let active_index: number | null = $state(null);
+	let selected_indices = $derived(
+		selected_index === null ? [] : [selected_index]
+	);

 	function handle_option_selected(index: any): void {
 		selected_index = parseInt(index);
@@ -227,7 +231,7 @@
 			{choices}
 			{filtered_indices}
 			{disabled}
-			selected_indices={selected_index === null ? [] : [selected_index]}
+			{selected_indices}
 			{active_index}
 			onchange={handle_option_selected}
 			onload={() => (initialized = true)}

PATCH

git add js/dropdown/shared/Dropdown.svelte
git commit -m "Apply fix for dropdown slowdown destructure issue"
