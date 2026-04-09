# Plugin hook cannot modify maxOutputTokens

## Problem

The `chat.params` plugin hook allows plugins to modify LLM parameters like `temperature`, `topP`, and `topK` before they are sent to the model. However, `maxOutputTokens` is not exposed through this hook — it is computed independently and used directly in the `streamText` call, bypassing any plugin modifications.

A plugin that tries to adjust `maxOutputTokens` via the `chat.params` hook has no effect. The value is neither included in the hook's output parameter nor read back from the hook's return.

## Expected Behavior

Plugins should be able to modify `maxOutputTokens` through the `chat.params` hook, just like they can modify `temperature`, `topP`, and `topK`. The hook's output type should include `maxOutputTokens`, and the value returned by the hook should be what's passed to the model.

## Files to Look At

- `packages/opencode/src/session/llm.ts` — LLM streaming logic, where `maxOutputTokens` is computed and the `chat.params` hook is triggered
- `packages/plugin/src/index.ts` — TypeScript type definitions for the `Hooks` interface including `chat.params`
