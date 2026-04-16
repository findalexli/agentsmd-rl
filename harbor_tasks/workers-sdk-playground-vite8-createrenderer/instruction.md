# Fix Vite 8 / rolldown crash in Workers Playground

## Problem

After the Vite 8 upgrade (which replaces Rollup with rolldown as its bundler), the Workers Playground application (`packages/workers-playground`) has two critical issues that prevent it from working in production.

### 1. Runtime crash: `createRenderer is not a function`

The application crashes at runtime with:

```
Uncaught TypeError: createRenderer is not a function
    at getRenderer (index-B9Sbpvoo.js:42950:28)
```

This error originates from the `@cloudflare/style-provider` package. This package ships a dual build: an ESM build in its `es/` directory and a CommonJS build in its `lib/` directory. The `es/` directory contains files that are nominally ESM but internally use `require()` calls. Rolldown mishandles this hybrid pattern and generates an anonymous, unreachable module initializer, leaving `createRenderer` as `undefined` at runtime. Rolldown handles pure CJS correctly via its interop layer.

### 2. Broken asset loading in production

The Workers Playground is hosted at the `/playground` path. The current Vite configuration sets `base: '/playground'`, which causes Vite to output HTML that references assets at `/playground/assets/`. However, Wrangler uploads the built assets as though they are at `/assets/`, so all asset URLs in the generated HTML are broken in production. The deployed assets need to be located under a path that includes `playground` to match how Wrangler resolves and serves them.

## Expected Behavior

- The Workers Playground should build successfully with Vite 8 and run without the `createRenderer` TypeError
- Built assets should be served at paths that match how Wrangler deploys them
- The existing `react/jsx-runtime.js` alias in `vite.config.ts` must be preserved
- The repository's changeset policy (per AGENTS.md) must be followed — changes to published packages like `@cloudflare/workers-playground` require a changeset entry in `.changeset/`
- The solution must pass the repository's lint (`check:lint`) and format (`check:format`) checks

## Relevant Context

- `packages/workers-playground/vite.config.ts` — Vite build configuration for the Workers Playground SPA
- `.changeset/` — directory where changeset markdown files are stored
