# Bug Report: Add "Copy Final Response" Chat Context Menu Action

## Problem Description

The VS Code chat interface currently lacks a way to copy just the final prose answer from a model response. When a response includes tool calls followed by markdown content, users can only:
- Copy the entire response (including all tool calls and intermediate content)
- Copy the whole session history

There is no way to quickly copy only the final textual answer without selecting text manually.

## Expected Behavior

Add a "Copy Final Response" action to the chat context menu that:
1. Appears only on response items (not user messages)
2. Copies only the last contiguous block of non-empty markdown content
3. Skips trailing tool calls and empty markdown parts
4. Includes inline references as part of the final text

## Relevant Files

- `src/vs/workbench/contrib/chat/browser/actions/chatCopyActions.ts` - Contains existing copy actions
- `src/vs/workbench/contrib/chat/browser/widget/chatListWidget.ts` - Context menu overlay setup
- `src/vs/workbench/contrib/chat/common/model/chatModel.ts` - Response model interface and implementation

## Requirements

1. Add a `getFinalResponse()` method to the `IResponse` interface that walks backwards through response parts, collecting the last contiguous block of markdown, `markdownVuln`, and `inlineReference` parts while skipping trailing tool calls and empty content.

2. Register a new `CopyFinalResponseAction` in the context menu that:
   - Is gated by the `ChatContextKeys.isResponse` context key
   - Is hidden when the response is filtered
   - Uses the `copy` menu group
   - Writes `response.getFinalResponse()` to the clipboard

3. Fix the context key overlay in `chatListWidget.ts` to include the `isResponse` key so the menu visibility works correctly.

4. Update any existing mock response objects to include the new `getFinalResponse()` method.

5. Add unit tests covering:
   - Last contiguous markdown after tool calls
   - Skipping trailing empty markdown
   - Including inline references
   - Empty responses
   - All-markdown responses (no tool calls)

## Behavior Examples

Given a response with parts: `[markdown: "Hello"], [tool call], [markdown: "Answer: 42"]`, calling `getFinalResponse()` should return `"Answer: 42"`.

Given a response with parts: `[markdown: "Text"], [tool call], [markdown: ""]`, calling `getFinalResponse()` should return `"Text"` (empty trailing markdown is skipped).

Given a response with only: `[markdown: "Hello"], [markdown: "World"]`, calling `getFinalResponse()` should return `"Hello World"`.

Given a response with only tool calls (no markdown), calling `getFinalResponse()` should return an empty string.
