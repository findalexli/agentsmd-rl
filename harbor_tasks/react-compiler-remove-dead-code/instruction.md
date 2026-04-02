# Bug Report: React Compiler contains dead code and unused abstractions

## Problem

The React Compiler codebase has accumulated dead code that increases maintenance burden and confuses contributors. There is an unused `ValidateNoUntransformedReferences` post-compilation step that is called but serves no purpose after recent refactors. The `compileProgram` function returns metadata (including retry error tracking) that no caller actually uses. Additionally, the `ProgramContext` class carries a `retryErrors` field and associated type exports that are never read. There is also a stale `'client-no-memo'` output mode option still defined in the schema despite being unsupported.

## Expected Behavior

The codebase should contain only live code paths. Functions should not return values that are always ignored. Types and fields that are not referenced anywhere should not exist. Configuration schema options should reflect only currently supported modes.

## Actual Behavior

Dead code remains throughout several entrypoint modules: an unused validation pass is invoked, return values are computed but discarded, a type alias and class field exist with no consumers, and an obsolete compiler output mode clutters the options schema.

## Files to Look At

- `src/Babel/BabelPlugin.ts`
- `src/Entrypoint/Imports.ts`
- `src/Entrypoint/Options.ts`
- `src/Entrypoint/Program.ts`
- `src/Entrypoint/ValidateNoUntransformedReferences.ts`
- `src/HIR/Environment.ts`
