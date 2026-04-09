#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'fn update_dirty_state' turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
index 98715f6ffabc2..9dde575d7221a 100644
--- a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
+++ b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
@@ -55,10 +55,10 @@ use crate::{
     backend::{
         operation::{
             AggregationUpdateJob, AggregationUpdateQueue, ChildExecuteContext,
-            CleanupOldEdgesOperation, ComputeDirtyAndCleanUpdate, ConnectChildOperation,
-            ExecuteContext, ExecuteContextImpl, LeafDistanceUpdateQueue, Operation, OutdatedEdge,
-            TaskGuard, TaskType, connect_children, get_aggregation_number, get_uppers,
-            is_root_node, make_task_dirty_internal, prepare_new_children,
+            CleanupOldEdgesOperation, ConnectChildOperation, ExecuteContext, ExecuteContextImpl,
+            LeafDistanceUpdateQueue, Operation, OutdatedEdge, TaskGuard, TaskType,
+            connect_children, get_aggregation_number, get_uppers, is_root_node,
+            make_task_dirty_internal, prepare_new_children,
         },
         storage::Storage,
         storage_schema::{TaskStorage, TaskStorageAccessors},
@@ -955,7 +955,13 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
         }

         // Cell should exist, but data was dropped or is not serializable. We need to recompute the
-        // task the get the cell content.
+        // task to get the cell content.
+
+        // Bail early if the task was cancelled — no point in registering a listener
+        // on a task that won't execute again.
+        if is_cancelled {
+            bail!("{} was canceled", task.get_task_description());
+        }

         // Listen to the cell and potentially schedule the task
         let (listener, new_listener) = self.listen_to_cell(&mut task, task_id, &reader_task, cell);
@@ -971,11 +977,6 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
         )
         .entered();

