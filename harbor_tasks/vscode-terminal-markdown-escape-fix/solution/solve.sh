#!/bin/bash
set -euo pipefail

# VS Code PR #306535: Remove unnecessary markdown escaping in terminal invocation messages
# Target file: src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts

TARGET_FILE="src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts"

# Check if already applied - look for the distinctive signature of the fix
# The fix removes 'escapeMarkdownSyntaxTokens' from the import and removes 'escapedDisplayCommand' variable
if ! grep -q "escapeMarkdownSyntaxTokens" "$TARGET_FILE" 2>/dev/null; then
    echo "Patch already applied or file not found"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
index a1bc09bf2e66b..bfc301ccaa20d 100644
--- a/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
+++ b/src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts
@@ -9,7 +9,7 @@ import { CancellationToken, CancellationTokenSource } from '../../../../../../base
 import { Codicon } from '../../../../../../base/common/codicons.js';
 import { CancellationError } from '../../../../../../base/common/errors.js';
 import { Event } from '../../../../../../base/common/event.js';
-import { escapeMarkdownSyntaxTokens, MarkdownString, type IMarkdownString } from '../../../../../../base/common/htmlContent.js';
+import { MarkdownString, type IMarkdownString } from '../../../../../../base/common/htmlContent.js';
 import { Disposable, DisposableStore, MutableDisposable } from '../../../../../../base/common/lifecycle.js';
 import { ResourceMap } from '../../../../../../base/common/map.js';
 import { getMediaMime } from '../../../../../../base/common/mime.js';
@@ -831,14 +831,13 @@ export class RunInTerminalTool extends Disposable implements IToolImpl {
 		const displayCommand = rawDisplayCommand.length > 80
 			? rawDisplayCommand.substring(0, 77) + '...'
 			: rawDisplayCommand;
-		const escapedDisplayCommand = escapeMarkdownSyntaxTokens(displayCommand);
 		const invocationMessage = toolSpecificData.commandLine.isSandboxWrapped
 			? args.isBackground
-				? new MarkdownString(localize('runInTerminal.invocation.sandbox.background', "Running `{0}` in sandbox in background", escapedDisplayCommand))
-				: new MarkdownString(localize('runInTerminal.invocation.sandbox', "Running `{0}` in sandbox", escapedDisplayCommand))
+				? new MarkdownString(localize('runInTerminal.invocation.sandbox.background', "Running `{0}` in sandbox in background", displayCommand))
+				: new MarkdownString(localize('runInTerminal.invocation.sandbox', "Running `{0}` in sandbox", displayCommand))
 			: args.isBackground
-				? new MarkdownString(localize('runInTerminal.invocation.background', "Running `{0}` in background", escapedDisplayCommand))
-				: new MarkdownString(localize('runInTerminal.invocation', "Running `{0}`", escapedDisplayCommand));
+				? new MarkdownString(localize('runInTerminal.invocation.background', "Running `{0}` in background", displayCommand))
+				: new MarkdownString(localize('runInTerminal.invocation', "Running `{0}`", displayCommand));

 		return {
 			invocationMessage,
PATCH

echo "Patch applied successfully"
