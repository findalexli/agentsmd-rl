# Task: Fix Gemini API Message Ordering Errors

## Symptom

When using the Gemini API integration in `continue`, sending messages that contain consecutive tool responses followed by more tool calls or user messages causes the API to return a 400 error. This happens because Gemini enforces a strict requirement: messages must strictly alternate between "user" and "model" roles, but multi-turn tool conversations can produce consecutive messages with the same role (e.g., multiple consecutive "user" turns from tool responses).

## Affected Code Locations

Two integration points handle message formatting for Gemini:

1. `packages/openai-adapters/src/apis/Gemini.ts` - The `GeminiApi._convertBody()` method converts OpenAI-compatible chat messages to Gemini's `contents` format. This is used when Gemini is accessed via the OpenAI adapter (e.g., for VertexAI compatibility).

2. `core/llm/llms/Gemini.ts` - The `Gemini.prepareBody()` method does the same conversion for the native continue core LLM integration.

## Expected Behavior

When consecutive messages have the same role (e.g., two "user" messages in a row from tool responses), they should be merged into a single message with combined `parts` arrays before being sent to the Gemini API.

For example:
- Input: `[{role: "user", parts: [...]}, {role: "user", parts: [...]}]`
- Output: `[{role: "user", parts: [...merge...]}]`

This allows the Gemini API to receive properly alternating message sequences.

A message-merging utility must be created and applied at both integration points above.

## Verification

After the fix, the following should hold:
- A message-merging utility exists in both `packages/openai-adapters/src/util/gemini-types.ts` and `core/llm/llms/gemini-types.ts`
- Both integration points apply this merging before sending requests
- TypeScript compiles without errors
- Existing vitest tests pass

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
