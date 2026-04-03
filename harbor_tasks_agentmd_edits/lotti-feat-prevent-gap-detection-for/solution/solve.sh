#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'skipGapDetection' lib/features/sync/sequence/sync_sequence_log_service.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/lib/features/sync/README.md b/lib/features/sync/README.md
index 4cce704119..e5037b41d3 100644
--- a/lib/features/sync/README.md
+++ b/lib/features/sync/README.md
@@ -152,6 +152,14 @@ complete reconstruction of sync state.
 - Any counter jumps > 1 trigger gap entries marked as `missing`
 - When an entry arrives, ALL (hostId, counter) pairs in its VC are updated to
   received/backfilled status (not just the originator's counter)
+- **Online Host Guard:** Gap detection is only performed for hosts that have been
+  seen "online" (i.e., have sent us a message directly via the `HostActivity`
+  table). This prevents false positive gaps for hosts we've never communicated
+  with — we may see their counters in vector clocks from other hosts, but we
+  can't know if entries are actually missing without having established
+  communication with them. The originating host is always considered online
+  since they just sent us the current message. Sequence entries are still
+  recorded for offline hosts to enable backfill responses later.

 **Ghost Entry Resolution:**
 Different payload types can share the same sequence counter. When one type
@@ -216,6 +224,7 @@ If the BackfillResponse arrives before the sync message (race condition):
 **Logging:** Key domains include `SYNC_SEQUENCE` (gap detection, status changes)
 and `SYNC_BACKFILL` (request/response handling). Look for:
 - `gapDetected hostId=... counter=... (last seen: ..., observed: ...)`
+- `skipGapDetection hostId=... counter=... - host never seen online`
 - `handleBackfillRequest: N entries from=...`
 - `handleBackfillResponse: stored hint hostId=... counter=... entryId=...`
 - `verifyAndMarkBackfilled: confirmed hostId=... counter=... entryId=...`
diff --git a/lib/features/sync/sequence/sync_sequence_log_service.dart b/lib/features/sync/sequence/sync_sequence_log_service.dart
index fc97797cc3..b54fd6e880 100644
--- a/lib/features/sync/sequence/sync_sequence_log_service.dart
+++ b/lib/features/sync/sequence/sync_sequence_log_service.dart
@@ -108,9 +108,32 @@ class SyncSequenceLogService {
       // Skip our own host
       if (hostId == myHost) continue;

+      // Only detect gaps for hosts that have been seen "online" (i.e., have
+      // sent us a message directly). This prevents false positive gaps for
+      // hosts we've never communicated with - we may see their counters in
+      // vector clocks from other hosts, but we can't know if entries are
+      // actually missing without having established communication with them.
+      // The originating host is always considered online (we just updated
+      // their activity above).
+      //
+      // Note: We still record the sequence entry for offline hosts (below),
+      // just skip gap detection. This allows us to respond to backfill
+      // requests later if the host comes online.
+      final hostLastOnline = await _syncDatabase.getHostLastSeen(hostId);
+      final shouldDetectGaps =
+          hostLastOnline != null || hostId == originatingHostId;
+
+      if (!shouldDetectGaps) {
+        _loggingService.captureEvent(
+          'skipGapDetection hostId=$hostId counter=$counter - host never seen online',
+          domain: 'SYNC_SEQUENCE',
+          subDomain: 'skipGap',
+        );
+      }
+
       final lastSeen = await _syncDatabase.getLastCounterForHost(hostId);

-      if (lastSeen != null && counter > lastSeen + 1) {
+      if (shouldDetectGaps && lastSeen != null && counter > lastSeen + 1) {
         // Gap detected! Mark missing counters for this host
         final gapSize = counter - lastSeen - 1;


PATCH

echo "Patch applied successfully."
