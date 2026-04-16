# Fix webpack node: protocol handling in @storybook/nextjs

## Problem

When using newer Next.js versions with Storybook, the webpack build fails with an `UnhandledSchemeError` for module requests like `node:stream`, `node:fs`, `node:path`, `node:util`, `node:buffer`. This occurs because newer Next.js versions import Node.js builtins using the `node:` protocol prefix (e.g., `import stream from 'node:stream'`), but the current webpack configuration doesn't handle these requests before polyfill handling kicks in.

## Symptoms

- Build fails with: `UnhandledSchemeError: Reading from "node:stream" is not handled by plugins`
- Dev server fails to start with similar scheme errors
- TypeScript compilation via `yarn nx compile nextjs` fails
- TypeScript type checking via `yarn nx check nextjs` fails

## What Must Be True After the Fix

When the fix is complete, the codebase must satisfy all of these conditions:

1. **A regex constant named `NODE_PROTOCOL_REGEX`** must be defined with the exact pattern `/^node:/`

2. **The `webpack` package must be imported** with the exact syntax `import webpack from 'webpack'`

3. **`webpack.NormalModuleReplacementPlugin` must be used** with `NODE_PROTOCOL_REGEX` as its first argument, and the callback must replace requests using `resource.request.replace(NODE_PROTOCOL_REGEX, '')`

4. **Existing fallback configuration must be preserved** using the exact spread syntax `...baseConfig.resolve?.fallback` when adding fallbacks

5. **Existing plugins must be preserved** using the exact spread syntax `...(baseConfig.plugins || [])` when constructing the plugins array

6. **`NormalModuleReplacementPlugin` must come before `NodePolyfillPlugin`** in the plugin order (so the prefix is stripped before polyfill resolution)

7. **TypeScript compilation must pass** for the nextjs package via `yarn nx compile nextjs`

8. **TypeScript type checking must pass** for the nextjs package via `yarn nx check nextjs`

## Affected Area

The fix involves the webpack configuration handling Node.js polyfills within the Next.js framework package. Look for code that configures `NodePolyfillPlugin` and manages webpack `resolve.fallback` settings.

## Testing

Validate your changes by running:
- `yarn nx compile nextjs`
- `yarn nx check nextjs`
