# Fix webpack node: protocol handling in @storybook/nextjs

## Problem

When using newer Next.js versions with Storybook, the webpack build fails with an `UnhandledSchemeError` for module requests like `node:stream`, `node:fs`, `node:path`, `node:util`, `node:buffer`. This occurs because newer Next.js versions import Node.js builtins using the `node:` protocol prefix (e.g., `import stream from 'node:stream'`), but webpack's polyfill and fallback handling only applies once the request is normalized (no prefix).

## Symptoms

- Build fails with: `UnhandledSchemeError: Reading from "node:stream" is not handled by plugins`
- Dev server fails to start with similar scheme errors
- TypeScript compilation via `yarn nx compile nextjs` fails
- TypeScript type checking via `yarn nx check nextjs` fails

## What Must Be True After the Fix

When the fix is complete, the following must all be satisfied:

1. **The `webpack` package must be imported** so that webpack's NormalModuleReplacementPlugin can be instantiated

2. **The node: prefix must be stripped from module requests** before webpack's polyfill handling. A pattern-matching approach is needed to match requests like `node:stream` and transform them to `stream`.

3. **A NormalModuleReplacementPlugin must be configured** to intercept requests matching the node: prefix pattern and strip the prefix from `resource.request`

4. **Existing resolve.fallback configuration must be preserved** when adding fallback entries

5. **Existing plugins must be preserved** when building the plugins array

6. **The node:-stripping plugin must come before NodePolyfillPlugin** in the plugins array, so the prefix is stripped before polyfill resolution

7. **TypeScript compilation must pass** for the nextjs package via `yarn nx compile nextjs`

8. **TypeScript type checking must pass** for the nextjs package via `yarn nx check nextjs`

## Affected Area

The fix is in the webpack configuration handling Node.js polyfills within the Next.js framework package. Look for where `NodePolyfillPlugin` is configured and where webpack `resolve.fallback` settings are managed.

## Testing

Validate your changes by running:
- `yarn nx compile nextjs`
- `yarn nx check nextjs`