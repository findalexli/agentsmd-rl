# Fix astro:config/client Build Failure in Client Scripts

## Problem Description

When importing `astro:config/client` inside a `<script>` tag in an Astro component and running `astro build`, the build fails with this error:

```
failed to resolve import "virtual:astro:routes" from "virtual:astro:manifest"
```

This error occurs because `virtual:astro:manifest` (which provides `astro:config/server`) imports server-only virtual modules (`virtual:astro:routes`, `virtual:astro:pages`) that are not available in client builds. The `astro:config/client` virtual module is trying to import from `virtual:astro:manifest` to get configuration values, which pulls in these unavailable server dependencies.

## Required Behavior

1. **The `astro:config/client` virtual module must work in client builds without causing the "failed to resolve import 'virtual:astro:routes' from 'virtual:astro:manifest'" error.** The `astro:config/client` module should not import from `virtual:astro:manifest` since that pulls in server-only dependencies.

2. **The `virtual:astro:manifest` module must be restricted to server-only environments.** The plugin that serves `virtual:astro:manifest` should implement `applyToEnvironment(environment)` and only serve the module in these environments:
   - `ASTRO_VITE_ENVIRONMENT_NAMES.astro`
   - `ASTRO_VITE_ENVIRONMENT_NAMES.ssr`
   - `ASTRO_VITE_ENVIRONMENT_NAMES.prerender`

3. **The `astro:config/client` virtual module must export these properties**: `base`, `i18n`, `trailingSlash`, `site`, `compressHTML`, `build`, `image`

4. **Config values must be properly serialized for client code.** String values (`base` and `site`) must be serialized using `JSON.stringify()` in the generated code to handle special characters.

5. **i18n configuration must match the serialized manifest format.** The i18n routing configuration should use these utilities from `../core/app/common.js` to ensure the client config matches the format used by the server manifest:
   - `fromRoutingStrategy`
   - `toFallbackType`
   - `toRoutingStrategy`

## Implementation Requirements

The following specific implementation details must be present:

- `virtualModulePlugin` must accept a `settings` parameter: `export default function virtualModulePlugin({ settings })`
- `createVite` must pass settings to the plugin: `astroVirtualManifestPlugin({ settings })`
- The client config handler must pre-compute config values and return them directly

## Files Likely Involved

Based on the error and Astro's architecture, you will likely need to modify:
- `packages/astro/src/manifest/virtual-module.ts` - Virtual module plugin code
- `packages/astro/src/manifest/serialized.ts` - Serialized manifest plugin code
- `packages/astro/src/core/create-vite.ts` - Vite creation code that wires up plugins

## Verification

To verify the fix:
1. Create an Astro component with a `<script>` tag that imports from `astro:config/client`
2. Run `astro build` - it should complete successfully without "failed to resolve import" errors
3. The client script should have access to the config values at runtime
