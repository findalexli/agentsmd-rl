# Fix: Discord gateway crashes on queued reconnect-exhausted event before teardown

## Problem

Discord stale-socket restarts cause the full gateway to crash when a `reconnect-exhausted` event is already buffered in the pending gateway events queue before lifecycle teardown begins. A Discord WebSocket close with code 1005 can kill the entire gateway process instead of allowing the channel health monitor to restart Discord cleanly.

## Root Cause

In `extensions/discord/src/monitor/provider.lifecycle.ts`, the `drainPendingGatewayErrors()` function only handles `reconnect-exhausted` as a graceful stop when `lifecycleStopping` is already true. However, the supervisor can drain a buffered `reconnect-exhausted` event before teardown flips that flag. In this race condition, the event is treated as fatal and throws an error, crashing the process.

## Expected Behavior

The `reconnect-exhausted` event type should be treated as a graceful stop event unconditionally, regardless of whether `lifecycleStopping` has been flipped yet, since the health monitor already owns reconnect recovery for this path.

## File to Modify

- `extensions/discord/src/monitor/provider.lifecycle.ts`
