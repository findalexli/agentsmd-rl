# Flink Source Split Enumerator Race Condition

## Problem

The `LazyFlinkSourceSplitEnumerator` in the Flink runner has a race condition that causes flaky test failures in the PostCommit Java Jpms Flink Java11 CI job (failing over 50% of the time).

The `handleSplitRequest()` method can be called by Flink before the asynchronous `initializeSplits()` has finished populating the `pendingSplits` list. When this happens, `handleSplitRequest` sees `pendingSplits` as empty and incorrectly calls `context.signalNoMoreSplits()`, telling Flink there is no more work — even though splits are still being computed in the background.

Additionally, the `splitsInitialized` field is not thread-safe, so changes made by the initialization thread may not be visible to the thread calling `handleSplitRequest`.

## Expected Behavior

`handleSplitRequest()` should wait for `initializeSplits()` to complete before checking `pendingSplits`. The waiting mechanism must handle the case where initialization fails (to avoid blocking forever). The `splitsInitialized` flag must be visible across threads.

## Files to Look At

- `runners/flink/src/main/java/org/apache/beam/runners/flink/translation/wrappers/streaming/io/source/LazyFlinkSourceSplitEnumerator.java` — The split enumerator that lazily initializes and assigns source splits to Flink subtasks. The `initializeSplits()` method runs asynchronously via `context.callAsync()`, but `handleSplitRequest()` has no synchronization to wait for it.
