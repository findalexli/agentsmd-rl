# Token Usage Reporting Bug

## Bug Description

After the AI SDK v6 upgrade, token usage reporting is incorrect for some providers. The reported `total` token count and `input` token count are inflated — cached tokens appear to be counted twice in some cases.

## Observed Symptoms

- For some providers, `tokens.input` values are higher than expected
- For some providers, `tokens.total` values do not match the SDK's reported total
- Downstream cost calculations may be incorrect due to inflated token counts

## Expected Behavior

The `Session.getUsage` function should:

1. Return accurate non-cached input token counts in `tokens.input`
2. Return accurate cache token breakdowns via `tokens.cache.read` and `tokens.cache.write`
3. Return accurate totals in `tokens.total` that match SDK-provided values
4. Return accurate reasoning token counts in `tokens.reasoning`
5. Produce correct dollar amounts in the `cost` field

## Return Value Schema

The function returns an object with:
- `tokens.input` — non-cached input tokens (integer)
- `tokens.output` — output tokens (integer)
- `tokens.cache.read` — cached read tokens (integer)
- `tokens.cache.write` — cached write tokens (integer)
- `tokens.total` — total tokens (integer)
- `tokens.reasoning` — reasoning tokens (integer)
- `cost` — computed cost in dollars (float)

## Provider Context

The `metadata` parameter accepts provider-specific structures:
- Anthropic provider: `metadata: { anthropic: { cacheCreationInputTokens?: number } }`
- Amazon Bedrock provider: `metadata: { bedrock: { usage: { cacheWriteInputTokens: number } } }`
- Other providers: metadata may be omitted or empty

The provider is identified by the `model.api.npm` field (e.g., `"@ai-sdk/anthropic"`, `"@ai-sdk/amazon-bedrock"`, `"@ai-sdk/google-vertex/anthropic"`, `"@ai-sdk/openai"`).

## Relevant File

The token accounting logic is in `packages/opencode/src/session/index.ts`.

## Testing

Existing tests for session token handling are in `packages/opencode/test/session/compaction.test.ts`.
