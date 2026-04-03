# Sync: Fix incomplete catch-up after offline periods and update documentation

## Problem

When a device goes offline and comes back online during the same app session, the Matrix sync pipeline fails to catch up on missed events. Two issues:

1. **No catch-up trigger on reconnect**: The stream consumer only triggers a catch-up on the very first stream event after startup. If the device goes offline and returns during the same session, the catch-up guard (`_initialCatchUpCompleted`) is already set to `true` and never resets, so only a live scan runs — which only processes the ~10 most recent events, missing everything in between.

2. **Incomplete backlog retrieval**: Even when catch-up does run, the `needsMore()` function in `catch_up_strategy.dart` stops escalating the snapshot size once it finds the marker and satisfies pre-context requirements. If the timeline has 5000 events but the snapshot only holds 400, catch-up returns just 400 events and stops — missing thousands of events after the marker.

Both issues result in missing EntryLinks (gray boxes) in the UI after offline periods.

3. **Self-origin echo events**: During prefetch/dedup, events sent by the current device are not suppressed unless they were in the sent-event registry. This causes duplicate processing when events echo back from the server.

## Expected Behavior

- Every client stream signal should trigger a catch-up, not just the first one. Use an in-flight guard to prevent overlapping catch-ups instead of one-shot flags.
- Catch-up should continue escalating the snapshot size until the snapshot is no longer full (meaning we've reached the timeline boundary), not just until pre-context requirements are met.
- Self-origin events (where the sender matches the current user) should be suppressed during processing.

## Files to Look At

- `lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart` — the stream consumer that handles signals and catch-up orchestration
- `lib/features/sync/matrix/pipeline/catch_up_strategy.dart` — the `needsMore()` function that controls escalation

After fixing the code, update the relevant sync documentation to reflect the new signal-driven catch-up behavior and corrected file paths. The project's AGENTS.md requires keeping feature READMEs up to date alongside code changes.
