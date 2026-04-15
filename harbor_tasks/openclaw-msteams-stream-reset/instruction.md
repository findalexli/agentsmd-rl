# MS Teams multi-segment response text loss

## Symptom

When an agent uses tools mid-response in Microsoft Teams, text sent after tool calls is silently lost or the response becomes fragmented into duplicate messages. The `preparePayload()` method in the reply stream controller incorrectly suppresses all text segments after the first one, because a state flag that tracks whether tokens have been received never resets after the first segment is handled.

## Observed Behavior

- First text segment: correctly suppressed (fallback proactive messaging used instead)
- Second text segment (after tool call): incorrectly suppressed — should be delivered normally
- Media payloads (containing `mediaUrl` or `mediaUrls`): pass through with text field stripped
- Group chat (`conversationType: "groupChat"`): all payloads pass through unchanged

## Target File

`extensions/msteams/src/reply-stream-controller.ts`

## Expected Correct Behavior

After the fix, when a text segment is suppressed, subsequent text segments must NOT be suppressed. The controller must track whether the stream has been finalized and must not re-suppress a finalized stream. The controller provides a `finalize()` method that callers use to clean up.

## Test Scenarios

The behavioral tests exercise the controller through its public API:

1. Call `createTeamsReplyStreamController(...)` with `{ conversationType, context, feedbackLoopEnabled, log }`
2. Call `ctrl.onPartialReply({ text })` to signal incoming tokens
3. Call `ctrl.preparePayload({ text })` and check the return value:
   - Returns `undefined` when the segment is suppressed
   - Returns a payload object (with `text` field) when the segment should be delivered
4. After `preparePayload` suppresses a segment, verify `stream.isFinalized` is `true`
5. Call `ctrl.finalize()` and verify it completes without error

For media payloads containing `mediaUrl` or `mediaUrls`, the text field is stripped but the payload is still delivered. Text-only payloads are suppressed.

## Constraint

The solution must not add `@ts-nocheck` or eslint-disable comments. The file must contain at least 40 non-trivial lines of real implementation.