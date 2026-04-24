# Fix XSS Vulnerability in Playground Config Parsing

## Problem

The React Compiler Playground's configuration editor has a cross-site scripting (XSS) vulnerability. The config override parsing currently uses `new Function()` to evaluate user-provided configuration text, which allows arbitrary JavaScript code to be executed in the user's browser.

The existing config format also requires TypeScript-style wrappers (`import type { PluginOptions }` statements and `satisfies PluginOptions` keywords), which are unnecessarily complex for what should be a plain configuration object.

## Symptom

When a user enters JavaScript code in the config editor — such as `({ compilationMode: eval("all") })` — the current parser executes it directly rather than rejecting it as invalid syntax. This allows code injection attacks via the config override field.

## Requirements

Your fix must satisfy all of the following:

1. **Safe parsing**: Replace any `new Function()`-based config parsing with a safe alternative. The replacement must:
   - Support single-line comments (`//`)
   - Support multi-line comments (`/* */`)
   - Support trailing commas
   - Reject arbitrary JavaScript expressions (IIFEs, `eval()`, template literals, variable references, function calls, constructor calls)

2. **Testable export**: The config parsing logic must be accessible to Node.js test runners via a named exported function. A test file named `parseConfigOverrides.test.mjs` must exist in the playground's `__tests__` directory and pass `node --test`.

3. **Simplified config format**: The default config and all config editor inputs must use plain objects without TypeScript type wrappers. Specifically:
   - No `import type { PluginOptions }` statements
   - No `satisfies PluginOptions` keywords

4. **Editor language**: The Monaco editor instance used for config editing must use a JSON-compatible language mode, not TypeScript.

5. **Dependency**: Any parsing library required for safe config handling must be added as a dependency in the playground's `package.json`.

## Verification

Your solution will be verified by:
- Running `node --test` on the config parsing test suite — it must pass
- Confirming the parser rejects code injection attempts (IIFEs, eval expressions, template literals, etc.)
- Confirming no `new Function()` calls remain in the config parsing path
- Confirming the config editor uses a JSON-compatible language mode
- Running the existing repository test suite to ensure no regressions

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
