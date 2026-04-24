# Fix astro:config/client Build Failure in Client Scripts

## Problem Description

When importing `astro:config/client` inside a `<script>` tag in an Astro component and running `astro build`, the build fails with this error:

```
failed to resolve import "virtual:astro:routes" from "virtual:astro:manifest"
```

### Root Cause

The client handler in `packages/astro/src/manifest/virtual-module.ts` currently imports from `SERIALIZED_MANIFEST_ID` (`virtual:astro:manifest`). Since `virtual:astro:manifest` imports server-only virtual modules (`virtual:astro:routes`, `virtual:astro:pages`) that are unavailable in client builds, the build fails.

The manifest plugin in `packages/astro/src/manifest/serialized.ts` does not restrict itself to server environments, so it serves the module in client builds where the server-only imports are unavailable.

The Vite plugin call in `packages/astro/src/core/create-vite.ts` does not pass required parameters to the manifest plugin.

## Required Behavior

1. **`astro:config/client` must not import from `virtual:astro:manifest`.** The client handler in `packages/astro/src/manifest/virtual-module.ts` should generate config values directly without importing `SERIALIZED_MANIFEST_ID`.

2. **`virtual:astro:manifest` must be server-only.** The manifest plugin in `packages/astro/src/manifest/serialized.ts` must restrict itself to server environments so it does not serve in client builds.

3. **Config values must be serializable for client code.** String values must be serialized properly to handle special characters.

4. **i18n routing config must match server format.** The i18n routing configuration should use the same format as the server manifest.

5. **`virtualModulePlugin` must accept parameters.** The plugin in `packages/astro/src/manifest/virtual-module.ts` must receive a settings object parameter.

6. **The plugin call must pass required arguments.** In `packages/astro/src/core/create-vite.ts`, the `astroVirtualManifestPlugin` call must pass required arguments.

7. **`astro:config/client` must export all required properties.** The client config module must export: `base`, `i18n`, `trailingSlash`, `site`, `compressHTML`, `build`, `image`

## Verification

To verify the fix:
1. Build an Astro component that uses `astro:config/client` in a `<script>` tag using `pnpm run build`
2. The build should complete successfully without "failed to resolve import" errors
3. The repo unit tests should pass (including `serializeManifest.test.js`)
