#!/bin/bash
# [pr_diff] Apply the gold patch for vscode-chat-startover-action
set -euo pipefail

cd /workspace/vscode

# Check if already applied (idempotency check)
if git diff HEAD | grep -q "StartOverAction" 2>/dev/null || grep -q "StartOverAction" src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the fix
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts b/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts
index c0768d6b70a59..d7f8eed7462e8 100644
--- a/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts
+++ b/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts
@@ -39,6 +39,7 @@ export function registerChatForkActions() {
 						order: 3,
 						when: ContextKeyExpr.and(
 							ChatContextKeys.isRequest,
+							ChatContextKeys.isFirstRequest.negate(),
 							ContextKeyExpr.or(
 								ChatContextKeys.lockedToCodingAgent.negate(),
 								ChatContextKeys.chatSessionSupportsFork
diff --git a/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts b/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts
index 4913141987b90..4669ede9df92a 100644
--- a/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts
+++ b/src/vs/workbench/contrib/chat/browser/chatEditing/chatEditingActions.ts
@@ -583,7 +583,7 @@ registerAction2(class RestoreCheckpointAction extends Action2 {
 					id: MenuId.ChatMessageCheckpoint,
 					group: 'navigation',
 					order: 2,
-					when: ContextKeyExpr.and(ChatContextKeys.isRequest, ChatContextKeys.lockedToCodingAgent.negate())
+					when: ContextKeyExpr.and(ChatContextKeys.isRequest, ChatContextKeys.lockedToCodingAgent.negate(), ChatContextKeys.isFirstRequest.negate())
 				}
 			]
 		});
@@ -617,6 +617,42 @@ registerAction2(class RestoreCheckpointAction extends Action2 {
 	}
 });

+registerAction2(class StartOverAction extends Action2 {
+	constructor() {
+		super({
+			id: 'workbench.action.chat.startOver',
+			title: localize2('chat.startOver.label', "Start Over"),
+			tooltip: localize2('chat.startOver.tooltip', "Clears the chat and undoes all changes"),
+			f1: false,
+			category: CHAT_CATEGORY,
+			menu: [
+				{
+					id: MenuId.ChatMessageCheckpoint,
+					group: 'navigation',
+					order: 2,
+					when: ContextKeyExpr.and(ChatContextKeys.isRequest, ChatContextKeys.lockedToCodingAgent.negate(), ChatContextKeys.isFirstRequest)
+				}
+			]
+		});
+	}
+
+	async run(accessor: ServicesAccessor, ...args: unknown[]) {
+		let item = args[0] as ChatTreeItem | undefined;
+		const chatWidgetService = accessor.get(IChatWidgetService);
+		const widget = (isChatTreeItem(item) && chatWidgetService.getWidgetBySessionResource(item.sessionResource)) || chatWidgetService.lastFocusedWidget;
+		if (!isResponseVM(item) && !isRequestVM(item)) {
+			item = widget?.getFocus();
+		}
+
+		if (!item) {
+			return;
+		}
+
+		widget?.viewModel?.model.setCheckpoint(item.id);
+		await restoreSnapshotWithConfirmation(accessor, item);
+	}
+});
+
 registerAction2(class RestoreLastCheckpoint extends Action2 {
 	constructor() {
 		super({
diff --git a/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts b/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts
index a33f39ab401aa..742a67eeb14e5 100644
--- a/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts
+++ b/src/vs/workbench/contrib/chat/browser/widget/chatListRenderer.ts
@@ -709,6 +709,7 @@ export class ChatListItemRenderer extends Disposable implements ITreeRenderer<Ch
 		ChatContextKeys.isResponse.bindTo(templateData.contextKeyService).set(isResponseVM(element));
 		ChatContextKeys.itemId.bindTo(templateData.contextKeyService).set(element.id);
 		ChatContextKeys.isRequest.bindTo(templateData.contextKeyService).set(isRequestVM(element));
+		ChatContextKeys.isFirstRequest.bindTo(templateData.contextKeyService).set(isRequestVM(element) && this.viewModel?.model.getRequests()[0]?.id === element.id);
 		ChatContextKeys.isPendingRequest.bindTo(templateData.contextKeyService).set(isRequestVM(element) && !!element.pendingKind);
 		ChatContextKeys.responseDetectedAgentCommand.bindTo(templateData.contextKeyService).set(isResponseVM(element) && element.agentOrSlashCommandDetected);
 		if (isResponseVM(element)) {
diff --git a/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts b/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts
index 64b70535c91cc..146941eba61a0 100644
--- a/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts
+++ b/src/vs/workbench/contrib/chat/common/actions/chatContextKeys.ts
@@ -30,6 +30,7 @@ export namespace ChatContextKeys {

 	export const isResponse = new RawContextKey<boolean>('chatResponse', false, { type: 'boolean', description: localize('chatResponse', "The chat item is a response.") });
 	export const isRequest = new RawContextKey<boolean>('chatRequest', false, { type: 'boolean', description: localize('chatRequest', "The chat item is a request") });
+	export const isFirstRequest = new RawContextKey<boolean>('chatFirstRequest', false, { type: 'boolean', description: localize('chatFirstRequest', "The chat item is the first request in the session.") });
 	export const isPendingRequest = new RawContextKey<boolean>('chatRequestIsPending', false, { type: 'boolean', description: localize('chatRequestIsPending', "True when the chat request item is pending in the queue.") });
 	export const itemId = new RawContextKey<string>('chatItemId', '', { type: 'string', description: localize('chatItemId', "The id of the chat item.") });
 	export const lastItemId = new RawContextKey<string[]>('chatLastItemId', [], { type: 'string', description: localize('chatLastItemId', "The id of the last chat item.") });
PATCH

echo "Patch applied successfully"
