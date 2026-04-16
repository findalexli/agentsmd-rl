# Fix astro preview host validation

## Problem

When you configure `vite.preview.allowedHosts` in your `astro.config.mjs`, the `astro preview` command ignores it. Requests to hosts listed in `vite.preview.allowedHosts` are rejected with a 403 Forbidden, even though you explicitly allowed them.

For example, with this config:
```js
// astro.config.mjs
export default {
  vite: {
    preview: {
      allowedHosts: ['example.com']
    }
  }
}
```

Running `astro preview` and making a request to `example.com` returns 403 instead of 200.

## Expected Behavior

The preview server should merge the user's Vite configuration from `astro.config.mjs` into its Vite preview call, so that `vite.preview.allowedHosts` and other `vite.preview.*` settings are respected.

When merging configs, plugins must be excluded from the user config to avoid conflicts.

The server's `allowedHosts` setting (if explicitly set) should take precedence over the merged preview config's value. An explicit setting means either a boolean value or a non-empty array.
