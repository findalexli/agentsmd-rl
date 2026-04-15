# Fix: Sub-agent sessions fail to resolve plugin-registered tools

## Problem

When a sub-agent session starts, plugin-registered tools (e.g., honcho memory tools) appear as "unknown entries" in the allowlist instead of being resolved. The exported function `resolvePluginTools` in `src/plugins/tools.ts` currently calls `resolveRuntimePluginRegistry` (imported from `./loader.js`) directly to obtain the plugin registry, ignoring any active registry that was set during gateway startup. Sub-agent sessions that pass `allowGatewaySubagentBinding: true` should reuse the gateway's active registry instead of triggering a redundant plugin load.

The gateway start flow works correctly because plugins load during `gateway_start` before any session resolves tools — the active registry already has everything.

## Root Cause

`resolveRuntimePluginRegistry()` compares cache keys to decide whether to reuse the active registry. Sub-agent callers pass different options (no `onlyPluginIds`, no `coreGatewayHandlers`) which produces a different cache key, so the active registry is bypassed and a fresh `loadOpenClawPlugins()` is triggered too late.

## Expected Behavior

The `resolvePluginTools` function must be updated to:

1. Import `getActivePluginRegistry` from `./runtime.js` to access the gateway's active registry.

2. When `allowGatewaySubagentBinding` is `true`, first check for an active registry using `getActivePluginRegistry()`. If one exists, reuse it. Only fall back to calling `resolveRuntimePluginRegistry` if no active registry is available.

3. The direct `resolveRuntimePluginRegistry(loadOptions)` call inside `resolvePluginTools` must be replaced with logic that accounts for the active registry — `resolvePluginTools` should not unconditionally assign the result of `resolveRuntimePluginRegistry(...)` to the `registry` variable. `resolveRuntimePluginRegistry` must still be imported and used as the fallback when no active registry exists.

## Files to Modify

- `src/plugins/tools.ts` — add the `getActivePluginRegistry` import from `./runtime.js` and restructure how `resolvePluginTools` resolves the plugin registry
