#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency check
if grep -q "const selectedSessions" src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --3way - <<'PATCH'
diff --git a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
index 5bbb4042257cc..aca5d84560873 100644
--- a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
+++ b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
@@ -4,6 +4,7 @@
  *--------------------------------------------------------------------------------------------*/

 import { Disposable } from '../../../../base/common/lifecycle.js';
+import { coalesce } from '../../../../base/common/arrays.js';
 import { IReader, autorun, observableValue } from '../../../../base/common/observable.js';
 import { localize2 } from '../../../../nls.js';
 import { Action2, registerAction2, MenuId, MenuRegistry, isIMenuItem } from '../../../../platform/actions/common/actions.js';
@@ -349,17 +350,18 @@ class CopilotSessionContextMenuBridge extends Disposable implements IWorkbenchCo
 			this._bridgedIds.add(commandId);

 			const wrapperId = `sessionsViewPane.bridge.${commandId}`;
-			this._register(CommandsRegistry.registerCommand(wrapperId, (accessor, sessionData?: ISession) => {
-				if (!sessionData) {
+			this._register(CommandsRegistry.registerCommand(wrapperId, (accessor, context?: ISession | ISession[]) => {
+				if (!context) {
 					return;
 				}
-				const agentSession = this.agentSessionsService.getSession(sessionData.resource);
-				if (!agentSession) {
+				const sessions = Array.isArray(context) ? context : [context];
+				const agentSessions = coalesce(sessions.map(s => this.agentSessionsService.getSession(s.resource)));
+				if (agentSessions.length === 0) {
 					return;
 				}
 				return this.commandService.executeCommand(commandId, {
-					session: agentSession,
-					sessions: [agentSession],
+					session: agentSessions[0],
+					sessions: agentSessions,
 					$mid: MarshalledId.AgentSessionContext,
 				});
 			}));
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
index 4f630e2fc1546..7b6d8d72afca8 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
@@ -958,6 +958,9 @@ export class SessionsList extends Disposable implements ISessionsList {
 			return;
 		}

+		const selection = this.tree.getSelection().filter((s): s is ISession => !!s && !isSessionSection(s) && !isSessionShowMore(s));
+		const selectedSessions = selection.includes(element) ? [element, ...selection.filter(s => s !== element)] : [element];
+
 		const contextOverlay: [string, boolean | string][] = [
 			[IsSessionPinnedContext.key, this.isSessionPinned(element)],
 			[IsSessionArchivedContext.key, element.isArchived.get()],
@@ -969,7 +972,7 @@ export class SessionsList extends Disposable implements ISessionsList {
 		const menu = this.menuService.createMenu(SessionItemContextMenuId, this.contextKeyService.createOverlay(contextOverlay));

 		this.contextMenuService.showContextMenu({
-			getActions: () => Separator.join(...menu.getActions({ arg: element, shouldForwardArgs: true }).map(([, actions]) => actions)),
+			getActions: () => Separator.join(...menu.getActions({ arg: selectedSessions, shouldForwardArgs: true }).map(([, actions]) => actions)),
 			getAnchor: () => e.anchor,
 			getKeyBinding: (action) => this.keybindingService.lookupKeybinding(action.id) ?? undefined,
 		});
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
index e61aab4d12b1c..c409f6a06d709 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
@@ -400,13 +400,16 @@ registerAction2(class PinSessionAction extends Action2 {
 			}]
 		});
 	}
-	run(accessor: ServicesAccessor, context?: ISession): void {
+	run(accessor: ServicesAccessor, context?: ISession | ISession[]): void {
 		if (!context) {
 			return;
 		}
+		const sessions = Array.isArray(context) ? context : [context];
 		const viewsService = accessor.get(IViewsService);
 		const view = viewsService.getViewWithId<SessionsView>(SessionsViewId);
-		view?.sessionsControl?.pinSession(context);
+		for (const session of sessions) {
+			view?.sessionsControl?.pinSession(session);
+		}
 	}
 });

@@ -435,13 +438,16 @@ registerAction2(class UnpinSessionAction extends Action2 {
 			}]
 		});
 	}
