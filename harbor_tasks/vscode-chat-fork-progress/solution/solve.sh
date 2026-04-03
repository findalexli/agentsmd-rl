#!/bin/bash
set -euo pipefail

# Apply the fix for vscode chat fork actions
# This removes IProgressService dependency and adds deduplication for concurrent forks

cd /workspace/vscode

# Check if already applied
if grep -q "private pendingFork = new Map<string" src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Apply the patch
git apply - << 'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts b/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts
index d7f8eed7462e8..57b337a8ccc4e 100644
--- a/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts
+++ b/src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts
@@ -12,7 +12,6 @@ import { localize, localize2 } from '../../../../../nls.js';
 import { Action2, MenuId, registerAction2 } from '../../../../../platform/actions/common/actions.js';
 import { ContextKeyExpr } from '../../../../../platform/contextkey/common/contextkey.js';
 import { ServicesAccessor } from '../../../../../platform/instantiation/common/instantiation.js';
-import { IProgressService } from '../../../../../platform/progress/common/progress.js';
 import { ChatContextKeys } from '../../common/actions/chatContextKeys.js';
 import { IChatService, ResponseModelState } from '../../common/chatService/chatService.js';
 import type { ISerializableChatData } from '../../common/model/chatModel.js';
@@ -54,7 +53,6 @@ export function registerChatForkActions() {
 			const chatWidgetService = accessor.get(IChatWidgetService);
 			const chatService = accessor.get(IChatService);
 			const chatSessionsService = accessor.get(IChatSessionsService);
-			const progressService = accessor.get(IProgressService);
 			const forkedTitlePrefix = localize('chat.forked.titlePrefix', "Forked: ");

 			// When invoked via /fork slash command, args[0] is a URI (sessionResource).
@@ -65,8 +63,7 @@ export function registerChatForkActions() {
 				// Check if this is a contributed session that supports forking
 				const contentProviderSchemes = chatSessionsService.getContentProviderSchemes();
 				if (contentProviderSchemes.includes(sourceSessionResource.scheme)) {
-					await forkContributedChatSession(sourceSessionResource, undefined, false, chatSessionsService, chatWidgetService, progressService);
-					return;
+					return await this.forkContributedChatSession(sourceSessionResource, undefined, false, chatSessionsService, chatWidgetService);
 				}

 				const chatModel = chatService.getSession(sourceSessionResource);
@@ -165,8 +162,7 @@ export function registerChatForkActions() {
 						}
 					}
 				}
-				await forkContributedChatSession(sessionResource, request, true, chatSessionsService, chatWidgetService, progressService);
-				return;
+				return await this.forkContributedChatSession(sessionResource, request, true, chatSessionsService, chatWidgetService);
 			}

 			const chatModel = chatService.getSession(sessionResource);
@@ -231,10 +227,28 @@ export function registerChatForkActions() {
 			await chatWidgetService.openSession(newSessionResource, ChatViewPaneTarget);
 			modelRef.dispose();
 		}
+
+		private pendingFork = new Map<string, Promise<void>>();
+
+		private async forkContributedChatSession(sourceSessionResource: URI, request: IChatSessionRequestHistoryItem | undefined, openForkedSessionImmediately: boolean, chatSessionsService: IChatSessionsService, chatWidgetService: IChatWidgetService) {
+			const pendingKey = `${sourceSessionResource.toString()}@${request?.id ?? 'full'}`;
+			const pending = this.pendingFork.get(pendingKey);
+			if (pending) {
+				return pending;
+			}
+
+			const forkPromise = forkContributedChatSession(sourceSessionResource, request, openForkedSessionImmediately, chatSessionsService, chatWidgetService);
+			this.pendingFork.set(pendingKey, forkPromise);
+			try {
+				await forkPromise;
+			} finally {
+				this.pendingFork.delete(pendingKey);
+			}
+		}
 	});
 }

-async function forkContributedChatSession(sourceSessionResource: URI, request: IChatSessionRequestHistoryItem | undefined, openForkedSessionImmediately: boolean, chatSessionsService: IChatSessionsService, chatWidgetService: IChatWidgetService, progressService: IProgressService) {
+async function forkContributedChatSession(sourceSessionResource: URI, request: IChatSessionRequestHistoryItem | undefined, openForkedSessionImmediately: boolean, chatSessionsService: IChatSessionsService, chatWidgetService: IChatWidgetService) {
 	const cts = new CancellationTokenSource();
 	try {
 		const forkedItem = await chatSessionsService.forkChatSession(sourceSessionResource, request, cts.token);
PATCH

echo "Fix applied successfully"
