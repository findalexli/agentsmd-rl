# Plugin hook cannot modify maxOutputTokens

## Problem

The `chat.params` plugin hook allows plugins to modify LLM parameters before they are sent to the model. The hook output type includes `temperature`, `topP`, `topK`, `maxOutputTokens`, and `options`. However, the implementation in `packages/opencode/src/session/llm.ts` has a bug: `maxOutputTokens` is computed after `Plugin.trigger("chat.params", ...)` is called, and the `streamText` function uses a local variable instead of the `params.maxOutputTokens` value returned from the hook. This means plugins cannot actually modify `maxOutputTokens` even though it appears in the hook type.

## Affected Files

- `packages/opencode/src/session/llm.ts` - Contains the `streamText` call and `Plugin.trigger("chat.params", ...)` hook invocation
- `packages/plugin/src/index.ts` - Contains the `chat.params` hook type definition

## Expected Behavior

When a plugin modifies `maxOutputTokens` via the `chat.params` hook, that modified value should be passed to the `streamText` function instead of the original computed value.

The hook output type in `packages/plugin/src/index.ts` defines:
```typescript
output: {
  temperature: number
  topP: number
  topK: number
  maxOutputTokens: number | undefined
  options: Record<string, any>
}
```

The `chat.params` hook must receive `maxOutputTokens` in its output object alongside `temperature`, `topP`, `topK`, and `options`, and the `streamText` call must use this value from the hook's return so that plugins can override it.
