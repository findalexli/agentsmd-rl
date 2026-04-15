# Task: Remove Deprecated Extras APIs

## Problem

The file `libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasProperty.kt` contains a section of deprecated extras APIs under a `DEPRECATED APIs` comment block. These APIs are annotated with `@Deprecated(level = DeprecationLevel.ERROR)` and their deprecation messages say "Scheduled for removal in Kotlin 2.3". The deprecated APIs include:

- Standalone functions: `extrasReadProperty`, `extrasFactoryProperty`, `extrasNullableLazyProperty`
- Interfaces: `ExtrasReadOnlyProperty`, `ExtrasFactoryProperty`, `NullableExtrasLazyProperty`
- Extension properties on `Extras.Key`: `readProperty`, `factoryProperty`, `nullableLazyProperty`

The `import java.util.*` statement is present only because the deprecated APIs use `Optional`.

The test file `libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasPropertyTest.kt` currently references these deprecated APIs and suppresses compilation errors with `@Suppress("DEPRECATION_ERROR")`.

## What to Do

1. Remove the entire `DEPRECATED APIs` comment section and all deprecated functions, extension properties, and interfaces from `ExtrasProperty.kt`.
2. Remove the `import java.util.*` from `ExtrasProperty.kt` since it is only needed by the deprecated code.
3. In `ExtrasPropertyTest.kt`, migrate all usages of deprecated APIs to their non-deprecated equivalents. Examine the remaining non-deprecated APIs in `ExtrasProperty.kt` to identify the correct replacements for each deprecated API used in the test.
4. Remove any test methods and associated helper code for the `nullableLazyProperty` API, since it has no non-deprecated replacement.
5. Remove the `@Suppress("DEPRECATION_ERROR")` annotation from the test class.

After your changes, the module's tests should still compile and pass.
