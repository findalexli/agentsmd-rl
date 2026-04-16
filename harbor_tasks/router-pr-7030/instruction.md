# CSS Assets Duplicated in Start Manifest

## Problem

The TanStack Start manifest builder in the `@tanstack/start-plugin-core` package is producing manifests with duplicate CSS asset entries. This causes redundant `<link>` tags to be injected into pages, resulting in unnecessary network requests and potential flash-of-unstyled-content issues.

The bug has two dimensions:

1. **Within a single route (diamond imports)**: When a route chunk imports multiple chunks that share a common CSS dependency (diamond pattern), that shared CSS appears multiple times in the route's asset list. For example, if chunk A imports chunks B and C, and both B and C import a shared chunk S with `shared.css`, then `shared.css` appears twice in A's collected CSS assets. The correct behavior is that each unique CSS file should appear exactly once — so if there are 4 distinct CSS files across the import graph (e.g., `a.css`, `b.css`, `c.css`, `shared.css`), the result should contain exactly 4 assets with 4 unique `href` values.

2. **Across parent-child routes**: When a child route imports CSS that's already present in an ancestor route's assets, that CSS is repeated in the child's asset list. For example, given a route tree where the root route already includes `shared.css` and `parent.css`, a child route `/child` that also transitively imports those same CSS files should only list its own unique CSS (e.g., `child.css`) — the child route's `assets` array should contain exactly 1 entry, not 3. The ancestor's CSS is already loaded and should not be duplicated in descendants.

However, CSS shared between sibling or cousin routes that is **not** present in their common ancestor must still appear in each sibling/cousin that needs it. For example, if routes `/a-child` and `/b-child` are cousins (under different parent branches) and both import a chunk with `deep.css`, then both `/a-child` and `/b-child` should each have `deep.css` in their assets — deduplication only removes CSS that an ancestor already provides, not CSS used by unrelated routes.

## Data Structures

### `RouterManagedTag`

CSS assets in the manifest are represented as `RouterManagedTag` objects with this structure:

```typescript
interface RouterManagedTag {
  tag: 'link'
  attrs: {
    rel: 'stylesheet'
    href: string    // e.g., '/assets/child.css'
    type: 'text/css'
  }
}
```

The `attrs.href` property is the key identifier used for deduplication — two assets with the same `href` are considered duplicates.

### Manifest Structure

The `buildStartManifest` function returns an object with the following structure:

```typescript
interface StartManifest {
  routes: Record<string, {
    assets: Array<RouterManagedTag>
    // ... other route properties (preloads, etc.)
  }>
}
```

Route entries are keyed by route ID (e.g., `'/child'`, `'/parent'`, `'__root__'`). Each route's `assets` array contains the `RouterManagedTag` entries for CSS stylesheets needed by that route.

### Chunk Structure

Vite/Rollup output chunks have the following relevant shape:

```typescript
interface OutputChunk {
  type: 'chunk'
  fileName: string
  imports: Array<string>         // filenames of statically imported chunks
  dynamicImports: Array<string>
  isEntry: boolean
  moduleIds: Array<string>       // e.g., ['/routes/parent.tsx?tsr-split=component']
  viteMetadata: {
    importedCss: Set<string>     // CSS files directly imported by this chunk
  }
}
```

### Route Tree Structure

The route tree passed to `buildStartManifest` uses this shape:

```typescript
interface RouteTreeRoutes {
  [routeId: string]: {
    filePath?: string          // e.g., '/routes/parent.tsx'
    children?: Array<string>   // child route IDs
  }
}
```

The root route is keyed as `__root__`.

## Key Functions

The manifest builder module (`packages/start-plugin-core/src/start-manifest-plugin/manifestBuilder.ts`) exports:

- **`createChunkCssAssetCollector(options)`** — Creates a collector for gathering CSS assets from chunks. Accepts `chunksByFileName` (a `Map<string, OutputChunk>`) and `getStylesheetAsset` (a callback `(cssFile: string) => RouterManagedTag`). Returns an object with `getChunkCssAssets(chunk)` which should return an `Array<RouterManagedTag>` with no duplicate `href` values.

- **`buildStartManifest(options)`** — Builds the complete route manifest. Accepts `clientBundle` (`Record<string, OutputChunk>`), `routeTreeRoutes` (`Record<string, { filePath?, children? }>`), and `basePath` (string, e.g., `'/assets'`). Returns the manifest with `routes` where each route's `assets` array should not contain CSS already present in ancestor routes.

## Expected Behavior Summary

1. `getChunkCssAssets` must return an array where each CSS `href` appears at most once, even when the chunk's import graph has diamond dependencies
2. In the manifest returned by `buildStartManifest`, a child route's `assets` must not contain CSS entries that already appear in an ancestor route's `assets`
3. Sibling/cousin routes under different branches of the route tree must each independently receive CSS assets they need — deduplication only applies along ancestor chains, not across unrelated branches
4. Existing ESLint checks, TypeScript type checking, and unit tests in the package must continue to pass
