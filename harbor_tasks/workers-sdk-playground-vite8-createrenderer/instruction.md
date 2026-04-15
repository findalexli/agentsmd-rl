# Fix Vite 8 / rolldown crash: TypeError: createRenderer is not a function

## Problem

After upgrading to Vite 8 (which uses rolldown as its bundler), the Workers Playground application crashes at runtime with:

```
Uncaught TypeError: createRenderer is not a function
    at getRenderer (index-B9Sbpvoo.js:42950:28)
```

The `@cloudflare/style-provider` package ships a hybrid ESM+CJS build. Its `es/` directory contains files that are nominally ESM but internally use `require()`. Rolldown (Vite 8's new bundler) mishandles this pattern and generates an anonymous, unreachable module initializer, leaving `createRenderer` as `undefined` at runtime.

Additionally, the built assets are deployed to incorrect paths by Wrangler. The HTML references assets at one path, but Wrangler uploads them to a different location, resulting in broken asset loading.

## Expected Behavior

- The application should build and run without the `createRenderer` TypeError
- Built assets should be deployed at paths that match how Wrangler serves them
- The changeset policy (per AGENTS.md) must be followed for changes to published packages

## Configuration Requirements

The Workers Playground vite configuration (`packages/workers-playground/vite.config.ts`) must satisfy all of the following:

1. **style-provider alias**: In `resolve.alias`, the `@cloudflare/style-provider` package must be aliased to a path that routes to its CommonJS build (the `lib/` directory inside the package), not the ESM `es/` directory. This is required because rolldown mishandles the hybrid ESM+CJS pattern in the `es/` directory, causing `createRenderer` to be `undefined` at runtime.

2. **No `base: '/playground'`**: The `base` option must not be set to `'/playground'`. That value causes Vite to generate HTML with asset references at `/playground/assets/`, while Wrangler uploads assets as if they are at `/assets/`, breaking all asset loading in production.

3. **assetsDir containing `playground`**: The `build.assetsDir` option must place built assets under a path that includes the word `playground`. This ensures the asset paths in the generated HTML match where Wrangler actually deploys the files.

4. **Changeset for published package**: A changeset file under `.changeset/` must exist that references `@cloudflare/workers-playground`. The repo's AGENTS.md requires a changeset for every change to a published package, and the CI will fail without it.

## Files to Look At

- `packages/workers-playground/vite.config.ts` — Vite build configuration for the Workers Playground SPA
- `.changeset/` — directory where changeset files are stored