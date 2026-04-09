# React Compiler Playground: Config Parsing Security Vulnerability

## Problem

The React Compiler playground parses user-provided compiler configuration using `new Function(...)`, which is a cross-site scripting (XSS) vulnerability. Arbitrary JavaScript code supplied as config text will execute in the playground context.

The config parsing is in the playground's compilation pipeline. When a user enters config overrides in the editor, the code uses `new Function()` to evaluate the config string as JavaScript, which means malicious config values (e.g., IIFEs, `eval()` calls, `fetch()` to exfiltrate data) would execute without restriction.

Additionally, the default config template uses TypeScript syntax (`import type`, `satisfies PluginOptions`) that is unnecessarily complex for what should be a simple JSON-like config object.

## Expected Behavior

Config parsing should use a safe parser (like JSON5) that only accepts data — not arbitrary JavaScript expressions. The default config should be a simple JSON5 object without TypeScript-specific syntax.

## Files to Look At

- `compiler/apps/playground/lib/compilation.ts` — contains the config parsing logic in the `parseOptions` function
- `compiler/apps/playground/lib/defaultStore.ts` — contains the default config template
- `compiler/apps/playground/components/Editor/ConfigEditor.tsx` — the Monaco editor config panel
- `compiler/apps/playground/package.json` — dependencies
