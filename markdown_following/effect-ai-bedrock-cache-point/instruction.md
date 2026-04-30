# Fix cache point support for user and tool messages in Amazon Bedrock

## Task

Fix the `prepareMessages` function in `packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts` to properly handle cache points for user and tool messages.

## The Problem

When using Amazon Bedrock's prompt caching feature with user or tool messages that have cache point markers set in their provider options, the cache points are silently ignored — they never appear in the Bedrock API request content arrays.

The `prepareMessages` function converts messages to the Bedrock API format. It uses the `BEDROCK_CACHE_POINT` constant and the `getCachePoint` helper to detect cache point options on messages and include the appropriate marker in each message's content array. Currently, prompt caching works correctly for some message roles but not for user and tool messages. The `prepareMessages` function needs to be updated so that user and tool messages also include `BEDROCK_CACHE_POINT` in their content when a cache point is detected.

In the switch statement inside `prepareMessages`, both the `user` and `tool` roles are handled together in the `case "user":` block. The fix should add cache point handling to this case block so that both user and tool messages with cache point markers are properly handled.

## Verification

After the fix, TypeScript compilation should still pass. The cache point handling should work correctly for all message types that support cache point options, including user and tool messages.