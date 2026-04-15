# Fix layout segment optimization: Turbopack transition layer for app-page imports

## Bug Description

The Turbopack layout segment optimization in Next.js is broken due to several interacting issues in how server-side imports are annotated and how module graphs are constructed for app pages with layout segments.

The core problem is that server-side imports in the `app-page.ts` template file are not being placed into the `next-server-utility` Turbopack transition layer. Only a few imports (such as `RouteKind` and the `entry-base` re-export) currently carry this transition annotation. The remaining server-side imports from paths including `server/instrumentation/utils`, `server/lib/trace/tracer`, `server/request-meta`, `server/lib/trace/constants`, `server/app-render/interop-default`, `server/app-render/strip-flight-headers`, `server/base-http/node`, `server/lib/experimental/ppr`, `server/request/fallback-params`, `server/app-render/manifests-singleton`, `server/lib/streaming-metadata`, `shared/lib/router/utils/app-paths`, `server/lib/server-action-request-meta`, `client/components/app-router-headers`, `shared/lib/router/utils/is-bot`, `server/response-cache`, `lib/fallback`, `server/render-result`, `lib/constants`, `server/stream-utils/encoded-tags`, `server/stream-utils/node-web-streams-helper`, `server/send-payload`, `shared/lib/no-fallback-error`, `shared/lib/size-limit`, `server/lib/postponed-request-body`, `lib/url`, `client/components/redirect-status-code`, `shared/lib/invariant-error`, `lib/scheduler`, `shared/lib/router/utils/interception-routes`, and `shared/lib/router/utils/get-segment-param` are all missing this annotation. Without it, these imports end up in the wrong chunk layer and the layout segment optimization cannot correctly group them.

## Specific Issues

### 1. Missing transition annotations in app-page template

In `packages/next/src/build/templates/app-page.ts`, the server-side imports listed above lack the `next-server-utility` turbopack transition. Compare with the imports that already have it (like `RouteKind` from `route-kind`) to see the correct annotation pattern.

### 2. Spurious transition on fillMetadataSegment import

In `crates/next-core/src/app_page_loader_tree.rs`, the `fillMetadataSegment` import from `next/dist/lib/metadata/get-metadata-route` includes the `next-server-utility` transition annotation. This metadata helper is not a server utility and should not carry the transition — especially once the template imports are properly annotated.

### 3. app_module_graphs parameter design flaw

In `crates/next-api/src/app.rs`, the `app_module_graphs` function takes two separate parameters: `client_shared_entries` (typed as `Vc<EvaluatableAssets>`) and `has_layout_segments` (a `bool`). This design forces callers to always provide client shared entries, even when there are no layout segments. Route handlers currently work around this by passing `EvaluatableAssets::empty()`, which creates a dead code path inside the function. The function should instead use a single optional parameter so that non-page endpoints naturally express "no client entries" without the empty sentinel.

### 4. Missing chunk group variant for multiple shared entries without merge

In `turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs`, the chunk group system has no way to represent multiple shared entries without a merge tag. The only option for grouping multiple shared modules is `SharedMerged`, which requires a `parent` entry and a `merge_tag`. When the layout segment optimization groups server utilities as shared entries, using `SharedMerged` with a parent entry breaks the optimization because the parent is itself part of the chunk graph being constructed. A new variant is needed in each of the three related enums — `ChunkGroupEntry`, `ChunkGroup`, and `ChunkGroupKey` — to represent a collection of shared entries without requiring a parent or merge tag. This variant must be integrated into all existing pattern-match arms (entries iteration, count, debug formatting, chunk group key computation, and chunk group construction).

### 5. Route handlers unnecessarily create empty assets

As a consequence of issue 3, the route handler code paths in `app.rs` pass `EvaluatableAssets::empty()` to `app_module_graphs`. After resolving the parameter design, route handlers should no longer need to create or pass empty asset collections.

## References

- PR #91701 in vercel/next.js (commit 883d93c8935afb2b8124ab324a10fa36cbd7a88c)
