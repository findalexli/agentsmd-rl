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

- `compiler/apps/playground/lib/compilation.ts` — config parsing logic
- `compiler/apps/playground/lib/defaultStore.ts` — default config template
- `compiler/apps/playground/components/Editor/ConfigEditor.tsx` — config editor panel
- `compiler/apps/playground/package.json` — dependencies

## Security Note

The fix must ensure that patterns like IIFEs, `eval()` calls, and function constructors in config values do NOT execute.