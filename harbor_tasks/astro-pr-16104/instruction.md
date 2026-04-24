# Fix astro preview host validation

## Problem

When you configure `vite.preview.allowedHosts` in your `astro.config.mjs`, the `astro preview` command ignores it. Requests to hosts listed in `vite.preview.allowedHosts` are rejected with a 403 Forbidden, even though you explicitly allowed them.

For example, with this config:
```js
// astro.config.mjs
export default {
  vite: {
    preview: {
      allowedHosts: ["example.com"]
    }
  }
}
```

Running `astro preview` and making a request to `example.com` returns 403 instead of 200.

## Expected Behavior

The preview server should respect `vite.preview.*` settings from the user's `astro.config.mjs`. Specifically, `vite.preview.allowedHosts` should be honored when the user has configured them.

When merging configuration, plugins from the user's vite config must not conflict with Astro's internal plugins. The source implementation must destructure and exclude plugins from the user config before merging.

If the user has explicitly set `server.allowedHosts` in their Astro config (as a boolean or non-empty array), that setting should take precedence over any `allowedHosts` value from the user's vite config. The implementation must use a type check to distinguish boolean from array values.

## Required Source Code Patterns

The fix must be implemented in the preview server source file (`packages/astro/src/core/preview/static-preview-server.ts`). The implementation must include the following patterns:

1. **Configuration merging**: The source must call `mergeConfig` and read from `settings.config.vite` to obtain the user's vite configuration.

2. **Plugin exclusion**: When destructuring the user's vite config, plugins must be excluded using a pattern like `plugins: _plugins` to avoid conflicts with Astro's internal plugins.

3. **Precedence check**: To determine if `server.allowedHosts` was explicitly set, the implementation must check `typeof allowedHosts` and compare against `'boolean'` to distinguish between boolean and array values.

## Bug Verification

After the fix:
- The preview server accepts requests to hosts listed in `vite.preview.allowedHosts`
- User plugins do not conflict with Astro's internal plugins
- `server.allowedHosts` (when explicitly set) takes precedence over `vite.preview.allowedHosts`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
