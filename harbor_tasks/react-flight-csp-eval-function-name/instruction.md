# Bug Report: React Flight CSP eval fallback function loses its name

## Problem

When using React Server Components (Flight) in an environment with a Content Security Policy that blocks `eval`/`new Function`, React falls back to creating a simple wrapper function. However, this fallback function does not preserve the original component or function name. Instead, it ends up with a generic name, which makes debugging significantly harder — stack traces and React DevTools show meaningless names instead of the actual component names that were serialized from the server.

## Expected Behavior

When React Flight creates fake functions for deserialized server references in CSP-restricted environments, each function should retain the correct display name matching the original server component or function name. Stack traces and developer tools should show meaningful names.

## Actual Behavior

In the CSP/eval fallback path within `createFakeFunction`, the generated wrapper function does not have its `name` property set to the intended name. The function ends up with whatever default name the runtime assigns, losing the server-side component name information. This degrades the developer experience when debugging server component trees in CSP-restricted environments.

## Files to Look At

- `packages/react-client/src/ReactFlightClient.js`
