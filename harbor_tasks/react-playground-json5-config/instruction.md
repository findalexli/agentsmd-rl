# XSS Vulnerability in Playground Config Parsing

## Problem

The React Compiler Playground's configuration editor has a cross-site scripting (XSS) vulnerability. The config override parsing uses `new Function()` to evaluate user-provided configuration text. This means any JavaScript code entered in the config editor will be executed, allowing arbitrary code execution in the user's browser.

The current config format requires a TypeScript-style wrapper (`import type { PluginOptions } from '...'` and `satisfies PluginOptions`), which is unnecessarily complex for what is essentially a JSON-like configuration object.

## Expected Behavior

Configuration parsing should use a safe JSON-like parser that supports comments and trailing commas but does **not** execute arbitrary JavaScript. The config format should be simplified to plain objects (e.g., `{ compilationMode: "all" }`) without TypeScript wrappers.

The editor UI should use JSON language mode instead of TypeScript.

## Requirements

The fix must satisfy all of the following:

1. **Safe parsing**: Replace any `new Function()`-based config parsing with a library that parses JSON-like data safely. The library must:
   - Support comments (both `//` and `/* */`)
   - Support trailing commas
   - Reject arbitrary JavaScript expressions (IIFEs, `eval()`, template literals, etc.)

2. **Exported function**: The config parsing logic must be exported as a named function so it can be unit tested via `node --test`. The test file must be named `parseConfigOverrides.test.mjs` and located in the playground's `__tests__` directory.

3. **Simplified config format**: Default config and all config editor inputs must use plain objects without TypeScript type wrappers (`import type` statements or `satisfies` keywords).

4. **Editor mode**: The Monaco editor for config must use JSON language mode, not TypeScript mode.

5. **Dependencies**: Any required parsing library must be added as a dependency in the playground package.

## Verification

The solution will be verified by:
- Running `node --test` on the config parsing test suite
- Confirming the parsing library rejects malicious inputs (code injection attempts)
- Confirming the config editor uses JSON language mode