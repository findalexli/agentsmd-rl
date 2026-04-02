#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if the fix is already applied, exit
if grep -q 'update_parent_tabs_initial_tab' js/core/src/init.svelte.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/core/src/init.svelte.ts b/js/core/src/init.svelte.ts
index 144ec6349c1..ef0a5c7cfad 100644
--- a/js/core/src/init.svelte.ts
+++ b/js/core/src/init.svelte.ts
@@ -437,11 +437,6 @@ export class AppTree {
 		new_state: Partial<SharedProps> & Record<string, unknown>,
 		check_visibility: boolean = true
 	) {
-		// Visibility is tricky 😅
-		// If the component is not visible, it has not been rendered
-		// and so it has no _set_data callback
-		// Therefore, we need to traverse the tree and set the visible prop to true
-		// and then render it and its children. After that, we can call the _set_data callback
 		const node = find_node_by_id(this.root!, id);
 		let already_updated_visibility = false;
 		if (check_visibility && !node?.component) {
@@ -481,6 +476,12 @@ export class AppTree {
 			if ("value" in new_state && !dequal(old_value, new_state.value)) {
 				this.#event_dispatcher(id, "change", null);
 			}
+
+			// If this is a non-mounted tabitem, update the parent Tabs'
+			// initial_tabs so the tab button reflects the new state.
+			if (node?.type === "tabitem") {
+				this.#update_parent_tabs_initial_tab(id, node);
+			}
 		} else if (_set_data) {
 			_set_data(new_state);
 		}
@@ -508,6 +509,55 @@ export class AppTree {
 		});
 	}

+	/**
+	 * Updates the parent Tabs component's initial_tabs when a non-mounted
+	 * tabitem's props change. This ensures the tab button (rendered by
+	 * the Tabs component) reflects the updated state even though the
+	 * TabItem component itself is not mounted.
+	 */
+	#update_parent_tabs_initial_tab(
+		id: number,
+		node: ProcessedComponentMeta
+	): void {
+		const parent = find_parent(this.root!, id);
+		if (!parent || parent.type !== "tabs") return;
+
+		const initial_tabs = parent.props.props.initial_tabs as Tab[];
+		if (!initial_tabs) return;
+
+		const tab_index = initial_tabs.findIndex((t) => t.component_id === node.id);
+		if (tab_index === -1) return;
+
+		const i18n = node.props.props.i18n as ((str: string) => string) | undefined;
+		const raw_label = node.props.shared_props.label as string;
+		// Use original_visibility since the node's visible may have been
+		// set to false by the startup optimization for non-selected tabs.
+		const visible =
+			"original_visibility" in node
+				? (node.original_visibility as boolean)
+				: (node.props.shared_props.visible as boolean);
+		initial_tabs[tab_index] = {
+			label: i18n ? i18n(raw_label) : raw_label,
+			id: node.props.props.id as string,
+			elem_id: node.props.shared_props.elem_id,
+			visible,
+			interactive: node.props.shared_props.interactive,
+			scale: node.props.shared_props.scale || null,
+			component_id: node.id
+		};
+
+		// Trigger reactivity by replacing the array
+		parent.props.props.initial_tabs = [...initial_tabs];
+
+		// Also update via _set_data if the Tabs component is mounted
+		const parent_set_data = this.#set_callbacks.get(parent.id);
+		if (parent_set_data) {
+			parent_set_data({
+				initial_tabs: parent.props.props.initial_tabs
+			});
+		}
+	}
+
 	/**
 	 * Gets the current state of a component by its ID
 	 * @param id the ID of the component to get the state of
diff --git a/js/tabs/shared/Tabs.svelte b/js/tabs/shared/Tabs.svelte
index 8103238cfef..9134dc7c158 100644
--- a/js/tabs/shared/Tabs.svelte
+++ b/js/tabs/shared/Tabs.svelte
@@ -30,6 +30,25 @@
 	let overflow_menu_open = false;
 	let overflow_menu: HTMLElement;

+	// Track which tab orders have been registered by mounted TabItem components.
+	// Once a TabItem mounts and calls register_tab, it manages its own tab entry
+	// via _set_data -> register_tab, so _sync_tabs should not overwrite it.
+	let mounted_tab_orders: Set<number> = new Set();
+
+	// When initial_tabs changes (e.g. a non-mounted tab's props were updated),
+	// sync the internal tabs array so the tab buttons reflect the new state.
+	// Using a function call so the $: dependency is only on initial_tabs,
+	// not on tabs (which would cause a loop with register_tab).
+	$: _sync_tabs(initial_tabs);
+
+	function _sync_tabs(new_tabs: Tab[]): void {
+		for (let i = 0; i < new_tabs.length; i++) {
+			if (new_tabs[i] && !mounted_tab_orders.has(i)) {
+				tabs[i] = new_tabs[i];
+			}
+		}
+	}
+
 	$: has_tabs = tabs.length > 0;

 	let tab_nav_el: HTMLDivElement;
@@ -59,6 +78,7 @@

 	setContext(TABS, {
 		register_tab: (tab: Tab, order: number) => {
+			mounted_tab_orders.add(order);
 			tabs[order] = tab;

 			if ($selected_tab === false && tab.visible !== false && tab.interactive) {
@@ -68,6 +88,7 @@
 			return order;
 		},
 		unregister_tab: (tab: Tab, order: number) => {
+			mounted_tab_orders.delete(order);
 			if ($selected_tab === tab.id) {
 				$selected_tab = tabs[0]?.id || false;
 			}

PATCH

echo "Patch applied successfully."
