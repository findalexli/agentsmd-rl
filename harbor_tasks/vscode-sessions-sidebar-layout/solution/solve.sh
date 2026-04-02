#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied: look for onDidChangeMenuItems usage in the widget
if grep -q "onDidChangeMenuItems" src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts b/src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts
index fe6f55d5fa0b5..d6a5afc39a044 100644
--- a/src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts
+++ b/src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts
@@ -29,7 +29,7 @@ const $ = DOM.$;
 const CUSTOMIZATIONS_COLLAPSED_KEY = 'agentSessions.customizationsCollapsed';

 export interface IAICustomizationShortcutsWidgetOptions {
-	readonly onDidToggleCollapse?: () => void;
+	readonly onDidChangeLayout?: () => void;
 }

 export class AICustomizationShortcutsWidget extends Disposable {
@@ -86,12 +86,17 @@ export class AICustomizationShortcutsWidget extends Disposable {
 		// Toolbar container
 		const toolbarContainer = DOM.append(container, $('.ai-customization-toolbar-content.sidebar-action-list'));

-		this._register(this.instantiationService.createInstance(MenuWorkbenchToolBar, toolbarContainer, Menus.SidebarCustomizations, {
+		const toolbar = this._register(this.instantiationService.createInstance(MenuWorkbenchToolBar, toolbarContainer, Menus.SidebarCustomizations, {
 			hiddenItemStrategy: HiddenItemStrategy.NoHide,
 			toolbarOptions: { primaryGroup: () => true },
 			telemetrySource: 'sidebarCustomizations',
 		}));

+		// Re-layout when toolbar items change (e.g., Plugins item appearing after extension activation)
+		this._register(toolbar.onDidChangeMenuItems(() => {
+			options?.onDidChangeLayout?.();
+		}));
+
 		let updateCountRequestId = 0;
 		const updateHeaderTotalCount = async () => {
 			const requestId = ++updateCountRequestId;
@@ -130,7 +135,7 @@ export class AICustomizationShortcutsWidget extends Disposable {
 			// Re-layout after the transition
 			transitionListener.value = DOM.addDisposableListener(toolbarContainer, 'transitionend', () => {
 				transitionListener.clear();
-				options?.onDidToggleCollapse?.();
+				options?.onDidChangeLayout?.();
 			});
 		};

diff --git a/src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css b/src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css
index e5428ea889ba2..460e935f9554e 100644
--- a/src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css
+++ b/src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css
@@ -40,7 +40,7 @@
 		flex: 1;
 		overflow: hidden;
 		min-height: 0;
-		margin-bottom: 12px;
+		margin-bottom: 6px;
 	}

 	.agent-sessions-header {
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts
index 61ef8dcc85088..a92f893eb35ed 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts
@@ -224,7 +224,7 @@ export class SessionsView extends ViewPane {

 		// AI Customization toolbar (bottom, fixed height)
 		this._register(this.instantiationService.createInstance(AICustomizationShortcutsWidget, sessionsContainer, {
-			onDidToggleCollapse: () => {
+			onDidChangeLayout: () => {
 				if (this.viewPaneContainer) {
 					const { offsetHeight, offsetWidth } = this.viewPaneContainer;
 					this.layoutBody(offsetHeight, offsetWidth);
PATCH

echo "Patch applied successfully"
