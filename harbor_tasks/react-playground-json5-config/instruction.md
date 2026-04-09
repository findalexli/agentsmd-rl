# XSS Vulnerability in Playground Config Parsing

## Problem

The React Compiler Playground's configuration editor has a cross-site scripting (XSS) vulnerability. The config override parsing in `compiler/apps/playground/lib/compilation.ts` uses `new Function()` to evaluate user-provided configuration text. This means any JavaScript code entered in the config editor will be executed, allowing arbitrary code execution in the user's browser.

The current config format requires a TypeScript-style wrapper (`import type { PluginOptions } from '...'` and `satisfies PluginOptions`), which is unnecessarily complex for what is essentially a JSON-like configuration object.

## Expected Behavior

Configuration parsing should use a safe JSON-like parser (such as JSON5) that supports comments and trailing commas but does **not** execute arbitrary JavaScript. The config format should be simplified to plain JSON5 objects (e.g., `{ compilationMode: "all" }`) without TypeScript wrappers.

The editor UI should reflect this change — using JSON language mode instead of TypeScript.

## Files to Look At

- `compiler/apps/playground/lib/compilation.ts` — config parsing logic (the `new Function()` call)
- `compiler/apps/playground/lib/defaultStore.ts` — default config template shown to users
- `compiler/apps/playground/components/Editor/ConfigEditor.tsx` — Monaco editor config for the config panel
- `compiler/apps/playground/package.json` — dependencies
