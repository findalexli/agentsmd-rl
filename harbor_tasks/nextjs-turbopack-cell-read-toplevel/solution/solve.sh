#!/usr/bin/env bash
set -euo pipefail

MANAGER="turbopack/crates/turbo-tasks/src/manager.rs"
TEST_FILE="turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs"

# Check if already applied (the debug_assert lines should be gone from try_read_task_cell)
if ! grep -q 'debug_assert_not_in_top_level_task("read_task_cell")' "$MANAGER"; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs b/turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs
index 5ca0530590f187..81274186179611 100644
--- a/turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs
+++ b/turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs
@@ -36,13 +36,13 @@ async fn test_eventual_read_in_top_level_task_fails() {
 }

 #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
-#[should_panic]
-async fn test_cell_read_in_top_level_task_fails() {
+async fn test_cell_read_in_top_level_task_succeeds() {
     run_once(&REGISTRATION, || async {
         let cell = returns_value_operation()
             .resolve_strongly_consistent()
             .await?;
-        let _ = cell.await?;
+        let value = cell.await?;
+        assert_eq!(value.value, 42);
         Ok(())
     })
     .await
diff --git a/turbopack/crates/turbo-tasks/src/manager.rs b/turbopack/crates/turbo-tasks/src/manager.rs
index cc2fd7070dcc7c..76fea4ae929577 100644
--- a/turbopack/crates/turbo-tasks/src/manager.rs
+++ b/turbopack/crates/turbo-tasks/src/manager.rs
@@ -1473,9 +1473,6 @@ impl<B: Backend + 'static> TurboTasksApi for TurboTasks<B> {
         options: ReadCellOptions,
     ) -> Result<Result<TypedCellContent, EventListener>> {
         let reader = current_task_if_available("reading Vcs");
-        if cfg!(debug_assertions) && reader != Some(task) {
-            debug_assert_not_in_top_level_task("read_task_cell");
-        }
         self.backend
             .try_read_task_cell(task, index, reader, options, self)
     }

PATCH

echo "Patch applied successfully."
