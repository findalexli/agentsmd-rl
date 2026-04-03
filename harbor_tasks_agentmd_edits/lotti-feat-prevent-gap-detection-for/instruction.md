# Prevent False Positive Gap Detection for Never-Seen Hosts

## Problem

The sync sequence log service detects gaps in message sequences by examining vector clocks from incoming messages. Currently, it checks ALL hosts present in a vector clock for gaps — including hosts that this device has never directly communicated with.

This causes false positive gap detection: when Device A receives a message from Device B whose vector clock references Device C's counter, the system flags missing entries for Device C even though we've never received a message from Device C directly. We're seeing counters for C only because B included them in its vector clock, but we have no way to know which entries from C are actually missing versus ones we simply haven't received yet because we've never talked to C.

These false positives trigger unnecessary backfill requests and pollute the sequence log with entries that can never be resolved.

## Expected Behavior

Gap detection should only run for hosts that have been seen "online" — meaning they have sent us a message directly (tracked via the `HostActivity` table). If a host has never been seen online, we should skip gap detection for it but still record its sequence entry so we can respond to backfill requests later if that host comes online.

The originating host of the current message should always be considered online since they just sent us the message (their activity was already updated before gap detection runs).

When gap detection is skipped for an offline host, a log event should be emitted so the behavior is observable.

## Files to Look At

- `lib/features/sync/sequence/sync_sequence_log_service.dart` — the `recordReceivedEntry` method performs gap detection for each host in the incoming vector clock
- `lib/features/sync/README.md` — documents the gap detection behavior and logging; update it to reflect the new behavior

## Hints

- The `SyncDatabase` already has a `getHostLastSeen` method via the `HostActivity` table
- The originating host's activity is updated at the top of `recordReceivedEntry` before the VC loop
- After fixing the code, update the sync README documentation to reflect the change. The project's AGENTS.md requires that feature READMEs stay in sync with the codebase
