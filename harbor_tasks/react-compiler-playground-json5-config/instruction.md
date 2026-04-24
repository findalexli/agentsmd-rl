# React Compiler Playground: Config Parsing Security Vulnerability

## Problem

The React Compiler playground's config editor accepts user input that is evaluated as executable JavaScript. This allows arbitrary code execution in the playground context, creating a cross-site scripting (XSS) vulnerability. A malicious config value could exfiltrate data or perform actions on behalf of the user.

Additionally, the default config template uses TypeScript-specific syntax that unnecessarily complicates what should be a simple data-only format.

## Expected Behavior

Config parsing must reject executable code (IIFEs, eval calls, function constructors, etc.) while accepting a data format that supports:
- Comments (both `//` line comments and `/* */` block comments)
- Trailing commas
- Unquoted keys

The playground should include a unit test suite for the config parsing logic.

## Files to Examine

- `compiler/apps/playground/lib/compilation.ts` — config parsing logic, specifically the `parseConfigOverrides` function which must be exported
- `compiler/apps/playground/lib/defaultStore.ts` — default config template (uses TypeScript `satisfies` syntax which must be removed)
- `compiler/apps/playground/components/Editor/ConfigEditor.tsx` — config editor panel (currently uses TypeScript language mode with path `config.ts`; must be changed to JSON language mode with path `config.json5`)
- `compiler/apps/playground/package.json` — dependencies (must add a JSON-with-comments parsing library)
- `compiler/apps/playground/__tests__/parseConfigOverrides.test.mjs` — unit test file that should exist and pass

## Security Note

The fix must ensure that patterns like IIFEs, `eval()` calls, and function constructors in config values do NOT execute.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
