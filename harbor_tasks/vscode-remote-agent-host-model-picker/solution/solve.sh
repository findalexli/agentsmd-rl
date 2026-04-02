#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if patch already applied (idempotency check)
if grep -q "IsActiveSessionRemoteAgentHost = ContextKeyExpr.regex(ActiveSessionProviderIdContext.key" src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

echo "Applying fix for remote agent host model picker..."

git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
index 2ab3811132f48..8585506a81ce7 100644
--- a/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
+++ b/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts
@@ -3,6 +3,7 @@
  *  Licensed under the MIT License. See License.txt in the project root for license information.
  *--------------------------------------------------------------------------------------------*/

+import { coalesce } from '../../../../base/common/arrays.js';
 import { Disposable } from '../../../../base/common/lifecycle.js';
 import { IReader, autorun, observableValue } from '../../../../base/common/observable.js';
 import { localize2 } from '../../../../nls.js';
@@ -40,7 +41,7 @@ const IsActiveSessionCopilotCloud = ContextKeyExpr.equals(ActiveSessionTypeConte
 const IsActiveCopilotChatSessionProvider = ContextKeyExpr.equals(ActiveSessionProviderIdContext.key, COPILOT_PROVIDER_ID);
 const IsActiveSessionCopilotChatCLI = ContextKeyExpr.and(IsActiveSessionCopilotCLI, IsActiveCopilotChatSessionProvider);
 const IsActiveSessionCopilotChatCloud = ContextKeyExpr.and(IsActiveSessionCopilotCloud, IsActiveCopilotChatSessionProvider);
-const IsActiveSessionRemoteAgentHost = ContextKeyExpr.regex('activeSessionProviderId', /^agenthost-/);
+const IsActiveSessionRemoteAgentHost = ContextKeyExpr.regex(ActiveSessionProviderIdContext.key, /^agenthost-/);

 // -- Actions --

@@ -246,7 +247,7 @@ class CopilotPickerActionViewItemContribution extends Disposable implements IWor
 				modelPicker.setEnabled(models.length > 0);
 				if (!currentModel.get() && models.length > 0) {
 					const remembered = rememberedModelId ? models.find(m => m.identifier === rememberedModelId) : undefined;
-					currentModel.set(remembered ?? models[0], undefined);
+					delegate.setModel(remembered ?? models[0]);
 				}
 			};
 			initModel();
@@ -362,17 +363,18 @@ class CopilotSessionContextMenuBridge extends Disposable implements IWorkbenchCo
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
diff --git a/src/vs/sessions/contrib/remoteAgentHost/browser/remoteAgentHost.contribution.ts b/src/vs/sessions/contrib/remoteAgentHost/browser/remoteAgentHost.contribution.ts
index 36ada54fccf7d..fa9c3658474a0 100644
--- a/src/vs/sessions/contrib/remoteAgentHost/browser/remoteAgentHost.contribution.ts
+++ b/src/vs/sessions/contrib/remoteAgentHost/browser/remoteAgentHost.contribution.ts
@@ -258,8 +258,8 @@ export class RemoteAgentHostContribution extends Disposable implements IWorkbenc
 			loggedConnection.logError('subscribe(root)', err);
 		});

-		// Authenticate with this new connection
-		this._authenticateWithConnection(loggedConnection);
+		// Authenticate with this new connection and refresh models afterward
+		this._authenticateWithConnection(loggedConnection).then(() => loggedConnection.refreshModels()).catch(() => { /* best-effort */ });

 		// Wire connection to existing sessions provider
 		this._providerInstances.get(address)?.setConnection(loggedConnection, connectionInfo.defaultDirectory);
@@ -380,7 +380,7 @@ export class RemoteAgentHostContribution extends Disposable implements IWorkbenc

 	private _authenticateAllConnections(): void {
 		for (const [, connState] of this._connections) {
-			this._authenticateWithConnection(connState.loggedConnection);
+			this._authenticateWithConnection(connState.loggedConnection).then(() => connState.loggedConnection.refreshModels()).catch(() => { /* best-effort */ });
 		}
 	}
PATCH

echo "Patch applied successfully!"
