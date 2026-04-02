#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied (idempotency check)
# The fix changes a hardcoded `true` to `items.length > 1` in changesView.ts
if grep -q "openFileItem(e.element, items, e.sideBySide, !!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, items.length > 1);" src/vs/sessions/contrib/changes/browser/changesView.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the fix using the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/changes/browser/changesView.ts b/src/vs/sessions/contrib/changes/browser/changesView.ts
index 80315bb486dfe..5ece08cf7fa6c 100644
--- a/src/vs/sessions/contrib/changes/browser/changesView.ts
+++ b/src/vs/sessions/contrib/changes/browser/changesView.ts
@@ -1063,7 +1063,7 @@ export class ChangesViewPane extends ViewPane {
 				}

 				const items = combinedEntriesObs.get();
-				openFileItem(e.element, items, e.sideBySide, !!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, true);
+				openFileItem(e.element, items, e.sideBySide, !!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, items.length > 1);
 			}));
 		}

diff --git a/src/vs/sessions/contrib/changes/browser/media/changesView.css b/src/vs/sessions/contrib/changes/browser/media/changesView.css
index 0cb63934128b6..2cb02c7115192 100644
--- a/src/vs/sessions/contrib/changes/browser/media/changesView.css
+++ b/src/vs/sessions/contrib/changes/browser/media/changesView.css
@@ -243,21 +243,21 @@
 }

 /* Action bar in list rows */
-.changes-view-body .monaco-list-row .chat-collapsible-list-action-bar {
+.chat-editing-session-list .monaco-list-row .chat-collapsible-list-action-bar {
 	padding-left: 5px;
 	display: none;
 }

-.changes-view-body .monaco-list-row:hover .chat-collapsible-list-action-bar:not(.has-no-actions),
-.changes-view-body .monaco-list-row.focused .chat-collapsible-list-action-bar:not(.has-no-actions),
-.changes-view-body .monaco-list-row.selected .chat-collapsible-list-action-bar:not(.has-no-actions) {
+.chat-editing-session-list .monaco-list-row:hover .chat-collapsible-list-action-bar:not(.has-no-actions),
+.chat-editing-session-list .monaco-list-row.focused .chat-collapsible-list-action-bar:not(.has-no-actions),
+.chat-editing-session-list .monaco-list-row.selected .chat-collapsible-list-action-bar:not(.has-no-actions) {
 	display: inherit;
 }

 /* Hide diff stats on hover/focus/select when toolbar has actions */
-.changes-view-body .monaco-list-row:hover .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
-.changes-view-body .monaco-list-row.focused .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
-.changes-view-body .monaco-list-row.selected .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts {
+.chat-editing-session-list .monaco-list-row:hover .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
+.chat-editing-session-list .monaco-list-row.focused .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
+.chat-editing-session-list .monaco-list-row.selected .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts {
 	display: none;
 }
PATCH

echo "Patch applied successfully!"
