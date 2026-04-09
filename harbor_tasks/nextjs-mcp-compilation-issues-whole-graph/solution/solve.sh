#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'whole_app_module_graphs_without_dropping_issues' crates/next-api/src/project.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/next-api/src/project.rs b/crates/next-api/src/project.rs
index 5eda1ba0386674..7238a7346b0543 100644
--- a/crates/next-api/src/project.rs
+++ b/crates/next-api/src/project.rs
@@ -1505,6 +1505,22 @@ impl Project {
         })
     }

+    /// Computes the whole app module graph without dropping issues.
+    ///
+    /// Use this instead of [`whole_app_module_graphs`] when you need to collect issues from the
+    /// computation (e.g. for the `get_compilation_issues` MCP tool).
+    #[turbo_tasks::function]
+    pub async fn whole_app_module_graphs_without_dropping_issues(
+        self: ResolvedVc<Self>,
+    ) -> Result<Vc<BaseAndFullModuleGraph>> {
+        let module_graphs_op = whole_app_module_graph_operation(self);
+        let module_graphs_vc = module_graphs_op.connect();
+        scale_down_node_pool(self).await?;
+        Ok(module_graphs_vc)
+    }
+
+    /// Computes the whole app module graph, dropping issues in development mode so that
+    /// individual routes don't each report every issue from the shared graph.
     #[turbo_tasks::function]
     pub async fn whole_app_module_graphs(
         self: ResolvedVc<Self>,
@@ -1513,23 +1529,11 @@ impl Project {
         let module_graphs_vc = if self.next_mode().await?.is_production() {
             module_graphs_op.connect()
         } else {
-            // In development mode, we need to to take and drop the issues, otherwise every
-            // route will report all issues.
             let vc = module_graphs_op.resolve().strongly_consistent().await?;
             module_graphs_op.drop_issues();
             *vc
         };
-
-        // At this point all modules have been computed and we can get rid of the node.js
-        // process pools
-        let execution_context = self.execution_context().await?;
-        let node_backend = execution_context.node_backend.into_trait_ref().await?;
-        if *self.is_watch_enabled().await? {
-            node_backend.scale_down()?;
-        } else {
-            node_backend.scale_zero()?;
-        }
-
+        scale_down_node_pool(self).await?;
         Ok(module_graphs_vc)
     }

@@ -2455,6 +2459,18 @@ impl Project {
     }
 }

+/// Scales down or shuts down the Node.js process pool after module graph computation.
+async fn scale_down_node_pool(project: ResolvedVc<Project>) -> Result<()> {
+    let execution_context = project.execution_context().await?;
+    let node_backend = execution_context.node_backend.into_trait_ref().await?;
+    if *project.is_watch_enabled().await? {
+        node_backend.scale_down()?;
+    } else {
+        node_backend.scale_zero()?;
+    }
+    Ok(())
+}
+
 // This is a performance optimization. This function is a root aggregation function that
 // aggregates over the whole subgraph.
 #[turbo_tasks::function(operation, root)]
diff --git a/crates/next-napi-bindings/src/next_api/project.rs b/crates/next-napi-bindings/src/next_api/project.rs
index e41027d13ce143..83810d2adb4762 100644
--- a/crates/next-napi-bindings/src/next_api/project.rs
+++ b/crates/next-napi-bindings/src/next_api/project.rs
@@ -2521,18 +2521,14 @@ async fn get_all_compilation_issues_inner_operation(
     container: ResolvedVc<ProjectContainer>,
 ) -> Result<Vc<()>> {
     let project = container.project();
-    // Build the module graph for every endpoint without chunking, code gen, or disk emission.
-    // We iterate endpoints rather than calling project.whole_app_module_graphs() because the
-    // latter calls drop_issues() in development mode (to avoid duplicate per-route HMR noise).
-    // Per-endpoint module_graphs() calls are not subject to that suppression, so issues like
-    // missing modules and transform errors are properly collected as collectables here.
-    let endpoint_groups = project.get_all_endpoint_groups(false).await?;
-    endpoint_groups
-        .iter()
-        .map(|(_, endpoint_group)| async move {
-            endpoint_group.module_graphs().as_side_effect().await
-        })
-        .try_join()
+    // Build the whole app module graph without chunking, code gen, or disk emission.
+    // We use whole_app_module_graphs_without_dropping_issues() instead of
+    // whole_app_module_graphs() because the latter drops issues in development mode
+    // (to avoid duplicate per-route HMR noise). The non-dropping variant ensures issues
+    // like missing modules and transform errors are properly collected as collectables here.
+    project
+        .whole_app_module_graphs_without_dropping_issues()
+        .as_side_effect()
         .await?;
     Ok(Vc::cell(()))
 }

PATCH

echo "Patch applied successfully."
