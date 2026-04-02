#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if the background_span is already in mod.rs, skip
if grep -q 'info_span!(parent: None, "background snapshot")' \
   turbopack/crates/turbo-tasks-backend/src/backend/mod.rs 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbo-persistence/src/db.rs b/turbopack/crates/turbo-persistence/src/db.rs
index 5967363809af5d..f86992923ea2ab 100644
--- a/turbopack/crates/turbo-persistence/src/db.rs
+++ b/turbopack/crates/turbo-persistence/src/db.rs
@@ -573,7 +573,7 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>

         new_meta_files.sort_unstable_by_key(|(seq, _)| *seq);

-        let sync_span = tracing::info_span!("sync new files").entered();
+        let sync_span = tracing::trace_span!("sync new files").entered();
         let mut new_meta_files = self
             .parallel_scheduler
             .parallel_map_collect_owned::<_, _, Result<Vec<_>>>(new_meta_files, |(seq, file)| {
@@ -813,7 +813,6 @@ impl<S: ParallelScheduler, const FAMILIES: usize> TurboPersistence<S, FAMILIES>
         if self.read_only {
             bail!("Compaction is not allowed on a read only database");
         }
-        let _span = tracing::info_span!("compact database").entered();
         if self
             .active_write_operation
             .compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire)
diff --git a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
index f373555d937ecd..368f887465ac2e 100644
--- a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
+++ b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
@@ -2769,12 +2769,22 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
                         }

                         let this = self.clone();
-                        let snapshot = this.snapshot_and_persist(None, reason, turbo_tasks);
+                        // Create a root span shared by both the snapshot/persist
+                        // work and the subsequent compaction so they appear
+                        // grouped together in trace viewers.
+                        let background_span =
+                            tracing::info_span!(parent: None, "background snapshot");
+                        let snapshot =
+                            this.snapshot_and_persist(background_span.id(), reason, turbo_tasks);
                         if let Some((snapshot_start, new_data)) = snapshot {
                             last_snapshot = snapshot_start;

                             // Compact while idle (up to limit), regardless of
                             // whether the snapshot had new data.
+                            // `background_span` is not entered here because
+                            // `EnteredSpan` is `!Send` and would prevent the
+                            // future from being sent across threads when it
+                            // suspends at the `select!` await below.
                             const MAX_IDLE_COMPACTION_PASSES: usize = 10;
                             for _ in 0..MAX_IDLE_COMPACTION_PASSES {
                                 let idle_ended = tokio::select! {
@@ -2788,6 +2798,14 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
                                 if idle_ended {
                                     break;
                                 }
+                                // Enter the span only around the synchronous
+                                // compact() call so we never hold an
+                                // `EnteredSpan` across an await point.
+                                let _compact_span = tracing::info_span!(
+                                    parent: background_span.id(),
+                                    "compact database"
+                                )
+                                .entered();
                                 match self.backing_storage.compact() {
                                     Ok(true) => {}
                                     Ok(false) => break,

PATCH

echo "Fix applied successfully."
