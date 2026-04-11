# Fix: propagate providerData for function_call items in chat completions converter

## Problem

When using the OpenAI Chat Completions API adapter, `providerData` attached to `function_call` items is silently dropped during message conversion. The `function_call_result` path already spreads `providerData` onto the tool message, and the `unknown` item path does the same — but the `function_call` branch constructs an assistant message without carrying over any provider-specific fields.

This means if a caller attaches custom provider data to a function call item (e.g. for routing, tracing, or provider-specific extensions), that data is lost when the item is converted to a chat completions message.

## Expected Behavior

`providerData` on `function_call` items should be propagated onto the resulting assistant message, just as it already is for `function_call_result` and `unknown` item types.

## Files to Look At

- `packages/agents-openai/src/openaiChatCompletionsConverter.ts` — the `itemsToMessages()` function handles each item type; the `function_call` branch is missing providerData propagation
- `CONTRIBUTING.md` — the PR submission checklist has a stale build verification command that should be updated to match the actual required steps documented in `AGENTS.md`
