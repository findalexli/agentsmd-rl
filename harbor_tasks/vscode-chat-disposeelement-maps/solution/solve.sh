#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency check
if grep -q "These maps are only read for the focused response which is always visible" src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --3way - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts b/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts
index a3c6e75b168d3..05973d9999804 100644
--- a/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts
+++ b/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts
@@ -2525,6 +2525,20 @@ export class ChatListItemRenderer extends Disposable implements ITreeRenderer<Ch
 			this.templateDataByRequestId.delete(templateData.currentElement.id);
 		}

+		// These maps are only read for the focused response which is always visible,
+		// so we can clean up entries for elements that leave the viewport.
+		const codeBlocks = this.codeBlocksByResponseId.get(node.element.id);
+		if (codeBlocks) {
+			for (const info of codeBlocks) {
+				if (info?.uri) {
+					this.codeBlocksByEditorUri.delete(info.uri);
+				}
+			}
+			this.codeBlocksByResponseId.delete(node.element.id);
+		}
+		this.fileTreesByResponseId.delete(node.element.id);
+		this.focusedFileTreesByResponseId.delete(node.element.id);
+
 		if (isRequestVM(node.element) && node.element.id === this.viewModel?.editing?.id && details?.onScroll) {
 			this._onDidDispose.fire(templateData);
 		}
PATCH

echo "Patch applied successfully."
