#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency check
if ! grep -q "this._config.connection.disposeSession(resolvedSession);" src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --3way - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts b/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts
index fd48e6d6b199e..bd95c6e5a6b56 100644
--- a/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts
+++ b/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts
@@ -302,7 +302,6 @@ export class AgentHostSessionHandler extends Disposable implements IChatSessionC
 				if (resolvedSession) {
 					this._clientState.unsubscribe(resolvedSession.toString());
 					this._config.connection.unsubscribe(resolvedSession);
-					this._config.connection.disposeSession(resolvedSession);
 				}
 			},
 		);
diff --git a/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentHostChatContribution.test.ts b/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentHostChatContribution.test.ts
index d3c9b2c17b43d..5a77a9eb50bf4 100644
--- a/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentHostChatContribution.test.ts
+++ b/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentHostChatContribution.test.ts
@@ -54,6 +54,7 @@ class MockAgentHostService extends mock<IAgentHostService>() {
 	private _nextId = 1;
 	private readonly _sessions = new Map<string, IAgentSessionMetadata>();
 	public createSessionCalls: IAgentCreateSessionConfig[] = [];
+	public disposedSessions: URI[] = [];
 	public agents = [{ provider: 'copilot' as const, displayName: 'Agent Host - Copilot', description: 'test', requiresAuth: true }];

 	override async listSessions(): Promise<IAgentSessionMetadata[]> {
@@ -76,7 +77,7 @@ class MockAgentHostService extends mock<IAgentHostService>() {
 		return session;
 	}

-	override async disposeSession(_session: URI): Promise<void> { }
+	override async disposeSession(session: URI): Promise<void> { this.disposedSessions.push(session); }
 	override async shutdown(): Promise<void> { }
 	override async restartAgentHost(): Promise<void> { }

@@ -1944,6 +1945,20 @@ suite('AgentHostChatContribution', () => {
 			assert.strictEqual(chatSession.isCompleteObs!.get(), true);
 		}));

+		test('disposing chat session does not call disposeSession on connection', async () => {
+			const { sessionHandler, agentHostService } = createContribution(disposables);
+
+			const sessionResource = URI.from({ scheme: 'agent-host-copilot', path: '/existing-session-1' });
+			const chatSession = await sessionHandler.provideChatSessionContent(sessionResource, CancellationToken.None);
+
+			// Dispose the chat session (simulates user navigating away)
+			chatSession.dispose();
+
+			// disposeSession must NOT be called — the backend session should persist
+			assert.strictEqual(agentHostService.disposedSessions.length, 0,
+				'Disposing the UI chat session should not dispose the backend session');
+		});
+
 		test('client-dispatched turns are not treated as server-initiated', () => runWithFakedTimers({ useFakeTimers: true }, async () => {
 			const { sessionHandler, agentHostService } = createContribution(disposables);
PATCH

echo "Patch applied successfully."
