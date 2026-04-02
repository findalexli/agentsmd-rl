#!/bin/bash
set -euo pipefail

# Idempotent patch application - vscode-chat-instructions-error-handling
# This wraps the instruction collection in try-catch to prevent blocking chat

cd /workspace/vscode

# Check if already applied (look for the try block around collect)
if grep -A2 "await computer.collect" src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts | grep -q "catch"; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix using git apply
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts b/src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts
index c6bf65d2c52f3..1fddece433ba6 100644
--- a/src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts
+++ b/src/vs/workbench/contrib/chat/browser/widget/chatWidget.ts
@@ -2819,13 +2819,16 @@ export class ChatWidget extends Disposable implements IChatWidget {
 			this.logService.debug(`ChatWidget#_autoAttachInstructions: skipped, autoAttachReferences is disabled`);
 			return;
 		}
-
-		this.logService.debug(`ChatWidget#_autoAttachInstructions: prompt files are enabled`);
-		const enabledTools = this.input.currentModeKind === ChatModeKind.Agent ? this.input.selectedToolsModel.userSelectedTools.get() : undefined;
-		const enabledSubAgents = this.input.currentModeKind === ChatModeKind.Agent ? this.input.currentModeObs.get().agents?.get() : undefined;
-		const sessionResource = this._viewModel?.model.sessionResource;
-		const computer = this.instantiationService.createInstance(ComputeAutomaticInstructions, this.input.currentModeKind, enabledTools, enabledSubAgents, sessionResource);
-		await computer.collect(attachedContext, CancellationToken.None);
+		try {
+			this.logService.debug(`ChatWidget#_autoAttachInstructions: prompt files are enabled`);
+			const enabledTools = this.input.currentModeKind === ChatModeKind.Agent ? this.input.selectedToolsModel.userSelectedTools.get() : undefined;
+			const enabledSubAgents = this.input.currentModeKind === ChatModeKind.Agent ? this.input.currentModeObs.get().agents?.get() : undefined;
+			const sessionResource = this._viewModel?.model.sessionResource;
+			const computer = this.instantiationService.createInstance(ComputeAutomaticInstructions, this.input.currentModeKind, enabledTools, enabledSubAgents, sessionResource);
+			await computer.collect(attachedContext, CancellationToken.None);
+		} catch (err) {
+			this.logService.error(`ChatWidget#_autoAttachInstructions: failed to compute automatic instructions`, err);
+		}
 	}

 	delegateScrollFromMouseWheelEvent(browserEvent: IMouseWheelEvent): void {
PATCH

echo "Patch applied successfully"
