# Turbopack: createRequire(new URL) not resolving correctly

## Problem

Turbopack fails to resolve CommonJS modules when `createRequire` is called with a `new URL(...)` constructor pattern. When code uses:

```js
const require = createRequire(new URL('./sub/', import.meta.url))
const foo = require('./foo.js')
```

Turbopack emits a `Module not found: Can't resolve './sub/'` error. It incorrectly treats the URL-relative path as a module specifier rather than as a base directory for subsequent require() calls.

The simpler `createRequire(import.meta.url)` pattern works fine — only the `new URL(...)` variant is broken.

## Expected Behavior

Turbopack should resolve `require()` calls made through a `createRequire(new URL(relativePath, import.meta.url))` factory relative to the URL path, not the current module. This matches `@vercel/nft` behavior and Node.js semantics.

## Implementation Requirements

The fix must satisfy the following constraints. These are not hints about how to fix the bug — they are the factual requirements that the test oracle uses to verify correctness:

1. **Enum variant**: The WellKnownFunctionKind enum must have a variant that carries a boxed constant string. The exact syntax must be `RequireFrom(Box<ConstantString>)` and it must appear in the analyzer module.

2. **Handler logic**: In the references module, a match arm must:
   - Destructure `RequireFrom(rel)` to bind the relative path
   - Use `rel.as_str()` to obtain the string value
   - Chain `.parent().join(rel)` to construct the resolve origin

3. **URL pattern detection**: The value visitor must:
   - Match `JsValue::Url(rel, JsValueUrlKind::Relative)` pattern
   - Wrap the relative path in `RequireFrom(Box::new(rel.clone()))`

4. **Display implementation**: The Debug/Display impl for the enum variant must format the path as `createRequire('<path>')` and include a link to the Node.js `module.createRequire` documentation at `module.html#modulecreaterequirefilename`.

5. **Test cases**: The previously-disabled test cases in unit.rs must be active. Required case names (uncommented, starting with `#[case::`):
   - `module_create_require_destructure_namespace`
   - `module_create_require_destructure`
   - `module_create_require_ignore_other`
   - `module_create_require_named_import`
   - `module_create_require_named_require`
   - `module_create_require_no_mixed`

6. **Entry name mapping**: The unit test entry_name match must map the `module-create-require-*` test cases to `input.mjs` (not `input.js`). The format string must use the `{entry_name}` variable.

## Files to Investigate

The relevant source files are in the turbopack-ecmascript crate and the turbopack-tracing tests directory. The agent should explore the codebase to understand how WellKnownFunctionKind variants are defined and how require() calls are resolved.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
