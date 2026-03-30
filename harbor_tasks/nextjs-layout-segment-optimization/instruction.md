# Fix layout segment optimization: move app-page imports to server-utility transition

## Bug Description

The Turbopack layout segment optimization in Next.js is broken because server-side imports in the `app-page.ts` template are not placed in the `next-server-utility` transition layer. Instead, these imports rely on `SharedMerged` chunk groups to handle them, which causes the layout segment optimization to break when the `parent` entry is passed into `SharedMerged`. This results in incorrect module graph construction for app pages that have layout segments.

Additionally, the `app_module_graphs` function takes separate `client_shared_entries` and `has_layout_segments` parameters, but passing `client_shared_entries` when there are no layout segments (e.g., route handlers) creates a dead code path.

The specific issues are:

1. In `app-page.ts`, server-side imports (like `getRevalidateReason`, `getTracer`, `request-meta`, `interopDefault`, etc.) lack the `with { 'turbopack-transition': 'next-server-utility' }` annotation, so they end up in the wrong layer.

2. In `app_page_loader_tree.rs`, the `fillMetadataSegment` import unnecessarily includes the `next-server-utility` transition (it should not need it once the template imports are properly annotated).

3. In `app.rs`, the `app_module_graphs` API uses two separate parameters (`client_shared_entries` + `has_layout_segments`) instead of a single `Option` parameter, leading to confusing semantics and a dead code path for non-page endpoints.

4. In `chunk_group_info.rs`, there is no `SharedMultiple` variant to support multiple shared entries without a merge tag, forcing the use of `SharedMerged` with a `parent` that breaks the optimization.

## Affected Code

- `packages/next/src/build/templates/app-page.ts` — add `with { 'turbopack-transition': 'next-server-utility' }` to all server-side imports
- `crates/next-core/src/app_page_loader_tree.rs` — remove unnecessary `next-server-utility` transition from `fillMetadataSegment` import
- `crates/next-api/src/app.rs` — refactor `app_module_graphs` to combine parameters into `Option<Vc<EvaluatableAssets>>`
- `turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs` — add `SharedMultiple` chunk group variant

## Acceptance Criteria

- All server-side imports in `app-page.ts` have the `next-server-utility` turbopack transition annotation
- The `fillMetadataSegment` import in `app_page_loader_tree.rs` no longer has the transition annotation
- `app_module_graphs` takes an `Option<Vc<EvaluatableAssets>>` instead of two separate parameters
- A new `SharedMultiple` variant exists in `ChunkGroupEntry`, `ChunkGroup`, and `ChunkGroupKey`
- Route handlers no longer pass client runtime entries to `app_module_graphs`
