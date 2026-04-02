#!/bin/bash
set -euo pipefail

# This fix removes the erroneous disposeSession() call that was causing
# backend sessions to disappear when the UI chat session was disposed.

TARGET_FILE="src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts"

# Check if fix already applied (idempotency)
if ! grep -q "this._config.connection.disposeSession(resolvedSession);" "$TARGET_FILE"; then
    echo "Fix already applied or file structure changed"
    exit 0
fi

echo "Applying fix..."

# Apply the patch to remove the disposeSession line
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts b/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts
index fd48e6d..dd95c6e 100644
--- a/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts
+++ b/src/vs/workbench/contrib/chat/browser/agentSessions/agentHost/agentHostSessionHandler.ts
@@ -302,7 +302,6 @@ export class AgentHostSessionHandler extends Disposable implements IChatSessionC
 			if (resolvedSession) {
 				this._clientState.unsubscribe(resolvedSession.toString());
 				this._config.connection.unsubscribe(resolvedSession);
-				this._config.connection.disposeSession(resolvedSession);
 			}
 		},
 	);
PATCH

echo "Fix applied successfully"
