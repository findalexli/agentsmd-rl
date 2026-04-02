#!/bin/bash
set -euo pipefail

# Check if already applied (look for Header item emission pattern)
if grep -q "ActionListItemKind.Header" src/vs/platform/actionWidget/browser/actionList.ts && \
   grep -q "kind: ActionListItemKind.Header" src/vs/platform/actionWidget/browser/actionList.ts; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/platform/actionWidget/browser/actionList.ts b/src/vs/platform/actionWidget/browser/actionList.ts
index 533246fb8dd5e..8ace9a35339c9 100644
--- a/src/vs/platform/actionWidget/browser/actionList.ts
+++ b/src/vs/platform/actionWidget/browser/actionList.ts
@@ -1243,13 +1243,20 @@ export class ActionListWidget<T> extends Disposable {
 		const groupsWithActions = submenuGroups.filter(g => g.actions.length > 0);
 		for (let gi = 0; gi < groupsWithActions.length; gi++) {
 			const group = groupsWithActions[gi];
+			if (group.label) {
+				submenuItems.push({
+					kind: ActionListItemKind.Header,
+					group: { title: group.label },
+					label: group.label,
+				});
+			}
 			for (let ci = 0; ci < group.actions.length; ci++) {
 				const child = group.actions[ci];
 				submenuItems.push({
 					item: child,
 					kind: ActionListItemKind.Action,
 					label: child.label,
-					description: ci === 0 && group.label ? group.label : (child.tooltip || undefined),
+					description: child.tooltip || undefined,
 					group: { title: '', icon: ThemeIcon.fromId(child.checked ? Codicon.check.id : Codicon.blank.id) },
 					hideIcon: false,
 					hover: {},
diff --git a/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts b/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts
index c97ee90fcf2b2..3e182eca1e948 100644
--- a/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts
+++ b/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts
@@ -343,11 +343,11 @@ export class WorkspacePicker extends Disposable {
 		const submenuActions = [...providerMap.values()].map(({ provider, actions }) =>
 			new SubmenuAction(
 				`workspacePicker.browse.${provider.id}`,
-				provider.label,
-				actions.map(({ action, index }) => toAction({
+				'',
+				actions.map(({ action, index }, ci) => toAction({
 					id: `workspacePicker.browse.${index}`,
 					label: localize(`workspacePicker.browse`, "{0}...", action.label),
-					tooltip: '',
+					tooltip: ci === 0 ? provider.label : '',
 					run: () => this._executeBrowseAction(index),
 				})),
 			)
PATCH

echo "Patch applied successfully"
