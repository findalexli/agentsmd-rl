#!/bin/bash
set -e

cd /workspace/turbo_repo

# Apply the fix patch using git apply
git apply -- <<'PATCH'
diff --git a/crates/turborepo-lib/src/run/mod.rs b/crates/turborepo-lib/src/run/mod.rs
index 501b74e9e2ffd..e2deab6c74266 100644
--- a/crates/turborepo-lib/src/run/mod.rs
+++ b/crates/turborepo-lib/src/run/mod.rs
@@ -829,7 +829,13 @@ impl Run {
         // When a proxy is present, the signal handler only stops processes on OS
         // signal. For normal completion without user interruption, we need an
         // explicit stop here.
-        self.processes.stop().await;
+        //
+        // In watch mode, persistent tasks run as fire-and-forget background
+        // processes that outlive the visit() call. The watch coordinator
+        // manages their lifecycle via RunStopper, so we must not kill them here.
+        if !is_watch {
+            self.processes.stop().await;
+        }

         visitor
             .finish(
diff --git a/crates/turborepo-lib/src/task_graph/visitor/mod.rs b/crates/turborepo-lib/src/task_graph/visitor/mod.rs
index a02999e772789..724a85e788022 100644
--- a/crates/turborepo-lib/src/task_graph/visitor/mod.rs
+++ b/crates/turborepo-lib/src/task_graph/visitor/mod.rs
@@ -560,10 +560,14 @@ impl<'a> Visitor<'a> {
         // Write out the traced-config.json file if we have one
         self.task_access.save().await;

-        let errors = Arc::into_inner(errors)
-            .expect("only one strong reference to errors should remain")
-            .into_inner()
-            .expect("mutex poisoned");
+        let errors = match Arc::try_unwrap(errors) {
+            Ok(mutex) => mutex.into_inner().expect("mutex poisoned"),
+            Err(arc) => {
+                // In watch mode, fire-and-forget persistent tasks may still
+                // hold references. Drain the collected errors from the mutex.
+                std::mem::take(&mut *arc.lock().expect("mutex poisoned"))
+            }
+        };

         Ok(errors)
     }
PATCH

# Verify the distinctive line is present
grep -q "if !is_watch" crates/turborepo-lib/src/run/mod.rs

echo "Fix applied successfully"
