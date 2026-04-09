#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'task_cache.get(&task_type).map(|r| \*r)' turbopack/crates/turbo-tasks-backend/src/backend/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
index 3b5a509d41591a..98715f6ffabc27 100644
--- a/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
+++ b/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs
@@ -1532,8 +1532,9 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
         // Create a single ExecuteContext for both lookup and connect_child
         let mut ctx = self.execute_context(turbo_tasks);
         // First check if the task exists in the cache which only uses a read lock
-        if let Some(task_id) = self.task_cache.get(&task_type) {
-            let task_id = *task_id;
+        // .map(|r| *r) copies the TaskId and drops the DashMap Ref (releasing the read lock)
+        // before ConnectChildOperation::run, which may re-enter task_cache with a write lock.
+        if let Some(task_id) = self.task_cache.get(&task_type).map(|r| *r) {
             self.track_cache_hit(&task_type);
             operation::ConnectChildOperation::run(
                 parent_task,
@@ -1614,9 +1615,10 @@ impl<B: BackingStorage> TurboTasksBackendInner<B> {
             );
         }
         let mut ctx = self.execute_context(turbo_tasks);
-        // First check if the task exists in the cache which only uses a read lock
-        if let Some(task_id) = self.task_cache.get(&task_type) {
-            let task_id = *task_id;
+        // First check if the task exists in the cache which only uses a read lock.
+        // .map(|r| *r) copies the TaskId and drops the DashMap Ref (releasing the read lock)
+        // before ConnectChildOperation::run, which may re-enter task_cache with a write lock.
+        if let Some(task_id) = self.task_cache.get(&task_type).map(|r| *r) {
             self.track_cache_hit(&task_type);
             operation::ConnectChildOperation::run(
                 parent_task,

PATCH

echo "Patch applied successfully."
