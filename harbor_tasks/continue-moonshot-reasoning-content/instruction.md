# Add reasoning_content field support for Moonshot Kimi models

## Problem

When using Kimi models (like `kimi-k2.5`) through the Moonshot provider with thinking/reasoning enabled, the API returns a 400 error:

```
400 thinking is enabled but reasoning_content is missing in assistant tool call message
```

The Moonshot provider needs to indicate that it supports the `reasoning_content` field for Kimi models, similar to how the DeepSeek provider already handles this.

## Context

- The file `core/llm/llms/Moonshot.ts` extends the OpenAI provider
- The DeepSeek provider (`core/llm/llms/Deepseek.ts`) already has this fix implemented and can serve as a reference
- The `supportsReasoningContentField` flag needs to be set based on whether the model name starts with "kimi"
- Non-Kimi Moonshot models (like `moonshot-v1-*`) should NOT have this flag set

## What You Need To Do

1. Modify `core/llm/llms/Moonshot.ts` to add a constructor that sets `supportsReasoningContentField` based on the model name
2. The flag should be `true` for models starting with "kimi" (e.g., `kimi-k2.5`, `kimi-k1.5`)
3. The flag should be `false` for non-kimi models (e.g., `moonshot-v1-8k`, `moonshot-v1-32k`)
4. Ensure the TypeScript code compiles without errors

## Key Considerations

- The fix should only affect Kimi models, not the standard Moonshot models
- Look at how Deepseek.ts implements this for guidance
- The constructor must call `super(options)` to preserve existing behavior
- TypeScript type safety must be maintained
