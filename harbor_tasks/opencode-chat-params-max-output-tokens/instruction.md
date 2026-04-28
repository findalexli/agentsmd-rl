# Plugin hook cannot modify maxOutputTokens

## Problem

The `chat.params` plugin hook allows plugins to modify LLM parameters before they are sent to the model. The hook is implemented in `packages/opencode/src/session/llm.ts` and its interface is defined in `packages/plugin/src/index.ts`.

Plugins that use the `chat.params` hook expect to be able to override `maxOutputTokens`, but the value they set is ignored. Instead, the `streamText` call always receives the originally computed `maxOutputTokens` value rather than the one returned from `Plugin.trigger("chat.params", ...)`. This means plugins cannot actually control `maxOutputTokens` through the hook.

Additionally, the `chat.params` hook output object passed to the trigger does not include `maxOutputTokens`, so plugins receive no default value to inspect or modify.

## Affected Files

- `packages/opencode/src/session/llm.ts` - Contains the `streamText` call and `Plugin.trigger("chat.params", ...)` hook invocation
- `packages/plugin/src/index.ts` - Contains the `chat.params` hook type definition in the `Hooks` interface

## Expected Behavior

When a plugin modifies `maxOutputTokens` via the `chat.params` hook, the modified value must be used by the `streamText` call. The hook output object must include a `maxOutputTokens` field (typed as `number | undefined`) alongside the existing `temperature`, `topP`, `topK`, and `options` fields, so that plugins can read and optionally override the default value.

The `chat.params` hook output type and the `streamText` call must agree on `maxOutputTokens` — the hook must supply it and `streamText` must consume it from the hook's return value.
