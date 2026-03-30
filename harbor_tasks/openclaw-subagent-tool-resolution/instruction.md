# Fix: Sub-agent sessions fail to resolve plugin-registered tools

## Problem

When a sub-agent session starts, `createOpenClawTools()` resolves the tool list before `loadOpenClawPlugins()` has run for that session context. Plugin-registered tools (e.g., honcho memory tools) miss the resolution window entirely and appear as "unknown entries" in the allowlist.

The gateway start flow works correctly because plugins load during `gateway_start` before any session resolves tools -- the active registry already has everything.

## Root Cause

`resolveRuntimePluginRegistry()` compares cache keys to decide whether to reuse the active registry. Sub-agent callers pass different options (no `onlyPluginIds`, no `coreGatewayHandlers`) which produces a different cache key, so the active registry is bypassed and a fresh `loadOpenClawPlugins()` is triggered too late.

## Expected Behavior

Add a check: when the caller does not restrict the plugin set with gateway-specific fields (`onlyPluginIds`, `coreGatewayHandlers`, `includeSetupOnlyChannelPlugins`, `preferSetupRuntimeForChannelPlugins`), the active registry set during gateway startup is a safe superset. Reuse it directly instead of falling through to a redundant load.

## Files to Modify

- `src/plugins/tools.ts` -- add fallback to active registry for non-gateway-scoped callers
