# Task: Update Deprecated Compose Feature Flags

## Problem

The Compose compiler Gradle plugin has several deprecated properties and feature flags that are scheduled for removal in Kotlin 2.5.0. Currently, the deprecation annotations don't properly indicate this removal timeline or use appropriate deprecation levels. Additionally, code that accesses these deprecated APIs may not have the correct `@Suppress` annotations to handle the updated deprecation levels.

## Files Context

The following files in the Kotlin Compose compiler plugin contain deprecated APIs and their usages:

- `libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerGradlePluginExtension.kt`
- `libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeFeatureFlags.kt`
- `libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerSubplugin.kt`
- `libraries/tools/kotlin-compose-compiler/src/functionalTest/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ExtensionConfigurationTest.kt`

## Current State

The following properties and feature flags currently have basic `@Deprecated` annotations without explicit deprecation levels or version information:

**In ComposeCompilerGradlePluginExtension.kt:**
- `generateFunctionKeyMetaClasses`
- `enableIntrinsicRemember`
- `enableNonSkippingGroupOptimization`
- `enableStrongSkippingMode`
- `stabilityConfigurationFile`

**In ComposeFeatureFlags.kt:**
- `ComposeFeatureFlag.StrongSkipping`
- `ComposeFeatureFlag.IntrinsicRemember`
- `ComposeFeatureFlag.OptimizeNonSkippingGroups`
- `ComposeFeatureFlag.PausableComposition`

## Desired State

1. **Deprecation annotations must include version information**: All deprecation messages for APIs scheduled for removal in Kotlin 2.5.0 should explicitly mention "Kotlin 2.5.0"

2. **Deprecation levels must reflect removal timeline**:
   - APIs scheduled for removal in Kotlin 2.5.0 should use `DeprecationLevel.ERROR` to indicate they will be removed soon
   - Some feature flags should use `DeprecationLevel.WARNING` where appropriate for the deprecation stage

3. **@Suppress annotations must be updated**: Code accessing deprecated APIs with `DeprecationLevel.ERROR` should use `@Suppress("DEPRECATION_ERROR", ...)` instead of just `@Suppress("DEPRECATION", ...)` to allow compilation

4. **Annotation format**: Deprecation annotations should use the named parameter format with explicit `message` and `level` parameters rather than the simple single-line form

## Requirements

- All 5 properties in `ComposeCompilerGradlePluginExtension.kt` should have deprecation messages mentioning "Kotlin 2.5.0"
- The feature flags `StrongSkipping` and `IntrinsicRemember` should have deprecation messages mentioning "Kotlin 2.5.0"
- The `@Suppress` annotation for the `featureFlags` property in the extension file should include "DEPRECATION_ERROR"
- The subplugin file should have multiple `@Suppress` annotations using "DEPRECATION_ERROR" for code accessing deprecated APIs
- All deprecated properties should use `DeprecationLevel.ERROR` except where `WARNING` is more appropriate
