# Task: Add asyncSequence(for:) Compatibility Function

## Problem

Users migrating from KMP-NativeCoroutines to Swift Export need source compatibility for their existing code that uses the `asyncSequence(for:)` function. Currently, Swift Export provides `asAsyncSequence()` method on flows, but KMP-NativeCoroutines users have code that calls `asyncSequence(for: someFlow)`.

## Requirements

Add a compatibility function to `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift` that:

1. Provides a top-level function `asyncSequence(for:)` that wraps the existing `asAsyncSequence()` method
2. Takes a `KotlinTypedFlow<T>` parameter and returns `KotlinFlowSequence<T>`
3. Is marked as deprecated with a message directing users to use `asAsyncSequence()` instead
4. Includes documentation explaining this is for KMP-NativeCoroutines migration compatibility

## Context

- The file `KotlinCoroutineSupport.swift` contains Swift-side support for Kotlin coroutines
- The existing `asAsyncSequence()` method is available on `KotlinTypedFlow` instances
- The compatibility function should be a simple wrapper that delegates to `asAsyncSequence()`

## Notes

- This function is intentionally deprecated immediately upon addition - it's purely for migration support
- The deprecation message should guide users to migrate to `asAsyncSequence()`
- Follow existing code style in the file
