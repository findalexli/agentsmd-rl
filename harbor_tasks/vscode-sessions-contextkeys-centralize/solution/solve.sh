#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Check if patch already applied (idempotency check)
if grep -q "ChatSessionProviderIdContext" src/vs/sessions/common/contextkeys.ts 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/common/contextkeys.ts b/src/vs/sessions/common/contextkeys.ts
index 76d7136d14c5a..dd02a136de7e9 100644
--- a/src/vs/sessions/common/contextkeys.ts
+++ b/src/vs/sessions/common/contextkeys.ts
@@ -6,6 +6,17 @@
 import { localize } from '../../nls.js';
 import { RawContextKey } from '../../platform/contextkey/common/contextkey.js';

+//#region < --- Active Session --- >
+
+export const IsNewChatSessionContext = new RawContextKey<boolean>('isNewChatSession', true);
+export const ActiveSessionProviderIdContext = new RawContextKey<string>('activeSessionProviderId', '', localize('activeSessionProviderId', "The provider ID of the active session"));
+export const ActiveSessionTypeContext = new RawContextKey<string>('activeSessionType', '', localize('activeSessionType', "The session type of the active session"));
+export const IsActiveSessionBackgroundProviderContext = new RawContextKey<boolean>('isActiveSessionBackgroundProvider', false, localize('isActiveSessionBackgroundProvider', "Whether the active session uses the background agent provider"));
+export const ActiveSessionHasGitRepositoryContext = new RawContextKey<boolean>('activeSessionHasGitRepository', false, localize('activeSessionHasGitRepository', "Whether the active session has an associated git repository"));
+export const ChatSessionProviderIdContext = new RawContextKey<string>('chatSessionProviderId', '', localize('chatSessionProviderId', "The provider ID of a session in context menu overlays"));
+
+//#endregion
+
 //#region < --- Chat Bar --- >

 export const ActiveChatBarContext = new RawContextKey<string>('activeChatBar', '', localize('activeChatBar', "The identifier of the active chat bar panel"));
