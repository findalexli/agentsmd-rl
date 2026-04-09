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

## Files to Look At

- `packages/workers-playground/vite.config.ts` — Vite build configuration for the Workers Playground SPA
