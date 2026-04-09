# Update Deprecated Compose Feature Flags

## Problem

The Kotlin Compose Compiler Gradle plugin has several deprecated properties and feature flags that need their deprecation levels updated to ERROR (since they will be removed in Kotlin 2.5.0). Additionally, two feature flags (`OptimizeNonSkippingGroups` and `PausableComposition`) need deprecation annotations added.

The affected files are in `libraries/tools/kotlin-compose-compiler/`:

1. **ComposeCompilerGradlePluginExtension.kt** - Contains deprecated extension properties:
   - `generateFunctionKeyMetaClasses`
   - `enableIntrinsicRemember`
   - `enableNonSkippingGroupOptimization`
   - `enableStrongSkippingMode`
   - `stabilityConfigurationFile`

   These currently have simple `@Deprecated` annotations without a level (defaulting to WARNING). They need to be updated to `DeprecationLevel.ERROR` with specific messages mentioning "Will be removed in Kotlin 2.5.0".

2. **ComposeFeatureFlags.kt** - Contains feature flag constants:
   - `StrongSkipping` and `IntrinsicRemember` currently have deprecation without level
   - `OptimizeNonSkippingGroups` and `PausableComposition` have NO deprecation annotation yet

   The first two need `DeprecationLevel.ERROR`, the latter two need `DeprecationLevel.WARNING`.

3. **ComposeCompilerSubplugin.kt** - Uses the deprecated properties internally. The `@Suppress("DEPRECATION")` annotations need to be updated to `@Suppress("DEPRECATION_ERROR")` where appropriate, or include both when accessing both deprecated and non-deprecated items.

4. **ExtensionConfigurationTest.kt** - Test file that accesses deprecated APIs. Its `@Suppress` annotations need updating.

5. **ComposeIT.kt** - Integration test that uses the deprecated `stabilityConfigurationFile` API. This needs to be migrated to use `stabilityConfigurationFiles` (the plural/non-deprecated version).

## What Needs to Change

1. Update all `@Deprecated` annotations on the 5 extension properties to include:
   - A `message` parameter mentioning "Will be removed in Kotlin 2.5.0"
   - `level = DeprecationLevel.ERROR`

2. Update `StrongSkipping` and `IntrinsicRemember` feature flags to have `DeprecationLevel.ERROR`.

3. Add `@Deprecated` annotations to `OptimizeNonSkippingGroups` and `PausableComposition` with `DeprecationLevel.WARNING`.

4. Update `@Suppress("DEPRECATION")` to `@Suppress("DEPRECATION_ERROR")` where only ERROR-level deprecated items are accessed.

5. Update places accessing both deprecated and non-deprecated items to use `@Suppress("DEPRECATION_ERROR", "DEPRECATION")`.

6. Migrate the test code in ComposeIT.kt from `stabilityConfigurationFile.set(...)` to `stabilityConfigurationFiles.set(listOf(...))`.

## Notes

- The `featureFlags` property accesses both ERROR and WARNING level deprecated items, so it needs both suppressions.
- The extension test file has many `@Suppress("DEPRECATION")` annotations that should become `@Suppress("DEPRECATION_ERROR")` for tests accessing the ERROR-level deprecated properties.
- Tests for `OptimizeNonSkippingGroups` and `PausableComposition` should keep or add `@Suppress("DEPRECATION")` since those are only WARNING level.
