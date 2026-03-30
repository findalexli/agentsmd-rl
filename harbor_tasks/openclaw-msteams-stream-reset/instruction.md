# Fix: MS Teams drops text after tool calls in multi-segment responses

## Problem

When an agent uses tools mid-response in Microsoft Teams, the LLM produces discontinuous text segments (text -> tool calls -> more text). The `preparePayload()` method in `reply-stream-controller.ts` suppresses fallback delivery for ALL text segments because `streamReceivedTokens` stays `true` permanently. The second text segment after tool calls is silently lost or the response gets fragmented into duplicate messages.

## Root Cause

`preparePayload()` uses a one-shot `streamReceivedTokens` flag that never resets after the first segment is streamed. When the first segment completes and the stream has content, the fallback delivery is suppressed (correctly). But for subsequent text segments after tool calls, the flag remains true, causing the same suppression logic to fire -- even though the stream never saw those tokens. There is also no `isFinalized` guard, so `onPartialReply` can re-trigger suppression after the stream should have been done.

## Expected Behavior

1. After suppressing the first text segment, reset `streamReceivedTokens` and finalize the stream
2. Add an `isFinalized` guard so a finalized stream never re-suppresses fallback delivery
3. Subsequent text segments (after tool calls) should use fallback proactive messaging delivery

## Files to Modify

- `extensions/msteams/src/reply-stream-controller.ts`
