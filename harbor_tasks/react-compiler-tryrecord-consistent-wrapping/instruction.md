# Inconsistent error handling in React Compiler pipeline

## Problem

The React Compiler's compilation pipeline in `Pipeline.ts` has inconsistent error handling. Transform passes are wrapped in `env.tryRecord()` for defense-in-depth (so that if a pass throws, the error is recorded and compilation can continue to accumulate additional errors). However, validation passes and inference passes are called directly without this wrapping, meaning a thrown error would terminate the pipeline immediately instead of being recorded.

Additionally, several validation files (`ValidateNoDerivedComputationsInEffects.ts`, `ValidatePreservedManualMemoization.ts`, `ValidateSourceLocations.ts`) use a manual for-loop to record errors one by one (`for (const detail of errors.details) { env.recordError(detail); }`) instead of the simpler batch method `env.recordErrors(errors)`.

There is also a redundant conditional in `BuildHIR.ts` where an `instanceof CompilerDiagnostic` ternary evaluates to the same expression on both branches.

## Expected Behavior

- All validation and inference passes in the pipeline should be wrapped in `env.tryRecord()` for consistent error handling, matching the approach already used for transform passes
- Validation files should use the batch `recordErrors()` method instead of manual iteration
- The redundant ternary in BuildHIR should be simplified
- Two consecutive `if (env.enableValidations)` guard blocks that are adjacent should be merged into one

## Files to Look At

- `compiler/packages/babel-plugin-react-compiler/src/Entrypoint/Pipeline.ts` — main compilation pipeline with pass ordering
- `compiler/packages/babel-plugin-react-compiler/src/HIR/BuildHIR.ts` — HIR lowering with error handling
- `compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoDerivedComputationsInEffects.ts` — validation pass with error recording
- `compiler/packages/babel-plugin-react-compiler/src/Validation/ValidatePreservedManualMemoization.ts` — validation pass with error recording
- `compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateSourceLocations.ts` — validation pass with error recording
