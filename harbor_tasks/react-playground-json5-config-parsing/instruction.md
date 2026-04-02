# XSS Vulnerability in React Compiler Playground Config Parsing

## Problem

The React Compiler Playground's configuration editor allows users to customize compiler options. However, the config parsing implementation uses `new Function()` to evaluate user-provided configuration strings, which is a **cross-site scripting (XSS) vulnerability**. Any arbitrary JavaScript expression entered in the config editor is executed in the user's browser context.

For example, a crafted playground URL could include a config like `(function(){ document.cookie; ... })()` which would be evaluated by `new Function()`.

The current config format also requires a TypeScript wrapper (`import type { PluginOptions } from '...'` and `satisfies PluginOptions`) around a plain object, which is unnecessarily complex for what is essentially a key-value configuration.

## Expected Behavior

Config parsing should use a safe data-only parser that:
- Accepts configuration objects with unquoted keys, comments, and trailing commas (JSON5 syntax)
- Rejects any JavaScript expressions, function calls, or code execution attempts
- Uses a simple object format `{ key: "value" }` without TypeScript wrappers

The config editor should reflect the new format (not TypeScript).

## Files to Look At

- `compiler/apps/playground/lib/compilation.ts` — contains the config parsing logic that uses `new Function()`
- `compiler/apps/playground/lib/defaultStore.ts` — defines the default config template shown to users
- `compiler/apps/playground/components/Editor/ConfigEditor.tsx` — Monaco editor configuration for the config panel
- `compiler/apps/playground/package.json` — playground dependencies
