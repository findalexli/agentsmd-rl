#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q '_catchUpInFlight' lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/docs/sync/sync_summary.md b/docs/sync/sync_summary.md
index 0bcf67f1b..1e55590ef 100644
--- a/docs/sync/sync_summary.md
+++ b/docs/sync/sync_summary.md
@@ -16,6 +16,16 @@ This note captures the current pipeline behavior, recent fixes, logs to look for
 ## What We Fixed/Added

 Recent changes (Oct 2025)
+- Client stream → signal-driven catch-up (2025-10-28):
+  - Every client stream signal triggers `forceRescan(includeCatchUp=true)` with an in-flight guard.
+  - Timeline callbacks continue to schedule debounced live scans and fall back to `forceRescan()`
+    on scheduling errors.
+  - Marker advancement only from ordered slices (catch-up/live scans), never directly from stream
+    events.
+- Catch-up backlog completion (2025-10-28):
+  - Catch-up continues escalating snapshot size until it is not full (or cap reached), ensuring the
+    full backlog after the marker is included.
+  - Pre-context by count and timestamp remains unchanged.
 - Removed rewind from both implementation and docs:
   Catch‑up always backfills until the marker is present and processes strictly after.
   Code: `pipeline_v2/catch_up_strategy.dart`, consumer call‑site.
diff --git a/lib/features/sync/README.md b/lib/features/sync/README.md
index 143c0da4f..5f44c1936 100644
--- a/lib/features/sync/README.md
+++ b/lib/features/sync/README.md
@@ -35,7 +35,7 @@ that keeps the pipeline testable and observable.
 | **MatrixSyncGateway** (`gateway/matrix_sdk_gateway.dart`) | Abstraction over the Matrix SDK for login, room lookup, invites, timelines, and logout. |
 | **MatrixMessageSender** (`matrix/matrix_message_sender.dart`) | Encodes `SyncMessage`s, uploads attachments, registers the Matrix event IDs it emits, increments send counters, and notifies `MatrixService`. |
 | **SentEventRegistry** (`matrix/sent_event_registry.dart`) | In-memory TTL cache of event IDs produced by this device so timeline ingestion can drop echo events without re-applying them. |
-| **MatrixStreamConsumer** (`matrix/pipeline_v2/matrix_stream_consumer.dart`) | Stream-first consumer: attach-time catch-up (SDK pagination/backfill with graceful fallback), micro-batched streaming, attachment prefetch, monotonic marker advancement, retries with TTL + size cap, circuit breaker, and metrics. |
+| **MatrixStreamConsumer** (`matrix/pipeline/matrix_stream_consumer.dart`) | Stream-first consumer: attach-time catch-up (SDK pagination/backfill with graceful fallback), micro-batched streaming, attachment prefetch, monotonic marker advancement, retries with TTL + size cap, circuit breaker, and metrics. |
 | **SyncRoomManager** (`matrix/sync_room_manager.dart`) | Persists the active room, filters invites, validates IDs, hydrates cached rooms, and orchestrates safe join/leave operations. |
 | **SyncEventProcessor** (`matrix/sync_event_processor.dart`) | Decodes `SyncMessage`s, mutates `JournalDb`, emits notifications (e.g. `UpdateNotifications`), and surfaces precise `applied/skipReason` diagnostics so the pipeline can distinguish conflicts, older/equal payloads, and genuine missing-base scenarios. |
 | **SyncReadMarkerService** (`matrix/read_marker_service.dart`) | Writes Matrix read markers after successful timeline processing and persists the last processed event ID. |
@@ -57,6 +57,14 @@ that keeps the pipeline testable and observable.
 - `MatrixStreamConsumer` attaches directly to the sync room and performs
   attach-time catch-up via SDK pagination/backfill with a graceful fallback for
   large gaps.
+- Signal-driven ingestion (2025-10-28):
+  - Client stream events are treated as signals that always trigger a
+    `forceRescan()` with catch-up. An in-flight guard prevents overlapping
+    catch-ups.
+  - Live timeline callbacks continue to schedule debounced live scans; on
+    scheduling failure, the consumer falls back to `forceRescan()`.
+  - Marker advancement happens only from ordered slices returned by
+    catch-up/live scans, never directly from the client stream.
 - Live streaming is micro-batched and ordered chronologically with
   de-duplication by event ID; attachment prefetch happens before invoking
   `SyncEventProcessor` so text payloads arrive with their media ready.
@@ -103,9 +111,9 @@ The stream-first consumer replaces the legacy multi-pass drain:
   when at least one new file was written.

 Key helpers:
-- `pipeline_v2/catch_up_strategy.dart`: no-rewind catch-up via SDK seam and
+- `matrix/pipeline/catch_up_strategy.dart`: no-rewind catch-up via SDK seam and
   snapshot-limit escalation fallback.
-- `pipeline_v2/attachment_index.dart`: in-memory relativePath→event map used by
+- `matrix/pipeline/attachment_index.dart`: in-memory relativePath→event map used by
   the apply phase.
 - `matrix/sync_event_processor.dart` smart loader: vector-clock aware JSON
   fetching that uses `AttachmentIndex` to fetch newer JSON for same-path
