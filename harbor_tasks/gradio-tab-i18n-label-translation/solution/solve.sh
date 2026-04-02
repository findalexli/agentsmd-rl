#!/usr/bin/env bash
set -euo pipefail

FILE="js/core/src/init.svelte.ts"

# Idempotency check: if the fix is already applied, exit
if grep -q 'i18n ? i18n(raw_label) : raw_label' "$FILE" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/js/core/src/init.svelte.ts b/js/core/src/init.svelte.ts
index 3cc1622ac9..3a9bea3ac9 100644
--- a/js/core/src/init.svelte.ts
+++ b/js/core/src/init.svelte.ts
@@ -719,8 +719,10 @@ function _gather_initial_tabs(
 		if (!("id" in node.props.props)) {
 			node.props.props.id = node.id;
 		}
+		const i18n = node.props.props.i18n as ((str: string) => string) | undefined;
+		const raw_label = node.props.shared_props.label as string;
 		initial_tabs[parent_tab_id].push({
-			label: node.props.shared_props.label as string,
+			label: i18n ? i18n(raw_label) : raw_label,
 			id: node.props.props.id as string,
 			elem_id: node.props.shared_props.elem_id,
 			visible: node.props.shared_props.visible as boolean,

PATCH

echo "Patch applied successfully."
