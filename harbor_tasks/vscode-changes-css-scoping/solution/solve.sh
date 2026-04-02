#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if fix is already applied
if grep -q 'changes-file-list' src/vs/sessions/contrib/changes/browser/changesView.ts; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the patch for CSS selector scoping
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/changes/browser/changesView.ts b/src/vs/sessions/contrib/changes/browser/changesView.ts
index 5ece08cf7fa6c..f44fcb7d469c7 100644
--- a/src/vs/sessions/contrib/changes/browser/changesView.ts
+++ b/src/vs/sessions/contrib/changes/browser/changesView.ts
@@ -538,7 +538,7 @@ export class ChangesViewPane extends ViewPane {
 		this.changesProgressBar.stop().hide();
 
 		// List container
-		this.listContainer = dom.append(this.contentContainer, $('.chat-editing-session-list'));
+		this.listContainer = dom.append(this.contentContainer, $('.changes-file-list'));
 
 		// Welcome message for empty state
 		this.welcomeContainer = dom.append(this.contentContainer, $('.changes-welcome'));
@@ -1194,7 +1194,7 @@ export class ChangesViewPane extends ViewPane {
 	): IDisposable {
 		const disposables = new DisposableStore();
 
-		container.classList.add('chat-editing-session-list');
+		container.classList.add('changes-file-list');
 
 		const tree = this.createChangesTree(container, Event.None, disposables, () => tree.getSelection().filter(item => !!item && isChangesFileItem(item)));
 
diff --git a/src/vs/sessions/contrib/changes/browser/media/changesView.css b/src/vs/sessions/contrib/changes/browser/media/changesView.css
index 2cb02c7115192..82cbc89c69d53 100644
--- a/src/vs/sessions/contrib/changes/browser/media/changesView.css
+++ b/src/vs/sessions/contrib/changes/browser/media/changesView.css
@@ -215,21 +215,21 @@
 }
 
 /* List container */
-.changes-view-body .chat-editing-session-list {
+.changes-file-list {
 	overflow: hidden;
 }
 
 /* Make the vertical scrollbar overlay on top of content instead of shifting it */
-.changes-view-body .chat-editing-session-list .monaco-scrollable-element > .scrollbar.vertical {
+.changes-file-list .monaco-scrollable-element > .scrollbar.vertical {
 	z-index: 1;
 }
 
-.changes-view-body .chat-editing-session-list .monaco-scrollable-element > .monaco-list-rows {
+.changes-file-list .monaco-scrollable-element > .monaco-list-rows {
 	width: 100% !important;
 }
 
 /* Remove tree indentation padding for hidden twisties (both list and tree mode) */
-.changes-view-body .chat-editing-session-list .monaco-tl-twistie.force-no-twistie {
+.changes-file-list .monaco-tl-twistie.force-no-twistie {
 	padding-left: 0 !important;
 }
 
@@ -243,26 +243,26 @@
 }
 
 /* Action bar in list rows */
-.chat-editing-session-list .monaco-list-row .chat-collapsible-list-action-bar {
+.changes-file-list .monaco-list-row .chat-collapsible-list-action-bar {
 	padding-left: 5px;
 	display: none;
 }
 
-.chat-editing-session-list .monaco-list-row:hover .chat-collapsible-list-action-bar:not(.has-no-actions),
-.chat-editing-session-list .monaco-list-row.focused .chat-collapsible-list-action-bar:not(.has-no-actions),
-.chat-editing-session-list .monaco-list-row.selected .chat-collapsible-list-action-bar:not(.has-no-actions) {
+.changes-file-list .monaco-list-row:hover .chat-collapsible-list-action-bar:not(.has-no-actions),
+.changes-file-list .monaco-list-row.focused .chat-collapsible-list-action-bar:not(.has-no-actions),
+.changes-file-list .monaco-list-row.selected .chat-collapsible-list-action-bar:not(.has-no-actions) {
 	display: inherit;
 }
 
 /* Hide diff stats on hover/focus/select when toolbar has actions */
-.chat-editing-session-list .monaco-list-row:hover .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
-.chat-editing-session-list .monaco-list-row.focused .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
-.chat-editing-session-list .monaco-list-row.selected .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts {
+.changes-file-list .monaco-list-row:hover .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
+.changes-file-list .monaco-list-row.focused .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts,
+.changes-file-list .monaco-list-row.selected .monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) .working-set-line-counts {
 	display: none;
 }
 
 /* Decoration badges (A/M/D) */
-.chat-editing-session-list .changes-decoration-badge {
+.changes-file-list .changes-decoration-badge {
 	display: inline-flex;
 	align-items: center;
 	justify-content: center;
@@ -274,27 +274,27 @@
 	opacity: 0.9;
 }
 
-.chat-editing-session-list .changes-decoration-badge.added {
+.changes-file-list .changes-decoration-badge.added {
 	color: var(--vscode-gitDecoration-addedResourceForeground);
 }
 
-.chat-editing-session-list .changes-decoration-badge.modified {
+.changes-file-list .changes-decoration-badge.modified {
 	color: var(--vscode-gitDecoration-modifiedResourceForeground);
 }
 
-.chat-editing-session-list .changes-decoration-badge.deleted {
+.changes-file-list .changes-decoration-badge.deleted {
 	color: var(--vscode-gitDecoration-deletedResourceForeground);
 }
 
 /* Line counts in list items */
-.chat-editing-session-list .working-set-line-counts {
+.changes-file-list .working-set-line-counts {
 	margin: 0 6px;
 	display: inline-flex;
 	gap: 4px;
 	font-size: 11px;
 }
 
-.changes-view-body .chat-editing-session-list .changes-review-comments-badge {
+.changes-file-list .changes-review-comments-badge {
 	display: inline-flex;
 	align-items: center;
 	gap: 4px;
@@ -303,11 +303,11 @@
 	color: var(--vscode-descriptionForeground);
 }
 
-.changes-view-body .chat-editing-session-list .changes-review-comments-badge .codicon {
+.changes-file-list .changes-review-comments-badge .codicon {
 	font-size: 12px;
 }
 
-.changes-view-body .chat-editing-session-list .changes-agent-feedback-badge {
+.changes-file-list .changes-agent-feedback-badge {
 	display: inline-flex;
 	align-items: center;
 	gap: 4px;
@@ -316,15 +316,15 @@
 	color: var(--vscode-descriptionForeground);
 }
 
-.changes-view-body .chat-editing-session-list .changes-agent-feedback-badge .codicon {
+.changes-file-list .changes-agent-feedback-badge .codicon {
 	font-size: 12px;
 }
 
-.chat-editing-session-list .working-set-lines-added {
+.changes-file-list .working-set-lines-added {
 	color: var(--vscode-chat-linesAddedForeground);
 }
 
-.chat-editing-session-list .working-set-lines-removed {
+.changes-file-list .working-set-lines-removed {
 	color: var(--vscode-chat-linesRemovedForeground);
 }
 
PATCH

echo "Fix applied successfully"
