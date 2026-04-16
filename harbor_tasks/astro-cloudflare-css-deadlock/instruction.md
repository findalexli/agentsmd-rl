# Fix Dev Server Hang with Cloudflare Adapter

## Problem

When using `@astrojs/cloudflare` in dev mode, the dev server permanently hangs on the first HTTP request. The server never responds and appears stuck indefinitely.

## Background

Astro's development server recursively walks Vite's module graph to load modules before collecting CSS. Virtual modules with these IDs are involved:

- `\0virtual:astro:dev-css`
- `\0virtual:astro:dev-css-all`
- `\0virtual:astro:dev-css:` (prefix for per-route modules)

Named constants for these IDs are defined in `packages/astro/src/vite-plugin-css/const.ts`.

The module-walking function in `packages/astro/src/vite-plugin-css/index.ts` is named `ensureModulesLoaded`.

## Your Task

Fix the hang so that the dev server responds normally when using the Cloudflare adapter.

## Verification

After making changes:
1. Run `pnpm -C packages/astro build`
2. Verify TypeScript compilation succeeds
3. Run lint: `pnpm lint`