-	run(accessor: ServicesAccessor, context?: ISession): void {
+	run(accessor: ServicesAccessor, context?: ISession | ISession[]): void {
 		if (!context) {
 			return;
 		}
+		const sessions = Array.isArray(context) ? context : [context];
 		const viewsService = accessor.get(IViewsService);
 		const view = viewsService.getViewWithId<SessionsView>(SessionsViewId);
-		view?.sessionsControl?.unpinSession(context);
+		for (const session of sessions) {
+			view?.sessionsControl?.unpinSession(session);
+		}
 	}
 });

@@ -464,12 +470,15 @@ registerAction2(class ArchiveSessionAction extends Action2 {
 			}]
 		});
 	}
-	async run(accessor: ServicesAccessor, context?: ISession): Promise<void> {
+	async run(accessor: ServicesAccessor, context?: ISession | ISession[]): Promise<void> {
 		if (!context) {
 			return;
 		}
+		const sessions = Array.isArray(context) ? context : [context];
 		const sessionsManagementService = accessor.get(ISessionsManagementService);
-		await sessionsManagementService.archiveSession(context);
+		for (const session of sessions) {
+			await sessionsManagementService.archiveSession(session);
+		}
 	}
 });

@@ -492,12 +501,15 @@ registerAction2(class UnarchiveSessionAction extends Action2 {
 			}]
 		});
 	}
-	async run(accessor: ServicesAccessor, context?: ISession): Promise<void> {
+	async run(accessor: ServicesAccessor, context?: ISession | ISession[]): Promise<void> {
 		if (!context) {
 			return;
 		}
+		const sessions = Array.isArray(context) ? context : [context];
 		const sessionsManagementService = accessor.get(ISessionsManagementService);
-		await sessionsManagementService.unarchiveSession(context);
+		for (const session of sessions) {
+			await sessionsManagementService.unarchiveSession(session);
+		}
 	}
 });

@@ -517,12 +529,15 @@ registerAction2(class MarkSessionReadAction extends Action2 {
 			}]
 		});
 	}
-	run(accessor: ServicesAccessor, context?: ISession): void {
+	run(accessor: ServicesAccessor, context?: ISession | ISession[]): void {
 		if (!context) {
 			return;
 		}
+		const sessions = Array.isArray(context) ? context : [context];
 		const sessionsManagementService = accessor.get(ISessionsManagementService);
-		sessionsManagementService.setRead(context, true);
+		for (const session of sessions) {
+			sessionsManagementService.setRead(session, true);
+		}
 	}
 });

@@ -542,12 +557,15 @@ registerAction2(class MarkSessionUnreadAction extends Action2 {
 			}]
 		});
 	}
-	run(accessor: ServicesAccessor, context?: ISession): void {
+	run(accessor: ServicesAccessor, context?: ISession | ISession[]): void {
 		if (!context) {
 			return;
 		}
+		const sessions = Array.isArray(context) ? context : [context];
 		const sessionsManagementService = accessor.get(ISessionsManagementService);
-		sessionsManagementService.setRead(context, false);
+		for (const session of sessions) {
+			sessionsManagementService.setRead(session, false);
+		}
 	}
 });

@@ -563,15 +581,18 @@ registerAction2(class OpenSessionInNewWindowAction extends Action2 {
 			}]
 		});
 	}
-	async run(accessor: ServicesAccessor, context?: ISession): Promise<void> {
+	async run(accessor: ServicesAccessor, context?: ISession | ISession[]): Promise<void> {
 		if (!context) {
 			return;
 		}
+		const sessions = Array.isArray(context) ? context : [context];
 		const chatWidgetService = accessor.get(IChatWidgetService);
-		await chatWidgetService.openSession(context.resource, AUX_WINDOW_GROUP, {
-			auxiliary: { compact: true, bounds: { width: 800, height: 640 } },
-			pinned: true
-		});
+		for (const session of sessions) {
+			await chatWidgetService.openSession(session.resource, AUX_WINDOW_GROUP, {
+				auxiliary: { compact: true, bounds: { width: 800, height: 640 } },
+				pinned: true
+			});
+		}
 	}
 });
PATCH

echo "Patch applied successfully."
