# Swift Export: Fix Coroutines Import Generation

## Problem

The Swift Export feature generates Kotlin bridge code for interoperability with Swift. When generating imports for coroutines functionality, extension functions like `kotlinx.coroutines.launch` are not being imported correctly with their safe import names.

This causes naming conflicts when the generated code tries to use these extension functions.

## What You Need to Do

Fix the `SirBridgeProviderImpl.kt` file in the native/swift/sir-providers module to:

1. Generate explicit coroutines imports (CancellationException, CoroutineScope, CoroutineStart, Dispatchers) instead of using wildcard imports
2. Import the `kotlinx.coroutines.launch` extension function with a safe import name alias (`kotlinx_coroutines_launch`)
3. Use the aliased name when generating bridge code that calls the launch function
4. Create a reusable `FqName.safeImportName` extension property for computing safe import names

## Files to Modify

- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt`

## Key Areas

Look at the `additionalImports()` function and the generated bridge code in `createKotlinBridge()`. The issue is that extension functions need special handling for their import names to avoid conflicts.

The safe import name format replaces dots with underscores and existing underscores with double underscores. For example:
- `kotlinx.coroutines.launch` → `kotlinx_coroutines_launch`

## Expected Outcome

After your fix:
- The `additionalImports()` function should return explicit coroutine imports plus the aliased launch import
- Generated bridge code should call `.kotlinx_coroutines_launch()` instead of `.launch()`
- The golden result test files should be updated to reflect these changes

## Context

This is part of the Swift Export standalone integration tests for coroutines. The generated bridge code is used to enable Swift interop with Kotlin suspend functions.
