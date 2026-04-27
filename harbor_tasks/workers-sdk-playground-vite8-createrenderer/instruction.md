# Fix Vite 8 runtime crash and asset paths in Workers Playground

## Problem

After the Vite 8 upgrade (which replaces Rollup with rolldown as its bundler), the Workers Playground application (`packages/workers-playground`) has two critical issues that prevent it from working in production.

### 1. Runtime crash: `createRenderer is not a function`

The application crashes at runtime with:

```
Uncaught TypeError: createRenderer is not a function
    at getRenderer (index-B9Sbpvoo.js:42950:28)
```

This error originates from the `@cloudflare/style-provider` package. When bundled with Vite 8's rolldown bundler, `createRenderer` is not properly included in the output bundle — it ends up `undefined` at runtime. The Vite build configuration needs to be updated so that rolldown can correctly resolve and bundle this package's exports.

A correct fix will result in `createRenderer` appearing in the built JavaScript bundle output.

### 2. Broken asset loading in production

The Workers Playground is hosted at the `/playground` path. After building with the current Vite configuration:

- **Static resource paths are wrong**: Generated HTML references static resources (such as `favicon.ico`) with a `/playground/` prefix (e.g., `/playground/favicon.ico`), but Wrangler serves these root-level static resources without that prefix, so they 404 in production.
- **JS/CSS assets must be under `dist/playground/`**: Wrangler serves assets based on their physical location in the dist directory. For the Workers Playground (hosted at `/playground`), compiled JS and CSS assets must be physically located under `dist/playground/` so Wrangler can serve them at the correct URL paths.

The Vite build configuration needs to be updated so that:
1. Static resources in the generated HTML are NOT referenced with a `/playground/` prefix (e.g., `/playground/favicon.ico` must not appear in `index.html`)
2. Compiled JS and CSS assets are physically placed under `dist/playground/` in the build output

## Expected Behavior

- The Workers Playground should build successfully with Vite 8 and the built bundle must contain `createRenderer` (no runtime TypeError)
- Generated HTML must not reference static resources (like favicon) with a `/playground/` prefix
- Built JS/CSS assets must be physically located under `dist/playground/` for correct Wrangler deployment
- The existing `react/jsx-runtime.js` alias in `vite.config.ts` must be preserved
- The repository's changeset policy (per AGENTS.md) must be followed — changes to published packages like `@cloudflare/workers-playground` require a changeset entry in `.changeset/`
- The solution must pass the repository's lint (`check:lint`) and format (`check:format`) checks
