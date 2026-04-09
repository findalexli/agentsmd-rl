#!/usr/bin/env bash
set -euo pipefail

cd /workspace/svelte

# Idempotent: skip if already applied
if grep -q 'effect\.b =' packages/svelte/src/internal/client/reactivity/effects.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/svelte/src/internal/client/reactivity/effects.js b/packages/svelte/src/internal/client/reactivity/effects.js
index aeffeedddd81..54c8a17d790b 100644
--- a/packages/svelte/src/internal/client/reactivity/effects.js
+++ b/packages/svelte/src/internal/client/reactivity/effects.js
@@ -559,6 +559,7 @@ export function destroy_effect(effect, remove_dom = true) {
 		effect.fn =
 		effect.nodes =
 		effect.ac =
+		effect.b =
 			null;
 }


PATCH

echo "Patch applied successfully."
