# Embed WebUI in Binary with Proxy Fallback

## Problem

The opencode server currently proxies all WebUI requests to `https://app.opencode.ai`. This means the WebUI always requires an internet connection and depends on the external hosted version. There's no way to serve the UI from the binary itself for offline or self-contained deployments.

## What needs to change

Three files need modifications:

### 1. `packages/opencode/script/build.ts`

The build script needs to support embedding the WebUI assets from `packages/app/dist` into the binary at build time. When embedding is enabled, the build should:
- Build the WebUI from `packages/app`
- Scan all files in the `dist` output
- Generate a TypeScript module that imports each file and exports a mapping of paths to file references
- Include this generated module as an additional entrypoint in the Bun build

There should also be a `--skip-embed-web-ui` flag to opt out of embedding.

### 2. `packages/opencode/src/flag/flag.ts`

Add a runtime flag `OPENCODE_DISABLE_EMBEDDED_WEB_UI` (using the existing `truthy()` helper) that allows users to disable the embedded UI at runtime, falling back to the proxy behavior.

### 3. `packages/opencode/src/server/server.ts`

The catch-all route handler (`.all("/*", ...)`) currently always proxies to `app.opencode.ai`. It needs to be updated to:
- Attempt to import the generated embedded UI module (which only exists in built binaries)
- If the embedded UI is available (and not disabled via the flag), serve files directly from it:
  - Strip the leading `/` from the request path to look up files
  - Fall back to `index.html` for SPA routing
  - Set appropriate `Content-Type` from `Bun.file()`
  - Set a Content Security Policy header for HTML responses
- If the embedded UI is not available or is disabled, fall back to the existing proxy behavior

The embedded UI module import should use a dynamic `import()` with `@ts-expect-error` since the file only exists after build, and should be wrapped in `.catch(() => null)` to gracefully handle the missing module case during development.

## Files to modify

- `packages/opencode/script/build.ts`
- `packages/opencode/src/flag/flag.ts`
- `packages/opencode/src/server/server.ts`
