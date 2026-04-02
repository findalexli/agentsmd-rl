#!/bin/bash
set -euo pipefail

# Idempotent fix for VS Code PR #306419: Session title bar context menu and session type icons

cd /workspace/vscode

# Check if already applied (look for _getSessionTypeIcon method)
if grep -q "_getSessionTypeIcon" src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts
index 06e06724d4b46..8fb2e4bb30424 100644
--- a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts
+++ b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts
@@ -640,7 +640,7 @@ class AgentSessionAdapter implements ISessionData {
 		this.resource = session.resource;
 		this.providerId = providerId;
 		this.sessionType = session.providerType;
-		this.icon = session.icon;
+		this.icon = this._getSessionTypeIcon(session);
 		this.createdAt = new Date(session.timing.created);
 		this._workspace = observableValue(this, this._buildWorkspace(session));
 		this.workspace = this._workspace;
@@ -692,6 +692,17 @@ class AgentSessionAdapter implements ISessionData {
 		});
 	}

+	private _getSessionTypeIcon(session: IAgentSession): ThemeIcon {
+		switch (session.providerType) {
+			case AgentSessionProviders.Background:
+				return CopilotCLISessionType.icon;
+			case AgentSessionProviders.Cloud:
+				return CopilotCloudSessionType.icon;
+			default:
+				return session.icon;
+		}
+	}
+
 	private _extractDescription(session: IAgentSession): string | undefined {
 		if (!session.description) {
 			return undefined;
diff --git a/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts b/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts
index 5e0de629eea4a..a9667a2112f33 100644
--- a/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts
+++ b/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts
@@ -21,7 +21,7 @@ import { IWorkbenchLayoutService, Parts } from '../../../../workbench/services/l
 import { Menus } from '../../../browser/menus.js';
 import { IWorkbenchContribution } from '../../../../workbench/common/contributions.js';
 import { IActionViewItemService } from '../../../../platform/actions/browser/actionViewItemService.js';
-import { ISessionsManagementService } from './sessionsManagementService.js';
+import { ISessionsManagementService, IsNewChatSessionContext } from './sessionsManagementService.js';
 import { autorun, observableSignalFromEvent } from '../../../../base/common/observable.js';
 import { ThemeIcon } from '../../../../base/common/themables.js';
 import { IsAuxiliaryWindowContext } from '../../../../workbench/common/contextkeys.js';
@@ -30,6 +30,8 @@ import { ISessionsProvidersService } from './sessionsProvidersService.js';
 import { SessionStatus } from '../common/sessionData.js';
 import { SHOW_SESSIONS_PICKER_COMMAND_ID } from './sessionsActions.js';
 import { IsSessionArchivedContext, IsSessionPinnedContext, IsSessionReadContext, SessionItemContextMenuId } from './views/sessionsList.js';
+import { SessionsView, SessionsViewId } from './views/sessionsView.js';
+import { IViewsService } from '../../../../workbench/services/views/common/viewsService.js';

 /**
  * Sessions Title Bar Widget - renders the active chat session title
@@ -66,6 +68,7 @@ export class SessionsTitleBarWidget extends BaseActionViewItem {
 		@IContextKeyService private readonly contextKeyService: IContextKeyService,
 		@ISessionsProvidersService private readonly sessionsProvidersService: ISessionsProvidersService,
 		@ICommandService private readonly commandService: ICommandService,
+		@IViewsService private readonly viewsService: IViewsService,
 	) {
 		super(undefined, action, options);

@@ -256,8 +259,13 @@ export class SessionsTitleBarWidget extends BaseActionViewItem {
 			return;
 		}

+		if (this.contextKeyService.getContextKeyValue<boolean>(IsNewChatSessionContext.key)) {
+			return;
+		}
+
+		const isPinned = this.viewsService.getViewWithId<SessionsView>(SessionsViewId)?.sessionsControl?.isSessionPinned(sessionData) ?? false;
 		const contextOverlay: [string, boolean | string][] = [
-			[IsSessionPinnedContext.key, false],
+			[IsSessionPinnedContext.key, isPinned],
 			[IsSessionArchivedContext.key, sessionData.isArchived.get()],
 			[IsSessionReadContext.key, sessionData.isRead.get()],
 			['chatSessionType', sessionData.sessionType],
PATCH

echo "Patch applied successfully"
