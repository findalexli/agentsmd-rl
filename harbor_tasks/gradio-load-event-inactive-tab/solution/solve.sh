#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency: check if the pending_updates map already exists
if grep -q '#pending_updates' js/core/src/init.svelte.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/core/src/init.svelte.ts b/js/core/src/init.svelte.ts
index c4346f47c8..d7fb4e8e00 100644
--- a/js/core/src/init.svelte.ts
+++ b/js/core/src/init.svelte.ts
@@ -67,6 +67,7 @@ export class AppTree {

 	#get_callbacks = new Map<number, get_data_type>();
 	#set_callbacks = new Map<number, set_data_type>();
+	#pending_updates = new Map<number, Record<string, unknown>>();
 	#event_dispatcher: (id: number, event: string, data: unknown) => void;
 	component_ids: number[];
 	initial_tabs: Record<number, Tab[]> = {};
@@ -195,6 +196,21 @@ export class AppTree {
 		this.#set_callbacks.set(id, _set_data);
 		this.#get_callbacks.set(id, _get_data);
 		this.components_to_register.delete(id);
+
+		// Apply any pending updates that were stored while the component
+		// was not yet mounted (e.g. hidden in an inactive tab).
+		// We must apply AFTER tick() so that the Gradio class's $effect
+		// (which syncs from node props) has already run. Otherwise the
+		// $effect would overwrite the values we set here.
+		const pending = this.#pending_updates.get(id);
+		if (pending) {
+			this.#pending_updates.delete(id);
+			tick().then(() => {
+				const _set = this.#set_callbacks.get(id);
+				if (_set) _set(pending);
+			});
+		}
+
 		if (this.components_to_register.size === 0 && !this.resolved) {
 			this.resolved = true;
 			this.ready_resolve();
@@ -429,11 +445,24 @@ export class AppTree {
 			const old_value = node?.props.props.value;
 			// @ts-ignore
 			const new_props = create_props_shared_props(new_state);
-			node!.props.shared_props = {
-				...node?.props.shared_props,
-				...new_props.shared_props
-			};
-			node!.props.props = { ...node?.props.props, ...new_props.props };
+			// Modify props in-place instead of replacing the entire object.
+			// Replacing with a new object via spread can cause Svelte 5's
+			// deep $state proxy to lose track of the values during async
+			// component mounting/revival.
+			for (const key in new_props.shared_props) {
+				// @ts-ignore
+				node!.props.shared_props[key] = new_props.shared_props[key];
+			}
+			for (const key in new_props.props) {
+				// @ts-ignore
+				node!.props.props[key] = new_props.props[key];
+			}
+
+			// Also store as pending so the value can be applied via _set_data
+			// when the component eventually mounts and registers
+			const existing = this.#pending_updates.get(id) || {};
+			this.#pending_updates.set(id, { ...existing, ...new_state });
+
 			if ("value" in new_state && !dequal(old_value, new_state.value)) {
 				this.#event_dispatcher(id, "change", null);
 			}
@@ -469,15 +498,21 @@ export class AppTree {
 	}

 	async render_previously_invisible_children(id: number) {
-		this.root = this.traverse(this.root!, [
-			(node) => {
-				if (node.id === id) {
-					make_visible_if_not_rendered(node, this.#hidden_on_startup, true);
-				}
-				return node;
-			},
-			(node) => handle_visibility(node, this.#config.api_url)
-		]);
+		const node = find_node_by_id(this.root!, id);
+		if (!node) return;
+
+		// Check if this node or any of its descendants need to be made visible.
+		// If not, skip entirely to avoid unnecessary reactive updates
+		// from mutating the tree through the $state proxy.
+		if (
+			!this.#hidden_on_startup.has(node.id) &&
+			!has_hidden_descendants(node, this.#hidden_on_startup)
+		) {
+			return;
+		}
+
+		make_visible_if_not_rendered(node, this.#hidden_on_startup, true);
+		load_components(node, this.#config.api_url);
 	}
 }

@@ -514,6 +549,24 @@ function make_visible_if_not_rendered(
 	}
 }

+function has_hidden_descendants(
+	node: ProcessedComponentMeta,
+	hidden_on_startup: Set<number>
+): boolean {
+	for (const child of node.children) {
+		if (hidden_on_startup.has(child.id)) return true;
+		if (has_hidden_descendants(child, hidden_on_startup)) return true;
+	}
+	return false;
+}
+
+function load_components(node: ProcessedComponentMeta, api_url: string): void {
+	if (node.props.shared_props.visible && !node.component) {
+		node.component = get_component(node.type, node.component_class_id, api_url);
+	}
+	node.children.forEach((child) => load_components(child, api_url));
+}
+
 /**
  * Process the server function names and return a dictionary of functions
  * @param id the component id

PATCH

echo "Patch applied successfully."
