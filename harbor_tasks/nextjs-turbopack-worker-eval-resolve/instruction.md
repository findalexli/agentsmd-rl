# Bug: Turbopack fails to build when a library uses `new Worker()` with `{ eval: true }`

## Summary

When a Next.js application uses a library (e.g., jsPDF) that creates worker threads by passing inline JavaScript code to the `Worker` constructor with `{ eval: true }` as the second argument, Turbopack incorrectly treats the inline code string as a file path and attempts to resolve it as a module reference. This causes build failures because the inline JS code is obviously not a valid file path.

## Reproduction

1. Create a Next.js app route that imports `jspdf` and uses it to generate a PDF
2. Build with Turbopack (the default bundler)
3. Turbopack crashes trying to resolve the inline JS string passed to `new Worker(code, { eval: true })` as if it were a module path

## Relevant Code

The Worker constructor reference handling is in:
- `turbopack/crates/turbopack-ecmascript/src/references/mod.rs` — the `WellKnownFunctionKind::NodeWorkerConstructor` match arm processes `new Worker(...)` calls and creates module references for the first argument. It currently does not check whether `{ eval: true }` is passed as the second argument.

The request resolution logic is in:
- `turbopack/crates/turbopack-core/src/resolve/parse.rs` — the `Request` enum and its `append_path` method handle how partial resolution requests compose. The `DataUri` and `Uri` variants are grouped with `Dynamic` in the same match arm, but they should be handled separately since appending a path to a data URI or regular URI should yield `Dynamic` rather than staying as-is.

## Expected Behavior

When `new Worker(code, { eval: true })` is detected, Turbopack should recognize that the first argument is executable code (not a file path) and skip creating a worker module reference entirely. It should also emit appropriate warnings when the `eval` option is present but its value cannot be statically determined.

## Scope

The fix should handle:
- `eval: true` — skip worker reference creation
- `eval: false` — continue normal resolution (first arg is a path)
- Dynamic `eval` value — emit a warning about the dynamic option
- Non-static options object — emit a warning about the dynamic options argument
