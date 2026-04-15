# Plugin hook cannot modify maxOutputTokens

## Problem

The `chat.params` plugin hook allows plugins to modify LLM parameters like `temperature`, `topP`, and `topK` before they are sent to the model. However, `maxOutputTokens` is not exposed through this hook — it is computed independently and used directly in the `streamText` call, bypassing any plugin modifications.

A plugin that tries to adjust `maxOutputTokens` via the `chat.params` hook has no effect. The value is neither included in the hook's output parameter nor read back from the hook's return.

## Expected Behavior

Plugins should be able to modify `maxOutputTokens` through the `chat.params` hook, just like they can modify `temperature`, `topP`, and `topK`.

Specifically:

1. The `chat.params` hook output type must include `maxOutputTokens` with type `number | undefined` alongside the existing fields `temperature`, `topP`, `topK`, and `options`

2. The `maxOutputTokens` value must be computed **before** the `Plugin.trigger("chat.params", ...)` call is made, so that it can be included in the output object passed to the hook

3. The `chat.params` hook output object passed to plugins must contain `maxOutputTokens` alongside `temperature`, `topP`, `topK`, and `options`

4. The `streamText` call must use `params.maxOutputTokens` (the value returned from the hook) rather than a bare local variable, so that plugins can override the value

The hook's output type should be:
```typescript
output: {
  temperature: number
  topP: number
  topK: number
  maxOutputTokens: number | undefined
  options: Record<string, any>
}
```
