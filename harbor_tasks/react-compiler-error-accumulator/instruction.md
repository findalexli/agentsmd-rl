# Error Accumulation Infrastructure for React Compiler

The React Compiler's `Environment` class manages the compilation state for individual React functions. Currently, when the compiler encounters errors during various analysis passes, the only option is to throw immediately, which halts compilation and prevents reporting multiple errors at once.

Your task is to add error accumulation infrastructure to the `Environment` class so that compiler passes can record errors without interrupting the pipeline.

## Background

The `Environment` class is defined in `src/HIR/Environment.ts`. The existing `CompilerError` class (from `src/CompilerError.ts`) provides utilities for creating and managing compilation errors, including:
- `CompilerDiagnostic` - represents a diagnostic message
- `CompilerErrorDetail` - detailed error information  
- `ErrorCategory` - categorizes errors (including `Invariant` for internal bugs)
- `hasAnyErrors()` - method on `CompilerError` to check if errors exist
- `pushDiagnostic()` / `pushErrorDetail()` - methods to add errors

## Requirements

Add the following to the `Environment` class:

1. A private field to accumulate compilation errors, initialized to a fresh `CompilerError` instance

2. `recordError()` - a method that takes a single diagnostic or error detail and:
   - If the error is an `Invariant` category, throws it immediately (invariants represent internal bugs)
   - Otherwise, accumulates the error in the private field

3. `recordErrors()` - a method that takes a `CompilerError` and records all its diagnostics

4. `hasErrors()` - a method that returns true if any errors have been accumulated

5. `aggregateErrors()` - a method that returns the accumulated `CompilerError`

6. `tryRecord()` - a helper that wraps a callback. If the callback throws a `CompilerError` that is NOT an invariant, record it. Re-throw non-`CompilerError` exceptions and any errors containing invariants.

Don't forget to import the necessary types from `CompilerError.ts`.

## Files to Edit

- `src/HIR/Environment.ts` - Add the error accumulation methods

## Testing

After implementing, verify:
- TypeScript compiles without errors
- The new methods follow the existing code style
- Error handling correctly distinguishes between recoverable errors and invariants
