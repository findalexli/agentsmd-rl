# Bug: Turbopack metadata dynamic routes crash with async module dependencies

## Summary

When using Turbopack (the default bundler), metadata dynamic routes such as `opengraph-image.tsx` fail at runtime if they transitively import a module that uses **top-level `await`** (TLA). The page either crashes during rendering or the OG image route returns an error instead of the expected image.

This is a regression. The same setup works correctly with Webpack.

## Reproduction

1. Create an App Router page at `app/blog/[slug]/page.tsx`
2. Add a shared data module `app/data.ts` that uses top-level await:
   ```ts
   const data = await Promise.resolve({ slugs: ['hello-world'] })
   export function getAllSlugs() { return data.slugs }
   ```
3. Create `app/blog/[slug]/opengraph-image.tsx` that imports from `data.ts`
4. Run `next dev` (Turbopack) and visit `/blog/hello-world`
5. The `<meta property="og:image">` tag is missing or the `/blog/hello-world/opengraph-image` route errors

## Root Cause

The issue is in how the app page loader tree (in the Rust crate `next-core`, file `crates/next-core/src/app_page_loader_tree.rs`) generates the JavaScript code for loading metadata modules. Currently:

1. **Metadata modules are eagerly required** at module scope rather than lazily loaded. This means the `require()` call happens at import time, which doesn't properly handle TLA modules that need to be awaited.

2. **The return value of the metadata module import is not properly awaited** in the generated code, so async modules (those with top-level await) don't resolve before their exports are used.

Additionally, the TypeScript layer in `packages/next/src/lib/metadata/resolve-metadata.ts` has a module interop wrapping step around metadata image modules in `collectStaticImagesFiles()`. This wrapping interacts poorly with changes to how the loader tree generates its import code, since the calling convention between the generated loader tree and the metadata resolver must be kept in sync.

## Key Files

- `crates/next-core/src/app_page_loader_tree.rs` — Rust code that generates the JavaScript loader tree for app pages, including how metadata modules (icons, OG images) are imported and referenced
- `packages/next/src/lib/metadata/resolve-metadata.ts` — TypeScript code in `collectStaticImagesFiles()` that calls metadata image modules

## Expected Behavior

- Metadata dynamic routes with async (TLA) dependencies should work identically under Turbopack and Webpack
- The `opengraph-image` route should serve a valid image
- The page should include the correct `og:image` meta tag