diff --git a/src/vs/sessions/contrib/chat/browser/chat.contribution.ts b/src/vs/sessions/contrib/chat/browser/chat.contribution.ts
index e771f7ee10dbc..314bd21d348e5 100644
--- a/src/vs/sessions/contrib/chat/browser/chat.contribution.ts
+++ b/src/vs/sessions/contrib/chat/browser/chat.contribution.ts
@@ -16,7 +16,8 @@ import { IWorkbenchContribution, registerWorkbenchContribution2, WorkbenchPhase
 import { IViewContainersRegistry, IViewsRegistry, ViewContainerLocation, Extensions as ViewExtensions, WindowVisibility } from '../../../../workbench/common/views.js';
 import { Registry } from '../../../../platform/registry/common/platform.js';
 import { SyncDescriptor } from '../../../../platform/instantiation/common/descriptors.js';
-import { IsActiveSessionBackgroundProviderContext, ISessionsManagementService, IsNewChatSessionContext } from '../../sessions/browser/sessionsManagementService.js';
+import { ISessionsManagementService } from '../../sessions/browser/sessionsManagementService.js';
+import { IsActiveSessionBackgroundProviderContext, IsNewChatSessionContext, SessionsWelcomeVisibleContext } from '../../../common/contextkeys.js';
 import { Menus } from '../../../browser/menus.js';
 import { BranchChatSessionAction } from './branchChatSessionAction.js';
 import { RunScriptContribution } from './runScriptAction.js';
@@ -38,7 +39,6 @@ import { registerIcon } from '../../../../platform/theme/common/iconRegistry.js'
 import { ChatViewPane } from '../../../../workbench/contrib/chat/browser/widgetHosts/viewPane/chatViewPane.js';
 import { IsAuxiliaryWindowContext } from '../../../../workbench/common/contextkeys.js';
 import { ContextKeyExpr } from '../../../../platform/contextkey/common/contextkey.js';
-import { SessionsWelcomeVisibleContext } from '../../../common/contextkeys.js';
 import { CopilotCLISessionType } from '../../sessions/browser/sessionTypes.js';

 export class OpenSessionWorktreeInVSCodeAction extends Action2 {
diff --git a/src/vs/sessions/contrib/chat/browser/runScriptAction.ts b/src/vs/sessions/contrib/chat/browser/runScriptAction.ts
index 032729f1671cc..d11c7a5d387e0 100644
--- a/src/vs/sessions/contrib/chat/browser/runScriptAction.ts
+++ b/src/vs/sessions/contrib/chat/browser/runScriptAction.ts
@@ -27,12 +27,12 @@ import { IQuickInputService, IQuickPickItem, IQuickPickSeparator } from '../../.
 import { ITelemetryService } from '../../../../platform/telemetry/common/telemetry.js';
 import { IWorkbenchContribution } from '../../../../workbench/common/contributions.js';
 import { SessionsCategories } from '../../../common/categories.js';
-import { IsActiveSessionBackgroundProviderContext, ISessionsManagementService } from '../../sessions/browser/sessionsManagementService.js';
+import { ISessionsManagementService } from '../../sessions/browser/sessionsManagementService.js';
+import { IsActiveSessionBackgroundProviderContext, SessionsWelcomeVisibleContext } from '../../../common/contextkeys.js';
 import { ISession } from '../../sessions/common/sessionData.js';
 import { Menus } from '../../../browser/menus.js';
 import { INonSessionTaskEntry, ISessionsConfigurationService, ISessionTaskWithTarget, ITaskEntry, TaskStorageTarget } from './sessionsConfigurationService.js';
 import { IsAuxiliaryWindowContext } from '../../../../workbench/common/contextkeys.js';
-import { SessionsWelcomeVisibleContext } from '../../../common/contextkeys.js';
 import { IRunScriptCustomTaskWidgetResult, RunScriptCustomTaskWidget } from './runScriptCustomTaskWidget.js';
 import { HoverPosition } from '../../../../base/browser/ui/hover/hoverWidget.js';

diff --git a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
index 5bbb4042257cc..e9ba844942fc5 100644
--- a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
+++ b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
@@ -19,7 +19,7 @@ import { IModelPickerDelegate } from '../../../../workbench/contrib/chat/browser
 import { IChatInputPickerOptions } from '../../../../workbench/contrib/chat/browser/widget/input/chatInputPickerActionItem.js';
 import { EnhancedModelPickerActionItem } from '../../../../workbench/contrib/chat/browser/widget/input/modelPickerActionItem2.js';
 import { HoverPosition } from '../../../../base/browser/ui/hover/hoverWidget.js';
-import { IContextKeyService, ContextKeyExpr, RawContextKey } from '../../../../platform/contextkey/common/contextkey.js';
+import { IContextKeyService, ContextKeyExpr } from '../../../../platform/contextkey/common/contextkey.js';
 import { IStorageService, StorageScope, StorageTarget } from '../../../../platform/storage/common/storage.js';
 import { Menus } from '../../../browser/menus.js';
 import { ISessionsManagementService } from '../../sessions/browser/sessionsManagementService.js';
@@ -29,16 +29,16 @@ import { ISession } from '../../sessions/common/sessionData.js';
 import { IAgentSessionsService } from '../../../../workbench/contrib/chat/browser/agentSessions/agentSessionsService.js';
 import { CopilotCLISession, COPILOT_PROVIDER_ID } from './copilotChatSessionsProvider.js';
 import { COPILOT_CLI_SESSION_TYPE, COPILOT_CLOUD_SESSION_TYPE } from '../../sessions/browser/sessionTypes.js';
+import { ActiveSessionHasGitRepositoryContext, ActiveSessionProviderIdContext, ActiveSessionTypeContext, ChatSessionProviderIdContext } from '../../../common/contextkeys.js';
 import { IsolationPicker } from './isolationPicker.js';
 import { BranchPicker } from './branchPicker.js';
 import { ModePicker } from './modePicker.js';
 import { CloudModelPicker } from './modelPicker.js';
 import { NewChatPermissionPicker } from '../../chat/browser/newChatPermissionPicker.js';

-const ActiveSessionHasGitRepositoryContext = new RawContextKey<boolean>('activeSessionHasGitRepository', false);
-const IsActiveSessionCopilotCLI = ContextKeyExpr.equals('activeSessionType', COPILOT_CLI_SESSION_TYPE);
-const IsActiveSessionCopilotCloud = ContextKeyExpr.equals('activeSessionType', COPILOT_CLOUD_SESSION_TYPE);
-const IsActiveCopilotChatSessionProvider = ContextKeyExpr.equals('activeSessionProviderId', COPILOT_PROVIDER_ID);
+const IsActiveSessionCopilotCLI = ContextKeyExpr.equals(ActiveSessionTypeContext.key, COPILOT_CLI_SESSION_TYPE);
+const IsActiveSessionCopilotCloud = ContextKeyExpr.equals(ActiveSessionTypeContext.key, COPILOT_CLOUD_SESSION_TYPE);
+const IsActiveCopilotChatSessionProvider = ContextKeyExpr.equals(ActiveSessionProviderIdContext.key, COPILOT_PROVIDER_ID);
 const IsActiveSessionCopilotChatCLI = ContextKeyExpr.and(IsActiveSessionCopilotCLI, IsActiveCopilotChatSessionProvider);
 const IsActiveSessionCopilotChatCloud = ContextKeyExpr.and(IsActiveSessionCopilotCloud, IsActiveCopilotChatSessionProvider);

@@ -364,7 +364,7 @@ class CopilotSessionContextMenuBridge extends Disposable implements IWorkbenchCo
 			});
 		}));

