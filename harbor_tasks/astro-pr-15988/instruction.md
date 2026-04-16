# withastro/astro#15988 — CSS Dynamic Import Dev Bug

## The Problem

When using dynamic imports (`await import(...)`) in Astro pages during development, CSS styles from the dynamically imported components are **not injected on the first request** to the dev server. The styles only appear after making a change (triggering HMR) or after the second request.

## Symptom

Visit a page that dynamically imports a component with styles:

```astro
---
const Layout = await import('../layouts/Layout.astro').then((m) => m.default);
---
<Layout>
  <h1>Hello</h1>
</Layout>
```

Where `Layout.astro` has a `<style>` block. On the **very first** request to this page in dev mode, the `<style>` tag is missing from the HTML. Refreshing the page or saving a file fixes it.

## Root Cause

The CSS collection logic in `packages/astro/src/vite-plugin-css/index.ts` walks the Vite module graph to find CSS imports. However, modules from dynamic imports (`import(...)`) may be **registered in the graph** (Vite's import analysis detected them) but **not yet transformed** (their imports haven't been resolved yet). When the CSS walk reaches these untransformed modules, their `importedModules` set is incomplete — so their CSS is never collected.

## Required Behavior

The plugin must ensure that all modules in the dependency graph reachable from the entry module are fully transformed before the CSS collection walk begins. Specifically:

1. **Pre-walk the module graph**: Before the existing CSS collection in the load handler, traverse the entire module graph reachable from the entry module to ensure all modules are processed.

2. **Trigger transformation for untransformed modules**: For each module encountered, check if it has been transformed. If a module lacks a transformation result, trigger Vite's transformation pipeline for that module.

3. **Handle circular dependencies**: Track already-visited modules to avoid infinite loops during the graph traversal.

4. **Skip asset propagation markers**: Modules with the propagated asset query parameter (`PROPAGATED_ASSET_QUERY_PARAM`) in their id should be skipped (these are not real modules but asset propagation markers).

5. **Traverse recursively**: Walk the graph depth-first by iterating over each module's imported modules and recursively processing those imports.

6. **Integration with load handler**: This pre-walk logic must be invoked before the existing CSS collection logic (`collectCSSWithOrder`) in the load handler, using the dev environment (`env`) and the entry module (`mod`) available in that context.

## Validation

After applying the fix, the following must all pass:
- TypeScript type-check (`tsc --noEmit`) on the `packages/astro` package
- Unit tests (`pnpm run test:unit` in `packages/astro`)
- Knip dead-code detection (`pnpm knip` at repo root)
- Biome lint on `packages/astro/src/vite-plugin-css/`
