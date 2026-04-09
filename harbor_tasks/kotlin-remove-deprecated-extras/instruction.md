# Task: Remove Deprecated Extras APIs

## Problem

The file `libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasProperty.kt` contains a section of deprecated extras APIs that are scheduled for removal. These APIs include extension properties and functions (`readProperty`, `factoryProperty`, `nullableLazyProperty`), standalone functions (`extrasReadProperty`, `extrasFactoryProperty`, `extrasNullableLazyProperty`), and interfaces (`ExtrasReadOnlyProperty`, `ExtrasFactoryProperty`, `NullableExtrasLazyProperty`). They are all marked with `@Deprecated(level = DeprecationLevel.ERROR)` and are no longer intended for use.

The test file `libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasPropertyTest.kt` currently references these deprecated APIs and uses `@Suppress("DEPRECATION_ERROR")` to suppress compilation errors.

## What to Do

1. Remove all deprecated functions, extension properties, and interfaces from `ExtrasProperty.kt` (everything under the `DEPRECATED APIs` comment section at the end of the file).
2. Remove the now-unnecessary `import java.util.*` from `ExtrasProperty.kt`.
3. In `ExtrasPropertyTest.kt`, migrate usages of deprecated APIs to their non-deprecated equivalents:
   - `keyA.readProperty` -> `keyA.readWriteProperty`
   - `keyB.readProperty` -> `keyB.readWriteProperty`
   - `keyList.factoryProperty { ... }` -> `keyList.lazyProperty { ... }`
4. Remove the test for `lazyNullableProperty` and its associated helper properties (`lazyNullString`, `lazyNullableString`, `lazyNullStringInvocations`, `lazyNullableStringInvocations`) since that API has no non-deprecated replacement.
5. Remove `@Suppress("DEPRECATION_ERROR")` from the test class since there are no longer any deprecated API usages.

After your changes, the module's tests should still compile and pass.
