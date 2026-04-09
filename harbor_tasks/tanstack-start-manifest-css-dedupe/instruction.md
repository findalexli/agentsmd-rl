# Fix CSS Asset Deduplication in TanStack Start Manifest

## Problem

CSS assets in the Start manifest are being duplicated in two scenarios:

1. **Within route entries**: When a chunk imports multiple other chunks that share a common dependency (e.g., both B and C import "shared.js"), the shared CSS appears multiple times in the collected assets.

2. **Across parent-child route chains**: Shared stylesheets appear multiple times within a route entry or across an active parent-child route chain.

## Relevant Files

- `packages/start-plugin-core/src/start-manifest-plugin/manifestBuilder.ts` - Contains the manifest building logic

## Key Functions

The following functions are involved in CSS asset collection and deduplication:

- `createChunkCssAssetCollector()` - Collects CSS assets from chunks and their imports
- `buildStartManifest()` - Main entry point for building the manifest
- `dedupeNestedRoutePreloads()` - Currently only deduplicates preloads, not assets

## Expected Behavior

CSS assets should be deduplicated:
- Shared CSS from common imported chunks should only appear once per route entry
- Assets already present in ancestor routes should not be duplicated in child routes
- Cousin routes (different branches) should maintain their own copies

## Testing

The existing test file `packages/start-plugin-core/tests/start-manifest-plugin/manifestBuilder.test.ts` contains tests that verify the correct deduplication behavior. Run tests with:

```bash
pnpm nx run @tanstack/start-plugin-core:test:unit -- tests/start-manifest-plugin/manifestBuilder.test.ts
```

## Hints

- The `createChunkCssAssetCollector` function currently collects CSS assets from each import path independently, which causes duplicates when chunks share common dependencies
- The deduplication logic for preloads (`dedupeNestedRoutePreloads`) provides a pattern that could be extended to assets as well
- Consider tracking "seen" assets during collection to avoid duplicates