@@ -133,9 +141,9 @@ Key helpers:
 - **Unit/Widget:** Coverage includes the client runner queue, activity gating,
   timeline error recovery, verification modals (provider overrides),
   dependency-injection helpers, and the modern sync pipeline:
-  - `pipeline_v2/matrix_stream_consumer_test.dart` covers SDK pagination seams,
+  - `test/features/sync/matrix/pipeline/matrix_stream_consumer_test.dart` covers SDK pagination seams,
     streaming/flush batching, metrics accuracy, and retry/circuit-breaker logic.
-  - `pipeline_v2/*` helper suites validate catch-up, descriptor hydration, and
+  - `test/features/sync/matrix/pipeline/*` helper suites validate catch-up, descriptor hydration, and
     attachment ingestion.
   - Lifecycle tests exercise activation, deactivation, and login/logout races with the pipeline.
   - `matrix_service_pipeline_test.dart` covers metrics exposure, retry/rescan
diff --git a/lib/features/sync/matrix/pipeline/catch_up_strategy.dart b/lib/features/sync/matrix/pipeline/catch_up_strategy.dart
index 3a667073f..3b9efbc11 100644
--- a/lib/features/sync/matrix/pipeline/catch_up_strategy.dart
+++ b/lib/features/sync/matrix/pipeline/catch_up_strategy.dart
@@ -63,7 +63,11 @@ class CatchUpStrategy {
             (events.isEmpty ||
                 TimelineEventOrdering.timestamp(events.first) >
                     preContextSinceTs);
-        return needCount || needSinceTs;
+        if (needCount || needSinceTs) return true;
+        // NEW: If the snapshot is full, there may be more events after the
+        // marker that are not yet included. Keep escalating until the snapshot
+        // is not full (boundary reached) or we hit the cap.
+        return events.length >= limit;
       }

       while (needsMore()) {
diff --git a/lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart b/lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart
index 5aebf79cc..adff33eb1 100644
--- a/lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart
+++ b/lib/features/sync/matrix/pipeline/matrix_stream_consumer.dart
@@ -194,11 +194,11 @@ class MatrixStreamConsumer implements SyncPipeline {
   // Client stream does not buffer events; scans are scheduled via timers.

   Timer? _liveScanTimer;
-  Timer? _initialCatchUpRetryTimer;
-  DateTime? _initialCatchUpStartAt;
-  int _initialCatchUpAttempts = 0;
-  bool _initialCatchUpCompleted = false;
-  bool _firstStreamEventCatchUpTriggered = false;
+  // Guard to prevent overlapping catch-ups triggered by signals.
+  bool _catchUpInFlight = false;
+  // Explicitly request catch-up when nudging via signals, keeping semantics
+  // independent of default parameter values.
+  final bool _alwaysIncludeCatchUp = true;
   final Duration _markerDebounce;
   // Catch-up window is handled by strategy with sensible defaults.

@@ -492,54 +492,38 @@ class MatrixStreamConsumer implements SyncPipeline {
         subDomain: 'start',
       );
     }
-    // Attempt catch‑up only when we have an active room; otherwise we'll rely
-    // on the later scheduled retry once the room is ready.
+    // Attempt catch‑up only when we have an active room; otherwise signals
+    // (client stream/connectivity) will trigger a catch‑up shortly.
     if (_roomManager.currentRoom != null) {
       await _attachCatchUp();
     }
-    // Ensure we eventually run initial catch‑up even if the room was not yet
-    // ready — schedule a retry loop that cancels itself once catch‑up runs.
-    if (_roomManager.currentRoom == null) {
-      _scheduleInitialCatchUpRetry();
-    }
     await _sub?.cancel();
-    // Client-level session stream → signal-only ingestion.
-    // Filter by current room; the very first event also triggers a catch-up
-    // to ensure we ingest backlog before scanning the tail.
+    // Client-level session stream → signal-driven catch-up.
+    // Filter by current room; every signal triggers a catch-up to avoid
+    // skipping backlog created while offline.
     _sub = _sessionManager.timelineEvents.listen((event) {
       final roomId = _roomManager.currentRoomId;
       if (roomId == null || event.roomId != roomId) return;
-      if (!_initialCatchUpCompleted && !_firstStreamEventCatchUpTriggered) {
-        _firstStreamEventCatchUpTriggered = true;
-        _loggingService.captureEvent(
-          'catchup.trigger.onFirstStreamEvent',
-          domain: syncLoggingDomain,
-          subDomain: 'catchup',
-        );
-        // Attempt a catch-up + live scan in the background.
-        unawaited(forceRescan());
-      }
-      // Record client-stream signal and schedule a scan with safeguards.
-      // If scheduling the scan throws (rare), fall back to a forceRescan
-      // which runs catch-up + a live scan to recover quickly.
       if (_collectMetrics) _metrics.incSignalClientStream();
       _loggingService.captureEvent(
         'signal.clientStream',
         domain: syncLoggingDomain,
         subDomain: 'signal',
       );
-      try {
-        _scheduleLiveScan();
-      } catch (e, st) {
-        _loggingService.captureException(
-          e,
+      if (_catchUpInFlight) {
+        _loggingService.captureEvent(
+          'signal.catchup.skipped inFlight=true',
           domain: syncLoggingDomain,
-          subDomain: 'signal.schedule',
-          stackTrace: st,
+          subDomain: 'signal',
         );
-        // Fallback: run a catch-up + live scan to recover
-        unawaited(forceRescan());
+        return;
       }
+      _catchUpInFlight = true;
+      unawaited(
+        forceRescan(includeCatchUp: _alwaysIncludeCatchUp).whenComplete(() {
+          _catchUpInFlight = false;
+        }),
+      );
     });

     // Also attach live timeline listeners to proactively scan in case the
@@ -565,7 +549,7 @@ class MatrixStreamConsumer implements SyncPipeline {
               subDomain: 'signal.schedule',
               stackTrace: st,
             );
-            unawaited(forceRescan());
+            unawaited(forceRescan(includeCatchUp: _alwaysIncludeCatchUp));
           }
         }

@@ -625,7 +609,6 @@ class MatrixStreamConsumer implements SyncPipeline {
     await _sub?.cancel();
     _sub = null;
     _liveScanTimer?.cancel();
-    _initialCatchUpRetryTimer?.cancel();
     _readMarkerManager.dispose();
     _descriptorCatchUp?.dispose();
     // Cancel live timeline subscriptions to avoid leaks.
@@ -684,10 +667,7 @@ class MatrixStreamConsumer implements SyncPipeline {
         if (_collectMetrics) _metrics.incCatchupBatches();
         await _processOrdered(slice);
       }
-      // Initial catch-up attempt considered completed (even if empty). Cancel any pending retries.
-      _initialCatchUpRetryTimer?.cancel();
-      _initialCatchUpRetryTimer = null;
-      _initialCatchUpCompleted = true;
+      // Catch-up completed.
     } catch (e, st) {
       _loggingService.captureException(
         e,
@@ -698,60 +678,6 @@ class MatrixStreamConsumer implements SyncPipeline {
     }
   }

-  void _scheduleInitialCatchUpRetry() {
-    _initialCatchUpRetryTimer?.cancel();
-    final start = _initialCatchUpStartAt ?? clock.now();
-    _initialCatchUpStartAt = start;
-    final elapsed = clock.now().difference(start);
-    // Give up after ~15 minutes of trying; logs will indicate timeout.
-    const maxWait = Duration(minutes: 15);
-    if (elapsed >= maxWait) {
-      _loggingService.captureEvent(
-        'catchup.timeout after ${elapsed.inSeconds}s',
-        domain: syncLoggingDomain,
-        subDomain: 'catchup',
-      );
-      return;
-    }
-    // Exponential backoff starting at 200ms, capping at 10s, no jitter.
-    final delay = tu.computeExponentialBackoff(
-      _initialCatchUpAttempts,
-    );
-    _initialCatchUpAttempts++;
-    _initialCatchUpRetryTimer = Timer(delay, () {
-      if (_initialCatchUpCompleted) return;
-      if (_roomManager.currentRoom != null) {
-        // Attempt catch-up and ensure we continue retrying until it marks
-        // completion. Capture and log errors before rescheduling.
-        _attachCatchUp().then((_) {
-          if (!_initialCatchUpCompleted) {
-            _loggingService.captureEvent(
-              'catchup.retry.reschedule (not completed)',
-              domain: syncLoggingDomain,
-              subDomain: 'catchup',
-            );
-            _scheduleInitialCatchUpRetry();
-          }
-        }).catchError((Object error, StackTrace st) {
-          _loggingService.captureException(
-            error,
-            domain: syncLoggingDomain,
-            subDomain: 'catchup.retry',
-            stackTrace: st,
-          );
-          _scheduleInitialCatchUpRetry();
-        });
-      } else {
-        _loggingService.captureEvent(
-          'waiting for room for initial catch-up (attempt=$_initialCatchUpAttempts, delay=${delay.inMilliseconds}ms)',
-          domain: syncLoggingDomain,
-          subDomain: 'catchup',
-        );
-        _scheduleInitialCatchUpRetry();
-      }
-    });
-  }
-
   Timeline? _liveTimeline;

   void _scheduleLiveScan() {
@@ -894,7 +820,8 @@ class MatrixStreamConsumer implements SyncPipeline {
       // Skip duplicate attachment work if we've already seen this eventId.
       // Keep processing for sync payload events to ensure apply/retry semantics.
       final dup = _isDuplicateAndRecordSeen(eventId);
-      final suppressed = _sentEventRegistry.consume(eventId);
+      final isSelfOrigin = e.senderId == _client.userID;
+      final suppressed = _sentEventRegistry.consume(eventId) || isSelfOrigin;
       if (suppressed) {
         suppressedIds.add(eventId);
         _metrics.incSelfEventsSuppressed();

PATCH

echo "Patch applied successfully."
