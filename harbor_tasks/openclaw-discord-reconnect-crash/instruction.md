# Fix: Discord gateway crashes on queued reconnect-exhausted event before teardown

## Problem

Discord stale-socket restarts crash the whole gateway when a `reconnect-exhausted` event is buffered in the pending gateway events queue before lifecycle teardown flips `lifecycleStopping`. A Discord WebSocket close with code 1005 can kill the full gateway process instead of letting the channel health monitor restart Discord cleanly.

## Root Cause

In `extensions/discord/src/monitor/provider.lifecycle.ts`, the `drainPendingGatewayErrors()` function only suppressed `reconnect-exhausted` when `lifecycleStopping` was already true. But the supervisor can drain a buffered `reconnect-exhausted` event before teardown flips that flag. In this race condition, the event is treated as fatal and throws `Max reconnect attempts (0) reached after code 1005`, crashing the process.

## Expected Behavior

Treat `reconnect-exhausted` as a graceful stop event regardless of whether `lifecycleStopping` has been flipped yet, since the health monitor already owns reconnect recovery for this path. The fix should make the condition check `event.type === "reconnect-exhausted"` without requiring `lifecycleStopping` to be true.

## File to Modify

- `extensions/discord/src/monitor/provider.lifecycle.ts`
