# Fix Anthropic Claude Model Max Window Tokens + Update Agent Skills

## Problem

Anthropic Claude models are configured with incorrect `max_tokens` values that are too low. The `resolveMaxTokens` function in the model runtime returns only 8192 tokens for normal-context Claude models, which severely limits response length. Similarly, `generateObject` hardcodes a low `max_tokens: 8192` when calling the Anthropic API. Additionally, the `toolResultMaxLength` default in the agent chat config is set to 6000 characters, causing tool execution results to be truncated too aggressively.

The agent tools engine also has a logic issue where `LocalSystem` tool is enabled whenever a device is online and a gateway is configured, but it should also require the device to be explicitly `autoActivated`. The `RemoteDevice` tool should be disabled when a device is already auto-activated.

The agent tracing viewer doesn't show tool errors by default — users must pass the `-t` flag to see failed tool results, making debugging harder.

## Expected Behavior

- `resolveMaxTokens` should return 64000 (not 8192) for normal-context Anthropic models
- `generateObject` should use 64000 as the default max_tokens
- `toolResultMaxLength` default should be 25000 (not 6000) characters
- `LocalSystem` tool should only be enabled when the device is auto-activated
- `RemoteDevice` tool should be disabled when a device is already auto-activated
- Tool errors should be displayed by default in the tracing viewer

Additionally, several `.agents/skills/` SKILL.md files need updates:
- A new `trpc-router` skill should document TRPC router development patterns (middleware, procedures, conventions)
- The `cli` skill should document dev mode usage and local development server setup
- The `db-migrations` skill Step 4 should be updated to describe journal tag updates

## Files to Look At

- `packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts` — resolves max_tokens for Anthropic API calls
- `packages/model-runtime/src/core/anthropicCompatibleFactory/generateObject.ts` — creates Anthropic API calls for structured output
- `packages/types/src/agent/chatConfig.ts` — agent chat config schema with toolResultMaxLength
- `src/server/modules/Mecha/AgentToolsEngine/index.ts` — server-side tool enable/disable logic
- `packages/agent-tracing/src/viewer/index.ts` — tracing viewer step detail renderer
- `.agents/skills/` — agent skill documentation files
