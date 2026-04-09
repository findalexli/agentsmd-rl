#!/usr/bin/env bash
set -euo pipefail

cd /workspace/svelte

# Idempotent: skip if already applied
if grep -q 'binding.scope !== context.state.scope' packages/svelte/src/compiler/phases/2-analyze/visitors/shared/function.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/svelte/src/compiler/phases/2-analyze/visitors/shared/function.js b/packages/svelte/src/compiler/phases/2-analyze/visitors/shared/function.js
index 4d93cd44e0d2..7bdb2243f2bd 100644
--- a/packages/svelte/src/compiler/phases/2-analyze/visitors/shared/function.js
+++ b/packages/svelte/src/compiler/phases/2-analyze/visitors/shared/function.js
@@ -10,7 +10,7 @@ export function visit_function(node, context) {
 		for (const [name] of context.state.scope.references) {
 			const binding = context.state.scope.get(name);

-			if (binding && binding.scope.function_depth < context.state.scope.function_depth) {
+			if (binding && binding.scope !== context.state.scope) {
 				context.state.expression.references.add(binding);
 			}
 		}

PATCH

echo "Patch applied successfully."
