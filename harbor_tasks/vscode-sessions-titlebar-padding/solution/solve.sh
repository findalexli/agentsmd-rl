#!/usr/bin/env bash
set -euo pipefail

# Check if fix is already applied
CSS_FILE="src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css"

if grep -q "agent-sessions-workbench:not(.nosidebar)" "$CSS_FILE"; then
    echo "Fix already applied, skipping..."
    exit 0
fi

# Apply the CSS fix
git apply - <<'PATCH'
diff --git a/src/vs/sessions/LAYOUT.md b/src/vs/sessions/LAYOUT.md
index 5c48d4391bbae..69a03f32e88cb 100644
--- a/src/vs/sessions/LAYOUT.md
+++ b/src/vs/sessions/LAYOUT.md
@@ -87,6 +87,7 @@ The widget:
 - Gets the active session label from `IActiveSessionService.getActiveSession()` and the live model title from `IChatService`, falling back to "New Session" if no active session is found
 - Re-renders automatically when the active session changes via `autorun` on `IActiveSessionService.activeSession`, and when session data changes via `IAgentSessionsService.model.onDidChangeSessions`
 - Is registered via `SessionsTitleBarContribution` (an `IWorkbenchContribution` in `contrib/sessions/browser/sessionsTitleBarWidget.ts`) that calls `IActionViewItemService.register()` to intercept the submenu rendering
+- Uses `padding-left: 0` while the sidebar is visible, and restores `padding-left: 16px` when the sidebar is hidden via the `nosidebar` workbench class

 ### 3.3 Left Toolbar

@@ -643,6 +644,7 @@ interface IPartVisibilityState {

 | Date | Change |
 |------|--------|
+| 2026-03-30 | Adjusted `.agent-sessions-titlebar-container` padding so it sits flush when the sidebar is visible and restores 16px left padding when the sidebar is hidden |
 | 2026-03-26 | Updated the sessions sidebar appear animation so only the body content (`.part.sidebar > .content`) slides/fades in during reveal while the sidebar title/header and footer remain fixed |
 | 2026-03-25 | Updated Sessions view documentation to reflect the refactored `SessionsView` implementation in `contrib/sessions/browser/views/sessionsView.ts` and documented the left-aligned "+ Session" sidebar action with its inline keybinding hint |
 | 2026-03-24 | Updated the sessions new-chat empty state: removed the watermark, vertically centered the empty-state controls block, restyled the workspace picker as an inline `New session in {dropdown}` title row aligned to the chat input, and tuned empty-state dropdown icon/chevron and local-mode spacing for the final visual polish. |
diff --git a/src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css b/src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css
index a8d1a3310c381..eeaa0e82ba771 100644
--- a/src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css
+++ b/src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css
@@ -21,6 +21,10 @@
 	cursor: default;
 }

+.agent-sessions-workbench:not(.nosidebar) .command-center .agent-sessions-titlebar-container {
+	padding-left: 0;
+}
+
 /* Session pill - clickable area for session picker */
 .command-center .agent-sessions-titlebar-container .agent-sessions-titlebar-pill {
 	display: flex;
PATCH

echo "Fix applied successfully"
