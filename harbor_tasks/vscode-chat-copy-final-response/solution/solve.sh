#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied (look for getFinalResponse in IResponse interface)
if grep -q "getFinalResponse(): string" src/vs/workbench/contrib/chat/common/model/chatModel.ts; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts b/src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts
index 42d67d3b3a579..e0bc6817f71fc 100644
--- a/src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts
+++ b/src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts
@@ -104,6 +104,45 @@ export function registerChatCopyActions() {
 		}
 	});

+	registerAction2(class CopyFinalResponseAction extends Action2 {
+		constructor() {
+			super({
+				id: 'workbench.action.chat.copyFinalResponse',
+				title: localize2('interactive.copyFinalResponse.label', "Copy Final Response"),
+				f1: false,
+				category: CHAT_CATEGORY,
+				menu: {
+					id: MenuId.ChatContext,
+					when: ContextKeyExpr.and(ChatContextKeys.isResponse, ChatContextKeys.responseIsFiltered.negate()),
+					group: 'copy',
+				}
+			});
+		}
+
+		async run(accessor: ServicesAccessor, ...args: unknown[]) {
+			const chatWidgetService = accessor.get(IChatWidgetService);
+			const clipboardService = accessor.get(IClipboardService);
+
+			const widget = chatWidgetService.lastFocusedWidget;
+			let item = args[0] as ChatTreeItem | undefined;
+			if (!isChatTreeItem(item)) {
+				item = widget?.getFocus();
+				if (!item) {
+					return;
+				}
+			}
+
+			if (!isResponseVM(item)) {
+				return;
+			}
+
+			const text = item.response.getFinalResponse();
+			if (text) {
+				await clipboardService.writeText(text);
+			}
+		}
+	});
+
 	registerAction2(class CopyKatexMathSourceAction extends Action2 {
 		constructor() {
 			super({
diff --git a/src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts b/src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts
index f183207775ddf..fc01578b02387 100644
--- a/src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts
+++ b/src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts
@@ -497,6 +497,7 @@ export class ChatListWidget extends Disposable {
 		const isKatexElement = target.closest(`.${katexContainerClassName}`) !== null;

 		const scopedContextKeyService = this.contextKeyService.createOverlay([
+			[ChatContextKeys.isResponse.key, isResponseVM(selected)],
 			[ChatContextKeys.responseIsFiltered.key, isResponseVM(selected) && !!selected.errorDetails?.responseIsFiltered],
 			[ChatContextKeys.isKatexMathElement.key, isKatexElement]
 		]);
diff --git a/src/vs/workbench/contrib/chat/common/model/chatModel.ts b/src/vs/workbench/contrib/chat/common/model/chatModel.ts
index d418832b971fe..1c220f71fad7e 100644
--- a/src/vs/workbench/contrib/chat/common/model/chatModel.ts
+++ b/src/vs/workbench/contrib/chat/common/model/chatModel.ts
@@ -234,6 +234,7 @@ export type IChatProgressRenderableResponseContent = Exclude<IChatProgressRespon
 export interface IResponse {
 	readonly value: ReadonlyArray<IChatProgressResponseContent>;
 	getMarkdown(): string;
+	getFinalResponse(): string;
 	toString(): string;
 }

@@ -471,6 +472,58 @@ class AbstractResponse implements IResponse {
 		return this._markdownContent;
 	}

+	/**
+	 * The trailing contiguous markdown/inline-reference content of the response,
+	 * skipping any trailing tool calls or empty markdown parts.
+	 */
+	getFinalResponse(): string {
+		const parts = this._responseParts;
+		// Walk backwards to find where the last contiguous markdown block starts.
+		// Phase 1: skip trailing non-markdown parts and empty markdown.
+		let i = parts.length - 1;
+		while (i >= 0) {
+			const part = parts[i];
+			if (part.kind === 'markdownContent' || part.kind === 'markdownVuln') {
+				if (part.content.value.length > 0) {
+					break;
+				}
+			} else if (part.kind === 'inlineReference') {
+				break;
+			}
+			i--;
+		}
+
+		if (i < 0) {
+			return '';
+		}
+
+		// Phase 2: collect contiguous markdown/inline-reference parts going backwards.
+		const end = i;
+		while (i >= 0) {
+			const part = parts[i];
+			if (part.kind === 'markdownContent' || part.kind === 'markdownVuln' || part.kind === 'inlineReference') {
+				i--;
+			} else {
+				break;
+			}
+		}
+		const start = i + 1;
+
+		// Combine the collected parts.
+		const segments: string[] = [];
+		for (let j = start; j <= end; j++) {
+			const part = parts[j];
+			if (part.kind === 'inlineReference') {
+				segments.push(this.inlineRefToRepr(part));
+			} else if (part.kind === 'markdownContent' || part.kind === 'markdownVuln') {
+				if (part.content.value.length > 0) {
+					segments.push(part.content.value);
+				}
+			}
+		}
+		return segments.join('');
+	}
+
 	/**
 	 * Invalidate cached representations so they are recomputed on next access.
 	 */
diff --git a/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentSessionApprovalModel.test.ts b/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentSessionApprovalModel.test.ts
index de54c6c14716d..f9836f765eae7 100644
--- a/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentSessionApprovalModel.test.ts
+++ b/src/vs/workbench/contrib/chat/test/browser/agentSessions/agentSessionApprovalModel.test.ts
@@ -77,7 +77,7 @@ function makeExecutingState(): IChatToolInvocation.State {
 /** Creates a minimal mock that satisfies the response chain: lastRequest.response.response.value */
 function mockModelWithResponse(model: MockChatModel, parts: IChatProgressResponseContent[]): void {
 	const response: Partial<IChatResponseModel> = {
-		response: { value: parts, getMarkdown: () => '', toString: () => '' } satisfies IResponse,
+		response: { value: parts, getMarkdown: () => '', getFinalResponse: () => '', toString: () => '' } satisfies IResponse,
 	};
 	const request: Partial<IChatRequestModel> = {
 		response: response as IChatResponseModel,
diff --git a/src/vs/workbench/contrib/chat/test/browser/agentSessions/localAgentSessionsController.test.ts b/src/vs/workbench/contrib/chat/test/browser/agentSessions/localAgentSessionsController.test.ts
index 6111539540230..f107fdce95666 100644
--- a/src/vs/workbench/contrib/chat/test/browser/agentSessions/localAgentSessionsController.test.ts
+++ b/src/vs/workbench/contrib/chat/test/browser/agentSessions/localAgentSessionsController.test.ts
@@ -73,6 +73,7 @@ function createMockChatModel(options: {
 			response: {
 				value: [],
 				getMarkdown: () => '',
+				getFinalResponse: () => '',
 				toString: () => options.customTitle ? '' : 'Test response content'
 			}
 		};
diff --git a/src/vs/workbench/contrib/chat/test/common/model/chatModel.test.ts b/src/vs/workbench/contrib/chat/test/common/model/chatModel.test.ts
index 8a3a743920751..3d1a017525641 100644
--- a/src/vs/workbench/contrib/chat/test/common/model/chatModel.test.ts
+++ b/src/vs/workbench/contrib/chat/test/common/model/chatModel.test.ts
@@ -612,6 +612,81 @@ suite('Response', () => {
 		assert.deepStrictEqual(response.value[0].toolSpecificData, toolSpecificData);
 		assert.strictEqual(IChatToolInvocation.isComplete(response.value[0]), true);
 	});
+
+	test('getFinalResponse returns last contiguous markdown after tool call', () => {
+		const response = store.add(new Response([]));
+		response.updateContent({ content: new MarkdownString('Early text'), kind: 'markdownContent' });
+		response.updateContent({
+			kind: 'externalToolInvocationUpdate',
+			toolCallId: 'tool-1',
+			toolName: 'some_tool',
+			isComplete: true,
+			invocationMessage: 'Ran tool',
+		});
+		response.updateContent({ content: new MarkdownString('Final text'), kind: 'markdownContent' });
+
+		assert.strictEqual(response.getFinalResponse(), 'Final text');
+	});
+
+	test('getFinalResponse skips trailing empty markdown and tool calls', () => {
+		const response = store.add(new Response([]));
+		response.updateContent({ content: new MarkdownString('Before tool'), kind: 'markdownContent' });
+		response.updateContent({
+			kind: 'externalToolInvocationUpdate',
+			toolCallId: 'tool-1',
+			toolName: 'some_tool',
+			isComplete: true,
+			invocationMessage: 'Ran tool',
+		});
+		response.updateContent({ content: new MarkdownString('The answer is 42.'), kind: 'markdownContent' });
+		response.updateContent({
+			kind: 'externalToolInvocationUpdate',
+			toolCallId: 'tool-2',
+			toolName: 'some_tool',
+			isComplete: true,
+			invocationMessage: 'Ran another tool',
+		});
+		response.updateContent({ content: new MarkdownString(''), kind: 'markdownContent' });
+
+		assert.strictEqual(response.getFinalResponse(), 'The answer is 42.');
+	});
+
+	test('getFinalResponse includes inline references in final block', () => {
+		const response = store.add(new Response([]));
+		response.updateContent({
+			kind: 'externalToolInvocationUpdate',
+			toolCallId: 'tool-1',
+			toolName: 'some_tool',
+			isComplete: true,
+			invocationMessage: 'Ran tool',
+		});
+		response.updateContent({ content: new MarkdownString('See '), kind: 'markdownContent' });
+		response.updateContent({ inlineReference: URI.parse('https://example.com/'), kind: 'inlineReference' });
+		response.updateContent({ content: new MarkdownString(' for details.'), kind: 'markdownContent' });
+
+		assert.strictEqual(response.getFinalResponse(), 'See https://example.com/ for details.');
+	});
+
+	test('getFinalResponse returns empty string when no markdown', () => {
+		const response = store.add(new Response([]));
+		response.updateContent({
+			kind: 'externalToolInvocationUpdate',
+			toolCallId: 'tool-1',
+			toolName: 'some_tool',
+			isComplete: true,
+			invocationMessage: 'Ran tool',
+		});
+
+		assert.strictEqual(response.getFinalResponse(), '');
+	});
+
+	test('getFinalResponse returns all markdown when there are no tool calls', () => {
+		const response = store.add(new Response([]));
+		response.updateContent({ content: new MarkdownString('Hello '), kind: 'markdownContent' });
+		response.updateContent({ content: new MarkdownString('World'), kind: 'markdownContent' });
+
+		assert.strictEqual(response.getFinalResponse(), 'Hello World');
+	});
 });

 suite('normalizeSerializableChatData', () => {
PATCH

echo "Patch applied successfully"
