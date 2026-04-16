# Task: Add asyncSequence(for:) Compatibility Function

## Problem Description

Users migrating from KMP-NativeCoroutines to Swift Export have code that calls `asyncSequence(for:)` to convert Kotlin flows to Swift AsyncSequences. However, in Swift Export, this function doesn't exist - only `asAsyncSequence()` is available. This forces users to manually update all call sites during migration.

## Your Task

Add a compatibility shim in `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift` that allows existing code using the `asyncSequence(for:)` calling pattern to continue working during the migration period.

## Requirements

1. **Support the legacy API pattern**: The shim should accept calls made using the `asyncSequence(for:)` pattern that KMP-NativeCoroutines provided, bridging them to work with Swift Export's `KotlinTypedFlow<T>` and `KotlinFlowSequence<T>` types.

2. **Guide migration with deprecation warnings**: The compatibility function should trigger deprecation warnings that guide users toward the new Swift Export API. The warning message must exactly state:
   ```
   Use `asAsyncSequence()` from Swift Export
   ```

3. **Documentation**: Include documentation comments before the function that explain:
   - This provides source compatibility with KMP-NativeCoroutines
   - The purpose is to ease migration to Swift Export
   - This is a temporary shim that should eventually be removed

4. **Preserve generic type safety**: The shim must properly handle the generic type parameter `T` used by `KotlinTypedFlow` and `KotlinFlowSequence` to maintain type safety.

## Expected Outcome

Users migrating from KMP-NativeCoroutines can temporarily keep their existing `asyncSequence(for: someFlow)` calls without immediate rewrites, while receiving clear compiler warnings that guide them toward the new `asAsyncSequence()` API.
