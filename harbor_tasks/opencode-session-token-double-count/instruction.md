# Token Usage Double-Counting for Anthropic/Bedrock Providers

## Bug Description

After the AI SDK v6 upgrade (merged in v1.3.4), token usage reporting is broken for Anthropic and Bedrock providers. The reported `total` token count and `tokens.input` are inflated — cached tokens are being counted twice.

## Root Cause Area

The token accounting logic lives in `packages/opencode/src/session/index.ts`, in the `getUsage` function within the `Session` namespace (around line 265–295).

AI SDK v6 changed how `inputTokens` is reported: it now includes cached tokens for **all** providers, including Anthropic and Bedrock. Previously, those two providers excluded cached tokens from `inputTokens`.

The current code has a provider-specific check (`excludesCachedTokens`) that skips the cache subtraction for Anthropic/Bedrock. Since v6 now includes cache in `inputTokens` for those providers too, the subtraction should always happen. The current logic causes:

1. `tokens.input` to be too high (cache tokens counted once in `inputTokens`, not subtracted)
2. `tokens.total` to be too high (a provider-specific branch manually recomputes total from components, double-adding cache)

## Expected Behavior

- `tokens.input` should always equal `inputTokens - cacheRead - cacheWrite` (the non-cached portion)
- `tokens.total` should use the SDK-provided `totalTokens` uniformly across all providers
- Cost calculations downstream should reflect correct token counts

## Relevant Files

- `packages/opencode/src/session/index.ts` — the `getUsage` function
- `packages/opencode/test/session/compaction.test.ts` — existing tests for `getUsage`

## Hints

- Look at how `adjustedInputTokens` is computed and whether the provider check is still valid after v6
- Look at how `total` is computed — there's a provider-specific branch that should no longer be needed
- The fix should make token handling uniform across all providers
