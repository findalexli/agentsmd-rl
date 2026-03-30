# fix(agents): handle unhandled stop reasons gracefully instead of crashing

## Problem

When the Anthropic provider adapter returns an unknown `stop_reason` (such as `"sensitive"`), the `mapStopReason()` function throws an error with the message `Unhandled stop reason: <reason>`. This error bubbles up through the embedded agent runner in `attempt.ts` and crashes the entire agent turn, stalling Telegram polling and any other channel waiting for a response.

## Root Cause

`mapStopReason()` in the Anthropic provider adapter throws for unknown stop reason values. The embedded agent runner (`src/agents/pi-embedded-runner/run/attempt.ts`) does not catch or handle this error, so it propagates as an uncaught runner error. Any provider-side addition of new stop reasons (like `"sensitive"` or `"refusal_policy"`) immediately breaks the agent.

## Expected Fix

1. Create a new recovery module (`src/agents/pi-embedded-runner/run/attempt.stop-reason-recovery.ts`) that wraps the stream function to intercept "Unhandled stop reason" errors.
2. Convert these errors into structured assistant error messages with a user-friendly message indicating the provider returned an unhandled stop reason, and suggesting the user rephrase and try again.
3. The wrapper must handle both the stream-event error path (errors emitted as events in the async stream) and the synchronous-throw path (errors thrown directly by the stream function).
4. Wire the wrapper into `attempt.ts` by wrapping `activeSession.agent.streamFn` before session history sanitization.

## Files to Modify

- `src/agents/pi-embedded-runner/run/attempt.stop-reason-recovery.ts` (new file)
- `src/agents/pi-embedded-runner/run/attempt.ts`
