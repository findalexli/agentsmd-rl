#!/bin/bash
set -euo pipefail

cd /workspace/vscode
CSS_FILE="src/vs/sessions/browser/parts/media/sidebarPart.css"

# Check if already applied (idempotency check for background: var(--vscode-toolbar-activeBackground))
if grep -q "\.action-label.checked {" "$CSS_FILE" 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/browser/parts/media/sidebarPart.css b/src/vs/sessions/browser/parts/media/sidebarPart.css
index 1ddbeedf2c20b..fd71ae41a81d7 100644
--- a/src/vs/sessions/browser/parts/media/sidebarPart.css
+++ b/src/vs/sessions/browser/parts/media/sidebarPart.css
@@ -28,6 +28,17 @@
 	-webkit-app-region: no-drag;
 }

+/* Toggled state for the sidebar toggle button in the sidebar title area */
+.agent-sessions-workbench .part.sidebar > .composite.title > .global-actions-left .action-label.checked {
+	background: var(--vscode-toolbar-activeBackground);
+	border-radius: var(--vscode-cornerRadius-medium);
+}
+
+/* Preserve toggled background when the toggle button is hovered or focused */
+.agent-sessions-workbench .part.sidebar > .composite.title > .global-actions-left .action-label.checked:hover,
+.agent-sessions-workbench .part.sidebar > .composite.title > .global-actions-left .action-label.checked:focus {
+	background: var(--vscode-toolbar-activeBackground);
+}
 /* Sidebar Footer Container */
 .agent-sessions-workbench .part.sidebar > .sidebar-footer {
 	display: flex;
PATCH

echo "Patch applied successfully"
