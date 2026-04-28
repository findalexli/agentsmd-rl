# Inconsistent error handling in React Compiler pipeline

## Problem

The React Compiler's compilation pipeline uses a method called `env.tryRecord()` to wrap compiler pass invocations. This wrapper captures exceptions thrown by a pass so the pipeline can record the error and continue executing — accumulating multiple errors for the user to fix at once rather than stopping at the first failure. However, this defensive wrapping is applied inconsistently: the transform passes are wrapped in `tryRecord`, but the validation passes and inference passes are called directly without this protection. If one of these unprotected passes throws, compilation terminates immediately instead of being recorded and continuing.

In several of the compiler's validation modules, when a pass detects problems, it collects error details into a diagnostic object and then reports each error individually using `env.recordError()` inside a manual for-loop (`for (const detail of errors.details) { env.recordError(detail); }`). However, the compiler environment also exposes a batch method called `env.recordErrors()` that accepts an entire diagnostic object and records all errors at once — but it is not being used in these files.

In the HIR (High-level Intermediate Representation) lowering module, the error-handling code contains a redundant conditional: a ternary expression checks `detail instanceof CompilerDiagnostic` but both branches access the same `detail.category` property, making the `instanceof` check unnecessary. The `ErrorCategory` enum and its `Invariant` variant are used here to decide whether an error should be re-thrown.

In the main pipeline, there are two consecutive guard blocks that both check the flag `env.enableValidations`. The first guard wraps a single validation pass, then closes. Immediately after, a second guard opens to wrap additional validation calls including a check of `env.config.assertValidMutableRanges`.

## Expected Behavior

- All passes in the compilation pipeline should have consistent error-handling behavior: if any pass throws, the error should be captured so compilation can continue and report all issues, matching the approach already used for transform passes
- Validation modules that report collected errors should use the batch method `env.recordErrors()` on the compiler environment, passing the full diagnostic object instead of iterating errors with manual loops
- The redundant `instanceof CompilerDiagnostic` ternary in the HIR lowering code should be simplified by accessing `detail.category` directly
- Adjacent guard blocks that both check `env.enableValidations` should be merged into a single block

## Code Style Requirements

This project uses ESLint for JavaScript/TypeScript code style enforcement and TypeScript (`tsc --noEmit`) for type checking. All changes must satisfy both the linter and the type checker for the `babel-plugin-react-compiler` workspace.

## Finding the Relevant Code

- The compilation pipeline is in the entry point module under the babel-plugin-react-compiler source tree; it defines the `runWithEnvironment` function that orchestrates the order of compiler passes
- The HIR lowering module lives under the HIR (intermediate representation) source directory and contains the `lower` function that converts AST nodes
- The validation modules that check for derived computations in effects, preserved manual memoization, and source locations are under the Validation source directory
- The compiler's fault-tolerance documentation (in the root of the compiler directory) describes the `tryRecord` wrapping strategy and may help understand the intended error-handling design
