#!/usr/bin/env bash
set -euo pipefail
cd /workspace/next.js

# Idempotent: skip if already applied
grep -q 'SharedMultiple' turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/next-api/src/app.rs b/crates/next-api/src/app.rs
index c539f4e37abade..b2f918fbda732d 100644
--- a/crates/next-api/src/app.rs
+++ b/crates/next-api/src/app.rs
@@ -874,8 +874,7 @@ impl AppProject {
         &self,
         endpoint: Vc<AppEndpoint>,
         rsc_entry: ResolvedVc<Box<dyn Module>>,
-        client_shared_entries: Vc<EvaluatableAssets>,
-        has_layout_segments: bool,
+        client_shared_entries_when_has_layout_segments: Option<Vc<EvaluatableAssets>>,
     ) -> Result<Vc<BaseAndFullModuleGraph>> {
         if *self.project.per_page_module_graph().await? {
             let next_mode = self.project.next_mode();
@@ -883,43 +882,47 @@ impl AppProject {
             let should_trace = next_mode_ref.is_production();
             let should_read_binding_usage = next_mode_ref.is_production();

-            let client_shared_entries = client_shared_entries
-                .await?
-                .into_iter()
-                .map(|m| ResolvedVc::upcast(*m))
-                .collect();
             // Implements layout segment optimization to compute a graph "chain" for each layout
             // segment
             async move {
                 let rsc_entry_chunk_group = ChunkGroupEntry::Entry(vec![rsc_entry]);

                 let mut graphs = vec![];
-                let mut visited_modules = if has_layout_segments {
+                let mut visited_modules = VisitedModules::empty();
+
+                if let Some(client_shared_entries) = client_shared_entries_when_has_layout_segments
+                {
                     let ServerEntries {
-                        server_utils,
                         server_component_entries,
+                        server_utils,
                     } = &*find_server_entries(*rsc_entry, should_trace, should_read_binding_usage)
                         .await?;

+                    let client_shared_entries = client_shared_entries
+                        .await?
+                        .into_iter()
+                        .map(|m| ResolvedVc::upcast(*m))
+                        .collect();
+
+                    // SEGMENT: client_shared_entries and server utils shared by the layout segments
+                    // and the page
                     let graph = SingleModuleGraph::new_with_entries_visited_intern(
                         vec![
-                            ChunkGroupEntry::SharedMerged {
-                                parent: Box::new(rsc_entry_chunk_group.clone()),
-                                merge_tag: NEXT_SERVER_UTILITY_MERGE_TAG.clone(),
-                                entries: server_utils
+                            ChunkGroupEntry::Entry(client_shared_entries),
+                            ChunkGroupEntry::SharedMultiple(
+                                server_utils
                                     .iter()
                                     .map(async |m| Ok(ResolvedVc::upcast(m.await?.module)))
                                     .try_join()
                                     .await?,
-                            },
-                            ChunkGroupEntry::Entry(client_shared_entries),
+                            ),
                         ],
-                        VisitedModules::empty(),
+                        visited_modules,
                         should_trace,
                         should_read_binding_usage,
                     );
                     graphs.push(graph);
-                    let mut visited_modules = VisitedModules::from_graph(graph);
+                    visited_modules = VisitedModules::concatenate(visited_modules, graph);

                     // Skip the last server component, which is the page itself, because that one
                     // won't have it's visited modules added, and will be visited in the next step
@@ -928,6 +931,7 @@ impl AppProject {
                         .iter()
                         .take(server_component_entries.len().saturating_sub(1))
                     {
+                        // SEGMENT: layout segment
                         let graph = SingleModuleGraph::new_with_entries_visited_intern(
                             vec![ChunkGroupEntry::Shared(ResolvedVc::upcast(*module))],
                             visited_modules,
@@ -948,18 +952,9 @@ impl AppProject {
                             VisitedModules::with_incremented_index(visited_modules)
                         };
                     }
-                    visited_modules
-                } else {
-                    let graph = SingleModuleGraph::new_with_entries_visited_intern(
-                        vec![ChunkGroupEntry::Entry(client_shared_entries)],
-                        VisitedModules::empty(),
-                        should_trace,
-                        should_read_binding_usage,
-                    );
-                    graphs.push(graph);
-                    VisitedModules::from_graph(graph)
-                };
+                }

+                // SEGMENT: rsc entry chunk group
                 let graph = SingleModuleGraph::new_with_entries_visited_intern(
                     vec![rsc_entry_chunk_group],
                     visited_modules,
@@ -1254,12 +1249,7 @@ impl AppEndpoint {
                 self,
                 *rsc_entry,
                 // We only need the client runtime entries for pages not for Route Handlers
-                if is_app_page {
-                    this.app_project.client_runtime_entries()
-                } else {
-                    EvaluatableAssets::empty()
-                },
-                is_app_page,
+                is_app_page.then(|| this.app_project.client_runtime_entries()),
             )
             .await?;

@@ -2133,13 +2123,14 @@ impl Endpoint for AppEndpoint {
     async fn module_graphs(self: Vc<Self>) -> Result<Vc<ModuleGraphs>> {
         let this = self.await?;
         let app_entry = self.app_endpoint_entry().await?;
+        let is_app_page = matches!(this.ty, AppEndpointType::Page { .. });
         let module_graphs = this
             .app_project
             .app_module_graphs(
                 self,
                 *app_entry.rsc_entry,
-                this.app_project.client_runtime_entries(),
-                matches!(this.ty, AppEndpointType::Page { .. }),
+                // We only need the client runtime entries for pages not for Route Handlers
+                is_app_page.then(|| this.app_project.client_runtime_entries()),
             )
             .await?;
         Ok(Vc::cell(vec![module_graphs.full]))
diff --git a/crates/next-core/src/app_page_loader_tree.rs b/crates/next-core/src/app_page_loader_tree.rs
index 77292e4ac9bd7a..a10976b59291c9 100644
--- a/crates/next-core/src/app_page_loader_tree.rs
+++ b/crates/next-core/src/app_page_loader_tree.rs
@@ -227,8 +227,7 @@ impl AppPageLoaderTreeBuilder {
         let identifier = magic_identifier::mangle(&format!("{name} #{i}"));
         let inner_module_id = format!("METADATA_{i}");
         let helper_import = rcstr!(
-            "import { fillMetadataSegment } from 'next/dist/lib/metadata/get-metadata-route' with \
-             { 'turbopack-transition': 'next-server-utility' }"
+            "import { fillMetadataSegment } from 'next/dist/lib/metadata/get-metadata-route'"
         );

         if !self.base.imports.contains(&helper_import) {
diff --git a/packages/next/src/build/templates/app-page.ts b/packages/next/src/build/templates/app-page.ts
index fc621e81ba66ec..bafdc15973fe91 100644
--- a/packages/next/src/build/templates/app-page.ts
+++ b/packages/next/src/build/templates/app-page.ts
@@ -9,31 +9,38 @@ import {

 import { RouteKind } from '../../server/route-kind' with { 'turbopack-transition': 'next-server-utility' }

-import { getRevalidateReason } from '../../server/instrumentation/utils'
-import { getTracer, SpanKind, type Span } from '../../server/lib/trace/tracer'
+import { getRevalidateReason } from '../../server/instrumentation/utils' with { 'turbopack-transition': 'next-server-utility' }
+import {
+  getTracer,
+  SpanKind,
+  type Span,
+} from '../../server/lib/trace/tracer' with { 'turbopack-transition': 'next-server-utility' }
 import type { RequestMeta } from '../../server/request-meta'
 import {
   addRequestMeta,
   getRequestMeta,
   setRequestMeta,
-} from '../../server/request-meta'
-import { BaseServerSpan } from '../../server/lib/trace/constants'
-import { interopDefault } from '../../server/app-render/interop-default'
-import { stripFlightHeaders } from '../../server/app-render/strip-flight-headers'
-import { NodeNextRequest, NodeNextResponse } from '../../server/base-http/node'
-import { checkIsAppPPREnabled } from '../../server/lib/experimental/ppr'
+} from '../../server/request-meta' with { 'turbopack-transition': 'next-server-utility' }
+import { BaseServerSpan } from '../../server/lib/trace/constants' with { 'turbopack-transition': 'next-server-utility' }
+import { interopDefault } from '../../server/app-render/interop-default' with { 'turbopack-transition': 'next-server-utility' }
+import { stripFlightHeaders } from '../../server/app-render/strip-flight-headers' with { 'turbopack-transition': 'next-server-utility' }
+import {
+  NodeNextRequest,
+  NodeNextResponse,
+} from '../../server/base-http/node' with { 'turbopack-transition': 'next-server-utility' }
+import { checkIsAppPPREnabled } from '../../server/lib/experimental/ppr' with { 'turbopack-transition': 'next-server-utility' }
 import {
   getFallbackRouteParams,
   createOpaqueFallbackRouteParams,
   type OpaqueFallbackRouteParams,
-} from '../../server/request/fallback-params'
-import { setManifestsSingleton } from '../../server/app-render/manifests-singleton'
+} from '../../server/request/fallback-params' with { 'turbopack-transition': 'next-server-utility' }
+import { setManifestsSingleton } from '../../server/app-render/manifests-singleton' with { 'turbopack-transition': 'next-server-utility' }
 import {
   isHtmlBotRequest,
   shouldServeStreamingMetadata,
-} from '../../server/lib/streaming-metadata'
-import { normalizeAppPath } from '../../shared/lib/router/utils/app-paths'
-import { getIsPossibleServerAction } from '../../server/lib/server-action-request-meta'
+} from '../../server/lib/streaming-metadata' with { 'turbopack-transition': 'next-server-utility' }
+import { normalizeAppPath } from '../../shared/lib/router/utils/app-paths' with { 'turbopack-transition': 'next-server-utility' }
+import { getIsPossibleServerAction } from '../../server/lib/server-action-request-meta' with { 'turbopack-transition': 'next-server-utility' }
 import {
   RSC_HEADER,
   NEXT_ROUTER_PREFETCH_HEADER,
@@ -42,8 +49,11 @@ import {
   NEXT_IS_PRERENDER_HEADER,
   NEXT_DID_POSTPONE_HEADER,
   RSC_CONTENT_TYPE_HEADER,
-} from '../../client/components/app-router-headers'
-import { getBotType, isBot } from '../../shared/lib/router/utils/is-bot'
+} from '../../client/components/app-router-headers' with { 'turbopack-transition': 'next-server-utility' }
+import {
+  getBotType,
+  isBot,
+} from '../../shared/lib/router/utils/is-bot' with { 'turbopack-transition': 'next-server-utility' }
 import {
   CachedRouteKind,
   IncrementalCacheKind,
@@ -51,9 +61,12 @@ import {
   type CachedPageValue,
   type ResponseCacheEntry,
   type ResponseGenerator,
-} from '../../server/response-cache'
-import { FallbackMode, parseFallbackField } from '../../lib/fallback'
-import RenderResult from '../../server/render-result'
+} from '../../server/response-cache' with { 'turbopack-transition': 'next-server-utility' }
+import {
+  FallbackMode,
+  parseFallbackField,
+} from '../../lib/fallback' with { 'turbopack-transition': 'next-server-utility' }
+import RenderResult from '../../server/render-result' with { 'turbopack-transition': 'next-server-utility' }
 import {
   CACHE_ONE_YEAR_SECONDS,
   HTML_CONTENT_TYPE_HEADER,
@@ -61,19 +74,19 @@ import {
   NEXT_NAV_DEPLOYMENT_ID_HEADER,
   NEXT_RESUME_HEADER,
   NEXT_RESUME_STATE_LENGTH_HEADER,
-} from '../../lib/constants'
+} from '../../lib/constants' with { 'turbopack-transition': 'next-server-utility' }
 import type { CacheControl } from '../../server/lib/cache-control'
-import { ENCODED_TAGS } from '../../server/stream-utils/encoded-tags'
-import { createInstantTestScriptInsertionTransformStream } from '../../server/stream-utils/node-web-streams-helper'
-import { sendRenderResult } from '../../server/send-payload'
-import { NoFallbackError } from '../../shared/lib/no-fallback-error.external'
-import { parseMaxPostponedStateSize } from '../../shared/lib/size-limit'
+import { ENCODED_TAGS } from '../../server/stream-utils/encoded-tags' with { 'turbopack-transition': 'next-server-utility' }
+import { createInstantTestScriptInsertionTransformStream } from '../../server/stream-utils/node-web-streams-helper' with { 'turbopack-transition': 'next-server-utility' }
+import { sendRenderResult } from '../../server/send-payload' with { 'turbopack-transition': 'next-server-utility' }
+import { NoFallbackError } from '../../shared/lib/no-fallback-error.external' with { 'turbopack-transition': 'next-server-utility' }
+import { parseMaxPostponedStateSize } from '../../shared/lib/size-limit' with { 'turbopack-transition': 'next-server-utility' }
 import {
   getMaxPostponedStateSize,
   getPostponedStateExceededErrorMessage,
   readBodyWithSizeLimit,
-} from '../../server/lib/postponed-request-body'
-import { parseUrl } from '../../lib/url'
+} from '../../server/lib/postponed-request-body' with { 'turbopack-transition': 'next-server-utility' }
+import { parseUrl } from '../../lib/url' with { 'turbopack-transition': 'next-server-utility' }

 // These are injected by the loader afterwards.

@@ -99,14 +112,14 @@ export const __next_app__ = {
 }

 import * as entryBase from '../../server/app-render/entry-base' with { 'turbopack-transition': 'next-server-utility' }
-import { RedirectStatusCode } from '../../client/components/redirect-status-code'
-import { InvariantError } from '../../shared/lib/invariant-error'
-import { scheduleOnNextTick } from '../../lib/scheduler'
-import { isInterceptionRouteAppPath } from '../../shared/lib/router/utils/interception-routes'
+import { RedirectStatusCode } from '../../client/components/redirect-status-code' with { 'turbopack-transition': 'next-server-utility' }
+import { InvariantError } from '../../shared/lib/invariant-error' with { 'turbopack-transition': 'next-server-utility' }
+import { scheduleOnNextTick } from '../../lib/scheduler' with { 'turbopack-transition': 'next-server-utility' }
+import { isInterceptionRouteAppPath } from '../../shared/lib/router/utils/interception-routes' with { 'turbopack-transition': 'next-server-utility' }
 import {
   getParamProperties,
   getSegmentParam,
-} from '../../shared/lib/router/utils/get-segment-param'
+} from '../../shared/lib/router/utils/get-segment-param' with { 'turbopack-transition': 'next-server-utility' }

 export * from '../../server/app-render/entry-base' with { 'turbopack-transition': 'next-server-utility' }

diff --git a/turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs b/turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs
index 5da760c9cc788c..2de0435dd5251f 100644
--- a/turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs
+++ b/turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs
@@ -136,6 +136,7 @@ pub enum ChunkGroupEntry {
         entries: Vec<ResolvedVc<Box<dyn Module>>>,
     },
     Shared(ResolvedVc<Box<dyn Module>>),
+    SharedMultiple(Vec<ResolvedVc<Box<dyn Module>>>),
     SharedMerged {
         parent: Box<ChunkGroupEntry>,
         merge_tag: RcStr,
@@ -150,6 +151,7 @@ impl ChunkGroupEntry {
             }
             Self::Entry(entries)
             | Self::IsolatedMerged { entries, .. }
+            | Self::SharedMultiple(entries)
             | Self::SharedMerged { entries, .. } => Either::Right(entries.iter().copied()),
         }
     }
@@ -175,6 +177,8 @@ pub enum ChunkGroup {
     /// A shared chunk group. Corresponds to an incoming [ChunkingType::Shared] reference with
     /// `merge_tag: None`
     Shared(ResolvedVc<Box<dyn Module>>),
+    /// A shared chunk group with multiple entries.
+    SharedMultiple(Vec<ResolvedVc<Box<dyn Module>>>),
     /// A shared chunk group. Corresponds to an incoming [ChunkingType::Shared] reference with
     /// `merge_tag: Some(_)`
     SharedMerged {
@@ -205,6 +209,7 @@ impl ChunkGroup {
             }
             ChunkGroup::Entry(entries)
             | ChunkGroup::IsolatedMerged { entries, .. }
+            | ChunkGroup::SharedMultiple(entries)
             | ChunkGroup::SharedMerged { entries, .. } => Either::Right(entries.iter().copied()),
         }
     }
@@ -214,6 +219,7 @@ impl ChunkGroup {
             ChunkGroup::Async(_) | ChunkGroup::Isolated(_) | ChunkGroup::Shared(_) => 1,
             ChunkGroup::Entry(entries)
             | ChunkGroup::IsolatedMerged { entries, .. }
+            | ChunkGroup::SharedMultiple(entries)
             | ChunkGroup::SharedMerged { entries, .. } => entries.len(),
         }
     }
@@ -237,6 +243,14 @@ impl ChunkGroup {
             ChunkGroup::Shared(entry) => turbofmt!("ChunkGroup::Shared({:?})", entry.ident())
                 .await?
                 .to_string(),
+            ChunkGroup::SharedMultiple(entries) => format!(
+                "ChunkGroup::SharedMultiple({:?})",
+                entries
+                    .iter()
+                    .map(|m| m.ident().to_string())
+                    .try_join()
+                    .await?
+            ),
             ChunkGroup::IsolatedMerged {
                 parent,
                 merge_tag,
@@ -286,6 +300,7 @@ pub enum ChunkGroupKey {
         merge_tag: RcStr,
     },
     Shared(ResolvedVc<Box<dyn Module>>),
+    SharedMultiple(Vec<ResolvedVc<Box<dyn Module>>>),
     SharedMerged {
         parent: ChunkGroupId,
         merge_tag: RcStr,
@@ -322,6 +337,14 @@ impl ChunkGroupKey {
             ChunkGroupKey::Shared(module) => {
                 turbofmt!("Shared({:?})", module.ident()).await?.to_string()
             }
+            ChunkGroupKey::SharedMultiple(entries) => format!(
+                "SharedMultiple({:?})",
+                entries
+                    .iter()
+                    .map(|m| m.ident().to_string())
+                    .try_join()
+                    .await?
+            ),
             ChunkGroupKey::SharedMerged { parent, merge_tag } => {
                 format!(
                     "SharedMerged {{ parent: {}, merge_tag: {:?} }}",
@@ -446,6 +469,7 @@ pub async fn compute_chunk_group_info(graph: &ModuleGraph) -> Result<Vc<ChunkGro
                 ChunkGroupEntry::Async(entry) => ChunkGroupKey::Async(entry),
                 ChunkGroupEntry::Isolated(entry) => ChunkGroupKey::Isolated(entry),
                 ChunkGroupEntry::Shared(entry) => ChunkGroupKey::Shared(entry),
+                ChunkGroupEntry::SharedMultiple(entries) => ChunkGroupKey::SharedMultiple(entries),
                 ChunkGroupEntry::IsolatedMerged {
                     parent,
                     merge_tag,
@@ -752,6 +776,7 @@ pub async fn compute_chunk_group_info(graph: &ModuleGraph) -> Result<Vc<ChunkGro
                         }
                     }
                     ChunkGroupKey::Shared(module) => ChunkGroup::Shared(module),
+                    ChunkGroupKey::SharedMultiple(entries) => ChunkGroup::SharedMultiple(entries),
                     ChunkGroupKey::SharedMerged { parent, merge_tag } => ChunkGroup::SharedMerged {
                         parent: parent.0 as usize,
                         merge_tag,

PATCH
