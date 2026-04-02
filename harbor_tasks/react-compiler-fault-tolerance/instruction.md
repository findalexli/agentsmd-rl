# Bug Report: React Compiler stops after first error instead of reporting all errors

## Problem

The React Compiler's fault tolerance mode is supposed to report all independent compilation errors found in a component, allowing developers to fix multiple issues at once. However, there is no test coverage verifying that the compiler actually reports multiple errors when a component contains more than one independent violation.

Without a fixture that exercises this behavior, regressions could silently cause the compiler to bail out after the first error, forcing developers into a frustrating fix-one-recompile-fix-another cycle.

## Expected Behavior

When a component contains multiple independent errors (e.g., reading a ref during render *and* mutating a frozen value like props), the compiler should report all errors together in a single diagnostic output, prefixed with a count like "Found 2 errors."

## Actual Behavior

There is no test fixture validating multi-error fault tolerance reporting. The compiler's behavior for this scenario is untested, meaning it could regress to stopping at the first error without anyone noticing.

## Files to Look At

- `compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/` — a new error fixture and its expected output are needed here
