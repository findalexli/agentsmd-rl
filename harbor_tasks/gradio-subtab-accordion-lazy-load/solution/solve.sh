#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Check if already applied by looking for accordion handling in _init.ts
if grep -q 'component.type === "accordion"' js/core/src/_init.ts; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/core/src/_init.ts b/js/core/src/_init.ts
index ac1d3d92ff..186292726d 100644
--- a/js/core/src/_init.ts
+++ b/js/core/src/_init.ts
@@ -935,6 +935,16 @@ function determine_visible_components(
 		) {
 			visible_components.add(layout.id);

+			const child_visible = process_children_visibility(
+				layout,
+				components,
+				parent_tabs_context
+			);
+			child_visible.forEach((id) => visible_components.add(id));
+		}
+	} else if (component.type === "accordion") {
+		visible_components.add(layout.id);
+		if (component.props.open !== false) {
 			const child_visible = process_children_visibility(
 				layout,
 				components,
diff --git a/js/core/src/init.svelte.ts b/js/core/src/init.svelte.ts
index 3a9bea3ac9..c4346f47c8 100644
--- a/js/core/src/init.svelte.ts
+++ b/js/core/src/init.svelte.ts
@@ -472,7 +472,7 @@ export class AppTree {
 		this.root = this.traverse(this.root!, [
 			(node) => {
 				if (node.id === id) {
-					make_visible_if_not_rendered(node, this.#hidden_on_startup);
+					make_visible_if_not_rendered(node, this.#hidden_on_startup, true);
 				}
 				return node;
 			},
@@ -483,14 +483,35 @@ export class AppTree {

 function make_visible_if_not_rendered(
 	node: ProcessedComponentMeta,
-	hidden_on_startup: Set<number>
+	hidden_on_startup: Set<number>,
+	is_target_node = false
 ): void {
 	node.props.shared_props.visible = hidden_on_startup.has(node.id)
 		? true
 		: node.props.shared_props.visible;
-	node.children.forEach((child) => {
-		make_visible_if_not_rendered(child, hidden_on_startup);
-	});
+
+	if (node.type === "tabs") {
+		const selectedId =
+			node.props.props.selected ?? node.props.props.initial_tabs?.[0]?.id;
+		node.children.forEach((child) => {
+			if (
+				child.type === "tabitem" &&
+				(child.props.props.id === selectedId || child.id === selectedId)
+			) {
+				make_visible_if_not_rendered(child, hidden_on_startup, false);
+			}
+		});
+	} else if (
+		node.type === "accordion" &&
+		node.props.props.open === false &&
+		!is_target_node
+	) {
+		// Don't recurse into closed accordion content
+	} else {
+		node.children.forEach((child) => {
+			make_visible_if_not_rendered(child, hidden_on_startup, false);
+		});
+	}
 }

 /**

PATCH

echo "Patch applied successfully."
