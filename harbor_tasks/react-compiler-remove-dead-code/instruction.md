# Bug Report: React Compiler contains dead code and unused abstractions

## Problem

The React Compiler codebase has accumulated dead code that increases maintenance burden and confuses contributors. There is an unused `ValidateNoUntransformedReferences` post-compilation step that is called but serves no purpose after recent refactors. The `compileProgram` function returns metadata (including retry error tracking) that no caller actually uses. Additionally, the `ProgramContext` class carries a `retryErrors` field and associated type exports that are never read. There is also a stale `'client-no-memo'` output mode option still defined in the schema despite being unsupported.

## Expected Behavior

The codebase should contain only live code paths. Functions should not return values that are always ignored. Types and fields that are not referenced anywhere should not exist. Configuration schema options should reflect only currently supported modes.

## Actual Behavior

Dead code remains throughout several entrypoint modules: an unused validation pass is invoked, return values are computed but discarded, a type alias and class field exist with no consumers, and an obsolete compiler output mode clutters the options schema.

## Problem

The React Compiler codebase has accumulated dead code that increases maintenance burden and confuses contributors. Post-compilation validation steps exist that no longer serve a purpose after recent refactors. Functions compute and return values that no caller actually uses. Classes carry fields and type exports that have no consumers. Configuration schema options include obsolete modes that are no longer supported.

## Expected Behavior

The codebase should contain only live code paths. Functions should not return values that are always ignored. Types and fields that are not referenced anywhere should not exist. Configuration schema options should reflect only currently supported modes.

## Actual Behavior

Dead code remains throughout several entrypoint modules: unused validation passes are invoked, return values are computed but discarded, class members and type exports exist with no consumers, and obsolete compiler output modes clutter the options schema.

## Scope

Focus your search on the compiler's entrypoint and Babel plugin code, as well as the HIR environment configuration. Look for code paths that compute values no caller uses, type definitions with no references, and configuration enums that include deprecated modes.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
