# Fix HrefError Detail Types and Error Messages

The `@remix-run/route-pattern` package has bugs in how `HrefError` errors are thrown and formatted when generating hrefs from route patterns.

## Symptoms

### 1. Wrong error type for nameless wildcards

When calling `href()` on a route pattern that contains a nameless wildcard (`*` without a name, e.g., `://*.example.com/path` or `/files/*`), the error thrown has type `missing-params`. This is misleading because a nameless wildcard isn't a parameter the user should be providing — the `*` matches but does not capture. The error type `nameless-wildcard` (which already exists in the `HrefErrorDetails` union type) should be used for this case instead.

### 2. Missing params error message leaks internal representations

When required pathname or hostname parameters are missing, the `HrefError` message currently shows internal variant representations. For example, for a pattern like `https://example.com/:id` called with no params, the error shows something like:

```
missing params

Pattern: https://example.com/:id
Params: {}
Pathname variants:
  - {:id} (missing: id)
```

This `Pathname variants:` section leaks internal formatting and is confusing. The error message should instead simply list the specific missing parameter names in a clear format like:

```
missing param(s): 'id'

Pattern: https://example.com/:id
Params: {}
```

Key differences in the fixed format:
- The message starts with `missing param(s):` (note the colon after the closing parenthesis)
- Each missing parameter name is individually quoted with single quotes (e.g., `'id'`)
- The `Pathname variants:` (or `Hostname variants:`) section is entirely removed

### 3. Inconsistent formatting for missing-search-params errors

The `missing-search-params` error message also needs its format updated for consistency. Currently it says:

```
missing required search param(s) 'q'
```

It should use a colon after the closing parenthesis:

```
missing required search param(s): 'q'
```

And parameter names should be individually quoted (e.g., `'q'`, `'sort'` rather than `q, sort`).

## Expected Behavior

- Route patterns with nameless wildcards (`*` without a name) should throw errors with type `nameless-wildcard`, not `missing-params`
- Missing params error messages should use the format `missing param(s):` (with colon) and list each missing param individually quoted
- Missing search params error messages should use the format `missing required search param(s):` (with colon) and list each param individually quoted
- The `Pathname variants:` and `Hostname variants:` internal representations should not appear in error messages
- Valid `href()` calls with all required params provided should continue to work correctly
- The full test suite for the route-pattern package should pass after changes are made

## Code Style Requirements

- Follow Prettier formatting (printWidth: 100, no semicolons, single quotes, spaces not tabs)
- Use `import type { X }` for type-only imports
- Use regular function declarations, not arrow functions for top-level functions
- Do not add inline comments unless the code is surprising or non-obvious
