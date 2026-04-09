# Swift Export: Export KotlinCoroutineSupport module

## Problem

When the Kotlin Swift Export Standalone tool generates Swift code for modules that use coroutines, the `KotlinCoroutineSupport` module is imported with a regular `import` statement. However, this module should be **exported** so that consumers of the generated Swift code can access the coroutine support types without needing their own import.

The symptom: Generated Swift files contain:
```swift
import KotlinCoroutineSupport
```

But they should contain:
```swift
@_exported import KotlinCoroutineSupport
```

## Files to Modify

The main source file to modify is:
- `native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt`

This file contains the logic for creating Swift import statements during the translation process. Look for where `SirImport` is constructed with the coroutine support module name.

## Test Data (Golden Results)

The PR also updates the expected output files ("golden results") in:
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/closures/golden_result/main/main.swift`
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/KotlinxCoroutinesCore/KotlinxCoroutinesCore.swift`
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/flow_overrides/flow_overrides.swift`
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift`
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutinesWithPackageFlattening/golden_result/main/main.swift`

Each of these files should be updated to use `@_exported import KotlinCoroutineSupport` instead of `import KotlinCoroutineSupport`.

## Context

The `@_exported` attribute in Swift makes the imported module's public interface available to any code that imports the current module. This is important for the generated Swift code because users of the exported module should be able to access coroutine support types without explicit imports.

In the source code, `SirImport` likely has different modes or an `exported` parameter that controls whether the `@_exported` attribute is used.
