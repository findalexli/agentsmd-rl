# React Compiler Playground: Config Parsing Security Vulnerability

## Problem

The React Compiler playground parses user-provided compiler configuration using `new Function(...)`, which is a cross-site scripting (XSS) vulnerability. Arbitrary JavaScript code supplied as config text will execute in the playground context.

The config parsing is in the playground's compilation pipeline. When a user enters config overrides in the editor, the code uses `new Function()` to evaluate the config string as JavaScript, which means malicious config values (e.g., IIFEs, `eval()` calls, `fetch()` to exfiltrate data) would execute without restriction.

Additionally, the default config template uses TypeScript syntax (`import type`, `satisfies PluginOptions`) that is unnecessarily complex for what should be a simple JSON-like config object.

## Expected Behavior

Config parsing should use a safe parser (like JSON5) that only accepts data — not arbitrary JavaScript expressions. The default config should be a simple JSON5 object without TypeScript-specific syntax.

The fix must satisfy these specific requirements:

1. **Function name**: The config override parsing function must be exported as `parseConfigOverrides` (not `parseOptions`)
2. **Config file path**: The config editor must reference a file named `config.json5` (not `config.ts`)
3. **Default config format**: The default config in defaultStore.ts must use the syntax `export const defaultConfig = \`` template literal, and must not contain TypeScript-specific syntax (`import type`, `satisfies PluginOptions`)
4. **Test file**: A unit test file must exist at `compiler/apps/playground/__tests__/parseConfigOverrides.test.mjs`
5. **Dependency**: The `json5` package must be listed as a dependency in `compiler/apps/playground/package.json`

## Files to Look At

- `compiler/apps/playground/lib/compilation.ts` — contains the config parsing logic in the `parseOptions` function
- `compiler/apps/playground/lib/defaultStore.ts` — contains the default config template
- `compiler/apps/playground/components/Editor/ConfigEditor.tsx` — the Monaco editor config panel
- `compiler/apps/playground/package.json` — dependencies
