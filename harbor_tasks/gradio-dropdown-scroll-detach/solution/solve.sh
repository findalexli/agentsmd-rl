#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency: check if already fixed
if grep -q 'let distance_from_top = \$state' js/dropdown/shared/DropdownOptions.svelte 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/dropdown/shared/DropdownOptions.svelte b/js/dropdown/shared/DropdownOptions.svelte
index 3d13b1d975..3a76f54b1a 100644
--- a/js/dropdown/shared/DropdownOptions.svelte
+++ b/js/dropdown/shared/DropdownOptions.svelte
@@ -26,9 +26,9 @@
 		onload?: () => void;
 	} = $props();

-	let distance_from_top: number;
-	let distance_from_bottom: number;
-	let input_height: number;
+	let distance_from_top = $state(0);
+	let distance_from_bottom = $state(0);
+	let input_height = $state(0);
 	let input_width = $state(0);
 	let refElement: HTMLDivElement;
 	let listElement: HTMLUListElement;

PATCH

echo "Patch applied successfully."