-        // Schedule the task, if not already scheduled
-        if is_cancelled {
-            bail!("{} was canceled", task.get_task_description());
-        }
-
         let _ = task.add_scheduled(
             TaskExecutionReason::CellNotAvailable,
             EventDescription::new(|| task.get_task_desc_fn()),
@@ -1857,7 +1858,7 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
         turbo_tasks: &dyn TurboTasksBackendApi<TurboTasksBackend<B>>,
     ) {
         let mut ctx = self.execute_context(turbo_tasks);
-        let mut task = ctx.task(task_id, TaskDataCategory::Data);
+        let mut task = ctx.task(task_id, TaskDataCategory::All);
         if let Some(in_progress) = task.take_in_progress() {
             match in_progress {
                 InProgressState::Scheduled {
@@ -1870,8 +1871,35 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
                 InProgressState::Canceled => {}
             }
         }
+        // Notify any readers waiting on in-progress cells so their listeners
+        // resolve and foreground jobs can finish (prevents stop_and_wait hang).
+        let in_progress_cells = task.take_in_progress_cells();
+        if let Some(ref cells) = in_progress_cells {
+            for state in cells.values() {
+                state.event.notify(usize::MAX);
+            }
+        }
+
+        // Mark the cancelled task as session-dependent dirty so it will be re-executed
+        // in the next session. Without this, any reader that encounters the cancelled task
+        // records an error in its output. That error is persisted and would poison
+        // subsequent builds. By marking the task session-dependent dirty, the next build
+        // re-executes it, which invalidates dependents and corrects the stale errors.
+        let data_update = if self.should_track_dependencies() && !task_id.is_transient() {
+            task.update_dirty_state(Some(Dirtyness::SessionDependent))
+        } else {
+            None
+        };
+
         let old = task.set_in_progress(InProgressState::Canceled);
         debug_assert!(old.is_none(), "InProgress already exists");
+        drop(task);
+
+        if let Some(data_update) = data_update {
+            AggregationUpdateQueue::run(data_update, &mut ctx);
+        }
+
+        drop(in_progress_cells);
     }

     fn try_start_task_execution(
@@ -2188,23 +2216,33 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
         }

         // handle cell counters: update max index and remove cells that are no longer used
-        let old_counters: FxHashMap<_, _> = task
-            .iter_cell_type_max_index()
-            .map(|(&k, &v)| (k, v))
-            .collect();
-        let mut counters_to_remove = old_counters.clone();
-
-        for (&cell_type, &max_index) in cell_counters.iter() {
-            if let Some(old_max_index) = counters_to_remove.remove(&cell_type) {
-                if old_max_index != max_index {
+        // On error, skip this update: the task may have failed before creating all cells it
+        // normally creates, so cell_counters is incomplete. Clearing cell_type_max_index entries
+        // based on partial counters would cause "cell no longer exists" errors for tasks that
+        // still hold dependencies on those cells. The old cell data is preserved on error
+        // (see task_execution_completed_cleanup), so keeping cell_type_max_index consistent with
+        // that data is correct.
+        // NOTE: This must stay in sync with task_execution_completed_cleanup, which similarly
+        // skips cell data removal on error.
+        if result.is_ok() {
+            let old_counters: FxHashMap<_, _> = task
+                .iter_cell_type_max_index()
+                .map(|(&k, &v)| (k, v))
+                .collect();
+            let mut counters_to_remove = old_counters.clone();
+
+            for (&cell_type, &max_index) in cell_counters.iter() {
+                if let Some(old_max_index) = counters_to_remove.remove(&cell_type) {
+                    if old_max_index != max_index {
+                        task.insert_cell_type_max_index(cell_type, max_index);
+                    }
+                } else {
                     task.insert_cell_type_max_index(cell_type, max_index);
                 }
-            } else {
-                task.insert_cell_type_max_index(cell_type, max_index);
             }
-        }
-        for (cell_type, _) in counters_to_remove {
-            task.remove_cell_type_max_index(&cell_type);
+            for (cell_type, _) in counters_to_remove {
+                task.remove_cell_type_max_index(&cell_type);
+            }
         }

         let mut queue = AggregationUpdateQueue::new();
@@ -2605,83 +2643,16 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
             }
         }

-        // Grab the old dirty state
-        let old_dirtyness = task.get_dirty().cloned();
-        let (old_self_dirty, old_current_session_self_clean) = match old_dirtyness {
-            None => (false, false),
-            Some(Dirtyness::Dirty(_)) => (true, false),
-            Some(Dirtyness::SessionDependent) => {
-                let clean_in_current_session = task.current_session_clean();
-                (true, clean_in_current_session)
-            }
-        };
-
-        // Compute the new dirty state
+        // Compute and apply the new dirty state, propagating to aggregating ancestors
         let session_dependent = task.is_session_dependent();
-        let (new_dirtyness, new_self_dirty, new_current_session_self_clean) = if session_dependent {
-            (Some(Dirtyness::SessionDependent), true, true)
-        } else {
-            (None, false, false)
-        };
-
-        // Update the dirty state
-        let dirty_changed = old_dirtyness != new_dirtyness;
-        if dirty_changed {
-            if let Some(value) = new_dirtyness {
-                task.set_dirty(value);
-            } else if old_dirtyness.is_some() {
-                task.take_dirty();
-            }
-        }
-        if old_current_session_self_clean != new_current_session_self_clean {
-            if new_current_session_self_clean {
-                task.set_current_session_clean(true);
-            } else if old_current_session_self_clean {
-                task.set_current_session_clean(false);
-            }
-        }
-
-        // Propagate dirtyness changes
-        let data_update = if old_self_dirty != new_self_dirty
-            || old_current_session_self_clean != new_current_session_self_clean
-        {
-            let dirty_container_count = task
-                .get_aggregated_dirty_container_count()
-                .cloned()
-                .unwrap_or_default();
-            let current_session_clean_container_count = task
-                .get_aggregated_current_session_clean_container_count()
-                .copied()
-                .unwrap_or_default();
-            let result = ComputeDirtyAndCleanUpdate {
-                old_dirty_container_count: dirty_container_count,
-                new_dirty_container_count: dirty_container_count,
-                old_current_session_clean_container_count: current_session_clean_container_count,
-                new_current_session_clean_container_count: current_session_clean_container_count,
-                old_self_dirty,
-                new_self_dirty,
-                old_current_session_self_clean,
-                new_current_session_self_clean,
-            }
-            .compute();
-            if result.dirty_count_update - result.current_session_clean_update < 0 {
-                // The task is clean now
-                if let Some(activeness_state) = task.get_activeness_mut() {
-                    activeness_state.all_clean_event.notify(usize::MAX);
-                    activeness_state.unset_active_until_clean();
-                    if activeness_state.is_empty() {
-                        task.take_activeness();
-                    }
-                }
-            }
-            result
-                .aggregated_update(task_id)
-                .and_then(|aggregated_update| {
-                    AggregationUpdateJob::data_update(&mut task, aggregated_update)
-                })
+        let new_dirtyness = if session_dependent {
+            Some(Dirtyness::SessionDependent)
         } else {
             None
         };
+        #[cfg(feature = "verify_determinism")]
+        let dirty_changed = task.get_dirty().cloned() != new_dirtyness;
+        let data_update = task.update_dirty_state(new_dirtyness);

         #[cfg(feature = "verify_determinism")]
         let reschedule =
@@ -2724,6 +2695,8 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
         // An error is potentially caused by a eventual consistency, so we avoid updating cells
         // after an error as it is likely transient and we want to keep the dependent tasks
         // clean to avoid re-executions.
+        // NOTE: This must stay in sync with task_execution_completed_prepare, which similarly
+        // skips cell_type_max_index updates on error.
         if !is_error {
             // Remove no longer existing cells and
             // find all outdated data items (removed cells, outdated edges)
diff --git a/turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs b/turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs
index d17c948dbe9b2..47cb900b23705 100644
--- a/turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs
+++ b/turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs
@@ -18,6 +18,7 @@ use turbo_tasks::{
     TurboTasksCallApi, TypedSharedReference, backend::CachedTaskType,
 };

+use self::aggregation_update::ComputeDirtyAndCleanUpdate;
 use crate::{
     backend::{
         EventDescription, OperationGuard, TaskDataCategory, TurboTasksBackend,
@@ -757,6 +758,77 @@ pub trait TaskGuard: Debug + TaskStorageAccessors {
             Some(Dirtyness::SessionDependent) => (true, self.current_session_clean()),
         }
     }
+    /// Update the task's dirty state to `new_dirtyness`, applying the change to stored fields,
+    /// computing the aggregated propagation update, and firing the `all_clean_event` if the task
+    /// transitioned to clean.
+    ///
+    /// Returns an optional `AggregationUpdateJob` that the caller must run via
+    /// `AggregationUpdateQueue::run` to propagate the change to aggregating ancestors.
+    fn update_dirty_state(
+        &mut self,
+        new_dirtyness: Option<Dirtyness>,
+    ) -> Option<AggregationUpdateJob>
+    where
+        Self: Sized,
+    {
+        let task_id = self.id();
+        let old_dirtyness = self.get_dirty().cloned();
+        let (old_self_dirty, old_current_session_self_clean) = self.dirty_state();
+        let (new_self_dirty, new_current_session_self_clean) = match new_dirtyness {
+            None => (false, false),
+            Some(Dirtyness::Dirty(_)) => (true, false),
+            Some(Dirtyness::SessionDependent) => (true, true),
+        };
+        if old_dirtyness != new_dirtyness {
+            if let Some(value) = new_dirtyness {
+                self.set_dirty(value);
+            } else {
+                self.take_dirty();
+            }
+        }
+        if old_current_session_self_clean != new_current_session_self_clean {
+            self.set_current_session_clean(new_current_session_self_clean);
+        }
+        if old_self_dirty == new_self_dirty
+            && old_current_session_self_clean == new_current_session_self_clean
+        {
+            return None;
+        }
+        let dirty_container_count = self
+            .get_aggregated_dirty_container_count()
+            .cloned()
+            .unwrap_or_default();
+        let current_session_clean_container_count = self
+            .get_aggregated_current_session_clean_container_count()
+            .copied()
+            .unwrap_or_default();
+        let result = ComputeDirtyAndCleanUpdate {
+            old_dirty_container_count: dirty_container_count,
+            new_dirty_container_count: dirty_container_count,
+            old_current_session_clean_container_count: current_session_clean_container_count,
+            new_current_session_clean_container_count: current_session_clean_container_count,
+            old_self_dirty,
+            new_self_dirty,
+            old_current_session_self_clean,
+            new_current_session_self_clean,
+        }
+        .compute();
+        // Fire the all_clean_event if the task transitioned to clean
+        if result.dirty_count_update - result.current_session_clean_update < 0
+            && let Some(activeness_state) = self.get_activeness_mut()
+        {
+            activeness_state.all_clean_event.notify(usize::MAX);
+            activeness_state.unset_active_until_clean();
+            if activeness_state.is_empty() {
+                self.take_activeness();
+            }
+        }
+        result
+            .aggregated_update(task_id)
+            .and_then(|aggregated_update| {
+                AggregationUpdateJob::data_update(self, aggregated_update)
+            })
+    }
     fn dirty_containers(&self) -> impl Iterator<Item = TaskId> {
         self.dirty_containers_with_count()
             .map(|(task_id, _)| task_id)
@@ -1102,8 +1174,8 @@ impl_operation!(LeafDistanceUpdate leaf_distance_update::LeafDistanceUpdateQueue
 pub use self::invalidate::TaskDirtyCause;
 pub use self::{
     aggregation_update::{
-        AggregatedDataUpdate, AggregationUpdateJob, ComputeDirtyAndCleanUpdate,
-        get_aggregation_number, get_uppers, is_aggregating_node, is_root_node,
+        AggregatedDataUpdate, AggregationUpdateJob, get_aggregation_number, get_uppers,
+        is_aggregating_node, is_root_node,
     },
     cleanup_old_edges::OutdatedEdge,
     connect_children::connect_children,

PATCH

echo "Patch applied successfully."
