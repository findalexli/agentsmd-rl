# Update Deprecated Compose Feature Flags for Kotlin 2.5.0 Removal

## Problem

Several properties and feature flags in the Kotlin Compose Compiler Gradle plugin have inconsistent deprecation annotations. These items are scheduled for removal in Kotlin 2.5.0, but their current deprecation levels do not appropriately reflect this timeline or the severity of their impending removal.

### Extension Properties

In `ComposeCompilerGradlePluginExtension.kt`, the following five extension properties currently have `@Deprecated` annotations without a specified level (defaulting to WARNING), despite being scheduled for removal in Kotlin 2.5.0:
- `generateFunctionKeyMetaClasses`
- `enableIntrinsicRemember`
- `enableNonSkippingGroupOptimization`
- `enableStrongSkippingMode`
- `stabilityConfigurationFile`

Since these properties will be removed in Kotlin 2.5.0, their deprecation annotations should include "2.5.0" in the message and use an appropriate `DeprecationLevel` to signal the severity of the upcoming breaking change.

### Feature Flags

In `ComposeFeatureFlags.kt`, the deprecation states are inconsistent:
- `StrongSkipping` and `IntrinsicRemember` have `@Deprecated` without a level specified
- `OptimizeNonSkippingGroups` and `PausableComposition` have no deprecation annotation at all

Given that all four flags relate to features that should be enabled by default and will be removed in upcoming versions, they need appropriate deprecation annotations that distinguish between:
- Items being removed in Kotlin 2.5.0 (which should reference "2.5.0" in their deprecation messages)
- Items transitioning to a warning state (which should use `DeprecationLevel.WARNING`)

### Suppress Annotations

The internal usage sites in `ComposeCompilerSubplugin.kt` and test code in `ExtensionConfigurationTest.kt` currently use `@Suppress("DEPRECATION")` to access deprecated APIs. However, since deprecation levels distinguish between WARNING (still usable) and ERROR (compilation fails), the suppress annotations must align with the actual deprecation levels of the items being accessed:
- Code accessing items with `DeprecationLevel.ERROR` requires `"DEPRECATION_ERROR"` suppression
- Code accessing items with `DeprecationLevel.WARNING` requires `"DEPRECATION"` suppression
- Code accessing both levels requires both suppression values

### Test Code Migration

The integration test in `ComposeIT.kt` currently uses `stabilityConfigurationFile.set(...)` to configure stability settings. Since `stabilityConfigurationFile` is scheduled for removal in Kotlin 2.5.0, the test should use the replacement API `stabilityConfigurationFiles.set(...)` which accepts a list argument.

## Affected Files

1. **ComposeCompilerGradlePluginExtension.kt** - Extension properties in `libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/`
2. **ComposeFeatureFlags.kt** - Feature flag constants in the same directory
3. **ComposeCompilerSubplugin.kt** - Internal usage of deprecated APIs
4. **ExtensionConfigurationTest.kt** - Test code accessing deprecated APIs in `libraries/tools/kotlin-compose-compiler/src/functionalTest/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/`
5. **ComposeIT.kt** - Integration test in `libraries/tools/kotlin-gradle-plugin-integration-tests/src/test/kotlin/org/jetbrains/kotlin/gradle/`

## Expected Behavior After Fix

1. The five extension properties have `DeprecationLevel.ERROR` with deprecation messages containing "2.5.0"
2. The `StrongSkipping` and `IntrinsicRemember` feature flags have `DeprecationLevel.ERROR` with messages containing "2.5.0"
3. The `OptimizeNonSkippingGroups` and `PausableComposition` feature flags have `@Deprecated` with `DeprecationLevel.WARNING`
4. Suppress annotations in subplugin and test code distinguish between `DEPRECATION_ERROR` and `DEPRECATION` based on which deprecation level they access
5. `ComposeIT.kt` uses `stabilityConfigurationFiles.set(listOf(...))` instead of `stabilityConfigurationFile.set(...)`
