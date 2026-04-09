#!/usr/bin/env bash
set -euo pipefail

cd /workspace/svelte

# Idempotent: skip if already applied
if grep -q "node.type === 'EachBlock' || node.type === 'HtmlTag'" packages/svelte/src/compiler/phases/3-transform/client/visitors/shared/fragment.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/svelte/src/compiler/phases/3-transform/client/visitors/shared/fragment.js b/packages/svelte/src/compiler/phases/3-transform/client/visitors/shared/fragment.js
index bd3e70866292..f77af74f7ee3 100644
--- a/packages/svelte/src/compiler/phases/3-transform/client/visitors/shared/fragment.js
+++ b/packages/svelte/src/compiler/phases/3-transform/client/visitors/shared/fragment.js
@@ -101,7 +101,7 @@ export function process_children(nodes, initial, is_element, context) {
 			if (is_static_element(node)) {
 				skipped += 1;
 			} else if (
-				node.type === 'EachBlock' &&
+				(node.type === 'EachBlock' || node.type === 'HtmlTag') &&
 				nodes.length === 1 &&
 				is_element &&
 				// In case it's wrapped in async the async logic will want to skip sibling nodes up until the end, hence we cannot make this controlled
@@ -109,8 +109,6 @@ export function process_children(nodes, initial, is_element, context) {
 				!node.metadata.expression.is_async()
 			) {
 				node.metadata.is_controlled = true;
-			} else if (node.type === 'HtmlTag' && nodes.length === 1 && is_element) {
-				node.metadata.is_controlled = true;
 			} else {
 				const id = flush_node(
 					false,

PATCH

echo "Patch applied successfully."
