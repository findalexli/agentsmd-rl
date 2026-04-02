#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if module_count method already exists in mod.rs, patch is applied
if grep -q 'fn module_count' turbopack/crates/turbopack-core/src/module_graph/mod.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/next-api/src/app.rs b/crates/next-api/src/app.rs
index b2f918fbda732d..afe386b5ca34a0 100644
--- a/crates/next-api/src/app.rs
+++ b/crates/next-api/src/app.rs
@@ -35,7 +35,7 @@ use next_core::{
     segment_config::{NextSegmentConfig, ParseSegmentMode},
     util::{NextRuntime, app_function_name, module_styles_rule_condition, styles_rule_condition},
 };
-use tracing::Instrument;
+use tracing::{Instrument, field::Empty};
 use turbo_rcstr::{RcStr, rcstr};
 use turbo_tasks::{
     Completion, NonLocalValue, ResolvedVc, TryJoinIterExt, ValueToString, Vc, fxindexset,
@@ -884,6 +884,8 @@ impl AppProject {

             // Implements layout segment optimization to compute a graph "chain" for each layout
             // segment
+            let span = tracing::info_span!("module graph for endpoint", modules = Empty);
+            let span_clone = span.clone();
             async move {
                 let rsc_entry_chunk_group = ChunkGroupEntry::Entry(vec![rsc_entry]);

@@ -974,6 +976,14 @@ impl AppProject {
                 );
                 graphs.push(additional_module_graph);

+                if !span.is_disabled() {
+                    let mut module_count = 0u64;
+                    for g in &graphs {
+                        module_count += g.connect().module_count().untracked().owned().await?;
+                    }
+                    span.record("modules", module_count);
+                }
+
                 let remove_unused_imports = *self
                     .project
                     .next_config()
@@ -1004,7 +1014,7 @@ impl AppProject {
                 }
                 .cell())
             }
-            .instrument(tracing::info_span!("module graph for endpoint"))
+            .instrument(span_clone)
             .await
         } else {
             Ok(self.project.whole_app_module_graphs())
diff --git a/crates/next-api/src/project.rs b/crates/next-api/src/project.rs
index 815fb763eed301..3a97bb4e47c468 100644
--- a/crates/next-api/src/project.rs
+++ b/crates/next-api/src/project.rs
@@ -1482,32 +1482,28 @@ impl Project {
     pub async fn whole_app_module_graphs(
         self: ResolvedVc<Self>,
     ) -> Result<Vc<BaseAndFullModuleGraph>> {
-        async move {
-            let module_graphs_op = whole_app_module_graph_operation(self);
-            let module_graphs_vc = if self.next_mode().await?.is_production() {
-                module_graphs_op.connect()
-            } else {
-                // In development mode, we need to to take and drop the issues, otherwise every
-                // route will report all issues.
-                let vc = module_graphs_op.resolve_strongly_consistent().await?;
-                module_graphs_op.drop_issues();
-                *vc
-            };
-
-            // At this point all modules have been computed and we can get rid of the node.js
-            // process pools
-            let execution_context = self.execution_context().await?;
-            let node_backend = execution_context.node_backend.into_trait_ref().await?;
-            if *self.is_watch_enabled().await? {
-                node_backend.scale_down()?;
-            } else {
-                node_backend.scale_zero()?;
-            }
+        let module_graphs_op = whole_app_module_graph_operation(self);
+        let module_graphs_vc = if self.next_mode().await?.is_production() {
+            module_graphs_op.connect()
+        } else {
+            // In development mode, we need to to take and drop the issues, otherwise every
+            // route will report all issues.
+            let vc = module_graphs_op.resolve_strongly_consistent().await?;
+            module_graphs_op.drop_issues();
+            *vc
+        };

-            Ok(module_graphs_vc)
+        // At this point all modules have been computed and we can get rid of the node.js
+        // process pools
+        let execution_context = self.execution_context().await?;
+        let node_backend = execution_context.node_backend.into_trait_ref().await?;
+        if *self.is_watch_enabled().await? {
+            node_backend.scale_down()?;
+        } else {
+            node_backend.scale_zero()?;
         }
-        .instrument(tracing::info_span!("module graph for app"))
-        .await
+
+        Ok(module_graphs_vc)
     }

     #[turbo_tasks::function]
@@ -2435,67 +2431,89 @@ impl Project {
 async fn whole_app_module_graph_operation(
     project: ResolvedVc<Project>,
 ) -> Result<Vc<BaseAndFullModuleGraph>> {
-    let next_mode = project.next_mode();
-    let next_mode_ref = next_mode.await?;
-    let should_trace = next_mode_ref.is_production();
-    let should_read_binding_usage = next_mode_ref.is_production();
-    let base_single_module_graph = SingleModuleGraph::new_with_entries(
-        project.get_all_entries().to_resolved().await?,
-        should_trace,
-        should_read_binding_usage,
-    );
-    let base_visited_modules = VisitedModules::from_graph(base_single_module_graph);
-
-    let base = ModuleGraph::from_single_graph(base_single_module_graph);
-
-    let turbopack_remove_unused_imports = *project
-        .next_config()
-        .turbopack_remove_unused_imports(next_mode)
-        .await?;
+    let span = tracing::info_span!("whole app module graph", modules = Empty);
+    let span_clone = span.clone();
+    async move {
+        let next_mode = project.next_mode();
+        let next_mode_ref = next_mode.await?;
+        let should_trace = next_mode_ref.is_production();
+        let should_read_binding_usage = next_mode_ref.is_production();
+        let base_single_module_graph = SingleModuleGraph::new_with_entries(
+            project.get_all_entries().to_resolved().await?,
+            should_trace,
+            should_read_binding_usage,
+        );
+        let base_visited_modules = VisitedModules::from_graph(base_single_module_graph);

-    let base = if turbopack_remove_unused_imports {
-        // TODO suboptimal that we do compute_binding_usage_info twice (once for the base graph
-        // and later for the full graph)
-        let binding_usage_info = compute_binding_usage_info(base, true);
-        ModuleGraph::from_single_graph_without_unused_references(
-            base_single_module_graph,
-            binding_usage_info,
-        )
-    } else {
-        base
-    };
+        let base = ModuleGraph::from_single_graph(base_single_module_graph);

-    let additional_entries = project
-        .get_all_additional_entries(base.connect())
-        .to_resolved()
-        .await?;
+        let turbopack_remove_unused_imports = *project
+            .next_config()
+            .turbopack_remove_unused_imports(next_mode)
+            .await?;

-    let additional_module_graph = SingleModuleGraph::new_with_entries_visited(
-        additional_entries,
-        base_visited_modules,
-        should_trace,
-        should_read_binding_usage,
-    );
-
-    let graphs = vec![base_single_module_graph, additional_module_graph];
-
-    let (full, binding_usage_info) = if turbopack_remove_unused_imports {
-        let full_with_unused_references = ModuleGraph::from_graphs(graphs.clone());
-        let binding_usage_info = compute_binding_usage_info(full_with_unused_references, true);
-        (
-            ModuleGraph::from_graphs_without_unused_references(graphs, binding_usage_info),
-            Some(binding_usage_info),
-        )
-    } else {
-        (ModuleGraph::from_graphs(graphs), None)
-    };
+        let base = if turbopack_remove_unused_imports {
+            // TODO suboptimal that we do compute_binding_usage_info twice (once for the base
+            // graph and later for the full graph)
+            let binding_usage_info = compute_binding_usage_info(base, true);
+            ModuleGraph::from_single_graph_without_unused_references(
+                base_single_module_graph,
+                binding_usage_info,
+            )
+        } else {
+            base
+        };

-    Ok(BaseAndFullModuleGraph {
-        base: base.connect().to_resolved().await?,
-        full: full.connect().to_resolved().await?,
-        binding_usage_info,
+        let additional_entries = project
+            .get_all_additional_entries(base.connect())
+            .to_resolved()
+            .await?;
+
+        let additional_module_graph = SingleModuleGraph::new_with_entries_visited(
+            additional_entries,
+            base_visited_modules,
+            should_trace,
+            should_read_binding_usage,
+        );
+
+        if !span.is_disabled() {
+            let base_module_count = base_single_module_graph
+                .connect()
+                .module_count()
+                .untracked()
+                .owned()
+                .await?;
+            let additional_module_count = additional_module_graph
+                .connect()
+                .module_count()
+                .untracked()
+                .owned()
+                .await?;
+            span.record("modules", base_module_count + additional_module_count);
+        }
+
+        let graphs = vec![base_single_module_graph, additional_module_graph];
+
+        let (full, binding_usage_info) = if turbopack_remove_unused_imports {
+            let full_with_unused_references = ModuleGraph::from_graphs(graphs.clone());
+            let binding_usage_info = compute_binding_usage_info(full_with_unused_references, true);
+            (
+                ModuleGraph::from_graphs_without_unused_references(graphs, binding_usage_info),
+                Some(binding_usage_info),
+            )
+        } else {
+            (ModuleGraph::from_graphs(graphs), None)
+        };
+
+        Ok(BaseAndFullModuleGraph {
+            base: base.connect().to_resolved().await?,
+            full: full.connect().to_resolved().await?,
+            binding_usage_info,
+        }
+        .cell())
     }
-    .cell())
+    .instrument(span_clone)
+    .await
 }

 #[turbo_tasks::value(shared)]
diff --git a/turbopack/crates/turbopack-core/src/module_graph/mod.rs b/turbopack/crates/turbopack-core/src/module_graph/mod.rs
index d6ac853c41528f..8d62eecdbd0ee9 100644
--- a/turbopack/crates/turbopack-core/src/module_graph/mod.rs
+++ b/turbopack/crates/turbopack-core/src/module_graph/mod.rs
@@ -1522,6 +1522,11 @@ impl SingleModuleGraph {
         )
         .await
     }
+
+    #[turbo_tasks::function]
+    pub async fn module_count(&self) -> Result<Vc<u64>> {
+        Ok(Vc::cell(self.number_of_modules as u64))
+    }
 }

 #[derive(Clone, Debug, Serialize, Deserialize, TraceRawVcs, NonLocalValue)]

PATCH

echo "Patch applied successfully."
