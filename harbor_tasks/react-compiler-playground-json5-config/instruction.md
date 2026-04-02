# Security: XSS Vulnerability in React Compiler Playground Config Parsing

The React Compiler Playground at `compiler/apps/playground/` currently parses user-provided configuration using `new Function()`, which is a cross-site scripting (XSS) vulnerability. Arbitrary JavaScript code can be executed through the config editor.

## Problem

The `parseOptions` function in `lib/compilation.ts` uses `new Function()` to evaluate the config string from the editor:

```javascript
configOverrideOptions = new Function(`return (${configString})`)();
```

This allows malicious JavaScript like `(function(){ document.title = "hacked"; return {}; })()` to execute when a user loads a playground URL with a crafted config.

## Your Task

1. Replace the unsafe `new Function()` parsing with a safe JSON5 parser
2. Add the `json5` dependency to `package.json`
3. Create a `parseConfigOverrides` function that:
   - Returns an empty object for empty/whitespace-only strings
   - Uses `JSON5.parse()` to safely parse the config
   - JSON5 supports comments and trailing commas (unlike strict JSON)
4. Update `lib/defaultStore.ts` to use plain JSON5 syntax for the default config (remove TypeScript type annotations and imports)

## Requirements

- The new implementation must reject XSS payloads (IIFE, eval calls, function calls, variable references)
- The playground should continue to accept configs with single-line comments (`//`) and trailing commas
- The existing config editor behavior should remain unchanged for valid configs

## Files to Examine

- `lib/compilation.ts` - Contains the vulnerable parsing logic
- `lib/defaultStore.ts` - Contains the default config template
- `package.json` - Needs the json5 dependency
