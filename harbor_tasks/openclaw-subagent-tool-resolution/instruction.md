# Fix: Sub-agent sessions fail to resolve plugin-registered tools

## Problem

When a sub-agent session starts, plugin-registered tools (e.g., honcho memory tools) appear as "unknown entries" in the allowlist instead of being resolved. The function that resolves plugin tools currently calls a loader function directly to obtain the plugin registry, ignoring any active registry that was set during gateway startup. Sub-agent sessions that pass `allowGatewaySubagentBinding: true` should reuse the gateway's active registry instead of triggering a redundant plugin load.

The gateway start flow works correctly because plugins load during `gateway_start` before any session resolves tools — the active registry already has everything.

## Root Cause

The loader function compares cache keys to decide whether to reuse the active registry. Sub-agent callers pass different options (no `onlyPluginIds`, no `coreGatewayHandlers`) which produces a different cache key, so the active registry is bypassed and a fresh plugin load is triggered too late.

## Expected Behavior

When `allowGatewaySubagentBinding` is `true`, the active plugin registry (if one exists) must be used instead of always calling the loader. The fix must:

1. Access the active plugin registry through the runtime module
2. When `allowGatewaySubagentBinding` is `true`, check for an active registry first and reuse it if available
3. Only fall back to the loader when no active registry is available
4. The loader must still be imported and remain available as the fallback mechanism

## Structural Requirements

- The file must remain valid TypeScript with balanced braces
- The main exported function for resolving plugin tools must still exist and be exported
- The active registry check must happen before or in place of the direct loader call
- The loader must not be called directly at the assignment site in the main exported function; instead, the call should go through logic that handles the active registry check

## Context

The runtime module exports `getActivePluginRegistry()` which returns the currently active plugin registry or undefined if none exists. The loader module exports `resolveRuntimePluginRegistry()` which loads plugins from scratch. The sub-agent session context indicates whether gateway binding is allowed via the `allowGatewaySubagentBinding` parameter.