-		const providerWhen = ContextKeyExpr.equals('chatSessionProviderId', COPILOT_PROVIDER_ID);
+		const providerWhen = ContextKeyExpr.equals(ChatSessionProviderIdContext.key, COPILOT_PROVIDER_ID);
 		this._register(MenuRegistry.appendMenuItem(SessionItemContextMenuId, {
 			command: { ...item.command, id: wrapperId },
 			group: item.group,
diff --git a/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts b/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts
index 76fa40d2767e8..a2ebfee177f73 100644
--- a/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts
+++ b/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts
@@ -7,9 +7,8 @@ import { Emitter, Event } from '../../../../base/common/event.js';
 import { Disposable } from '../../../../base/common/lifecycle.js';
 import { IObservable, IReader, observableFromEvent, observableValue } from '../../../../base/common/observable.js';
 import { URI } from '../../../../base/common/uri.js';
-import { localize } from '../../../../nls.js';
 import { createDecorator } from '../../../../platform/instantiation/common/instantiation.js';
-import { IContextKey, IContextKeyService, RawContextKey } from '../../../../platform/contextkey/common/contextkey.js';
+import { IContextKey, IContextKeyService } from '../../../../platform/contextkey/common/contextkey.js';
 import { ILogService } from '../../../../platform/log/common/log.js';
 import { IStorageService, StorageScope, StorageTarget } from '../../../../platform/storage/common/storage.js';
 import { COPILOT_CLI_SESSION_TYPE } from './sessionTypes.js';
@@ -19,26 +18,7 @@ import { SessionsGroupModel } from './sessionsGroupModel.js';
 import { ISession, ISessionWorkspace, ISessionData, IChat, SessionStatus } from '../common/sessionData.js';
 import { ChatViewPaneTarget, IChatWidgetService } from '../../../../workbench/contrib/chat/browser/chat.js';
 import { IUriIdentityService } from '../../../../platform/uriIdentity/common/uriIdentity.js';
-
-/**
- * Configuration properties available on new/pending sessions.
- * Not part of the public {@link ISession} contract but present on
- * concrete session implementations (CopilotCLISession, RemoteNewSession, AgentHostNewSession).
- */
-
-export const IsNewChatSessionContext = new RawContextKey<boolean>('isNewChatSession', true);
-
-/**
- * The provider ID of the active session (e.g., 'default-copilot', 'agenthost-hostA').
- */
-export const ActiveSessionProviderIdContext = new RawContextKey<string>('activeSessionProviderId', '', localize('activeSessionProviderId', "The provider ID of the active session"));
-
-/**
- * The session type of the active session (e.g., 'copilotcli', 'cloud').
- */
-export const ActiveSessionTypeContext = new RawContextKey<string>('activeSessionType', '', localize('activeSessionType', "The session type of the active session"));
-
-export const IsActiveSessionBackgroundProviderContext = new RawContextKey<boolean>('isActiveSessionBackgroundProvider', false, localize('isActiveSessionBackgroundProvider', "Whether the active session uses the background agent provider"));
+import { ActiveSessionProviderIdContext, ActiveSessionTypeContext, IsActiveSessionBackgroundProviderContext, IsNewChatSessionContext } from '../../../common/contextkeys.js';

 //#region Active Session Service

diff --git a/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts b/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts
index fb5d3a5f359be..a7f278173134a 100644
--- a/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts
+++ b/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts
@@ -26,7 +26,7 @@ import { ISessionsManagementService } from './sessionsManagementService.js';
 import { autorun } from '../../../../base/common/observable.js';
 import { ThemeIcon } from '../../../../base/common/themables.js';
 import { IsAuxiliaryWindowContext } from '../../../../workbench/common/contextkeys.js';
-import { SessionsWelcomeVisibleContext } from '../../../common/contextkeys.js';
+import { ChatSessionProviderIdContext, SessionsWelcomeVisibleContext } from '../../../common/contextkeys.js';
 import { ISessionsProvidersService } from './sessionsProvidersService.js';
 import { SessionStatus } from '../common/sessionData.js';
 import { Codicon } from '../../../../base/common/codicons.js';
@@ -306,7 +306,7 @@ export class SessionsTitleBarWidget extends BaseActionViewItem {
 			[IsSessionArchivedContext.key, sessionData.isArchived.get()],
 			[IsSessionReadContext.key, sessionData.isRead.get()],
 			['chatSessionType', sessionData.sessionType],
-			['chatSessionProviderId', sessionData.providerId],
+			[ChatSessionProviderIdContext.key, sessionData.providerId],
 		];

 		const menu = this.menuService.createMenu(SessionItemContextMenuId, this.contextKeyService.createOverlay(contextOverlay));
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
index 4f630e2fc1546..eda2aae1b8da1 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
@@ -23,6 +23,7 @@ import { localize } from '../../../../../nls.js';
 import { MenuId, IMenuService } from '../../../../../platform/actions/common/actions.js';
 import { MenuWorkbenchToolBar } from '../../../../../platform/actions/browser/toolbar.js';
 import { IContextKeyService, RawContextKey } from '../../../../../platform/contextkey/common/contextkey.js';
+import { ChatSessionProviderIdContext } from '../../../../common/contextkeys.js';
 import { IContextMenuService } from '../../../../../platform/contextview/browser/contextView.js';
 import { IInstantiationService } from '../../../../../platform/instantiation/common/instantiation.js';
 import { IKeybindingService } from '../../../../../platform/keybinding/common/keybinding.js';
@@ -963,7 +964,7 @@ export class SessionsList extends Disposable implements ISessionsList {
 			[IsSessionArchivedContext.key, element.isArchived.get()],
 			[IsSessionReadContext.key, element.isRead.get()],
 			['chatSessionType', element.sessionType],
-			['chatSessionProviderId', element.providerId],
+			[ChatSessionProviderIdContext.key, element.providerId],
 		];

 		const menu = this.menuService.createMenu(SessionItemContextMenuId, this.contextKeyService.createOverlay(contextOverlay));
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
index e61aab4d12b1c..f1c837c302c4a 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
@@ -19,12 +19,12 @@ import { IChatWidgetService } from '../../../../../workbench/contrib/chat/browse
 import { AUX_WINDOW_GROUP } from '../../../../../workbench/services/editor/common/editorService.js';
 import { SessionsCategories } from '../../../../common/categories.js';
 import { SessionItemToolbarMenuId, SessionItemContextMenuId, SessionSectionToolbarMenuId, SessionSectionTypeContext, IsSessionPinnedContext, IsSessionArchivedContext, IsSessionReadContext, SessionsGrouping, SessionsSorting, ISessionSection } from './sessionsList.js';
-import { ISessionsManagementService, IsNewChatSessionContext } from '../sessionsManagementService.js';
+import { ISessionsManagementService } from '../sessionsManagementService.js';
+import { IsNewChatSessionContext, SessionsWelcomeVisibleContext } from '../../../../common/contextkeys.js';
 import { ISession, SessionStatus } from '../../common/sessionData.js';
 import { IsWorkspaceGroupCappedContext, SessionsViewFilterOptionsSubMenu, SessionsViewFilterSubMenu, SessionsViewGroupingContext, SessionsViewId, SessionsView, SessionsViewSortingContext } from './sessionsView.js';
 import { SessionsViewId as NewChatViewId, NewChatViewPane } from '../../../chat/browser/newChatViewPane.js';
 import { Menus } from '../../../../browser/menus.js';
-import { SessionsWelcomeVisibleContext } from '../../../../common/contextkeys.js';

 //  Constants
PATCH

echo "Patch applied successfully"
