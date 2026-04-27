# Task: Remove Deprecated Extras APIs

## Problem

The `kotlin-tooling-core` module contains a group of APIs annotated `@Deprecated(level = DeprecationLevel.ERROR)` whose deprecation messages cite "Scheduled for removal in Kotlin 2.3". Because the module's own tests still reference some of these APIs through property delegates, the test class works around the resulting compile errors with a class-level `@Suppress("DEPRECATION_ERROR")` annotation.

The deprecation deadline has arrived. The deprecated APIs (and the supporting interfaces/extensions that exist solely to back them) need to be deleted. The test code that consumes them must be updated, and the `@Suppress("DEPRECATION_ERROR")` workaround should no longer be necessary.

## What to Do

### Source: `ExtrasProperty.kt`

Remove every API in `kotlin-tooling-core` that is annotated `@Deprecated(level = DeprecationLevel.ERROR)` with the "Scheduled for removal in Kotlin 2.3" message. After this work, the file must no longer contain:

- The `DEPRECATED APIs` section comment
- The standalone functions `extrasReadProperty`, `extrasFactoryProperty`, and `extrasNullableLazyProperty` (in any of their overloads)
- The interfaces `ExtrasReadOnlyProperty`, `ExtrasFactoryProperty`, and `NullableExtrasLazyProperty`
- The `Extras.Key` extension members `readProperty` (the read-only `get()` extension), `factoryProperty`, and `nullableLazyProperty` (on `Extras.Key<Optional<T>>`)
- Any `"Scheduled for removal in Kotlin 2.3"` deprecation annotations

Drop any imports that become unused once those declarations are gone — in particular, `import java.util.*` was only needed for `Optional` in the deprecated nullable-lazy machinery and should be removed.

### Tests: `ExtrasPropertyTest.kt`

Update the test class so it no longer depends on any of the removed APIs:

- Delegates that previously used `keyA.readProperty` / `keyB.readProperty` (including the `.notNull(...)` variants) must be migrated to `readWriteProperty` (the non-deprecated read-write delegate that already exists in the module).
- The delegate using `keyList.factoryProperty { ... }` must be migrated to `lazyProperty { ... }`.
- The deprecated nullable-lazy machinery has no replacement: remove the `` `test - lazyNullableProperty` `` test method along with any helper properties/fields that existed only to support it. After this work, the identifier `lazyNullableProperty` must not appear anywhere in the test file.
- Once the test file no longer references any deprecated APIs, remove the class-level `@Suppress("DEPRECATION_ERROR")` annotation.

After your changes, the `kotlin-tooling-core` module's main sources and tests must still compile, and all of its existing test classes (including `ExtrasPropertyTest`, `ExtrasTest`, `ExtrasSerializableTest`, `ExtrasKeyStableStringTest`, `ClosureTest`, `TypeTest`, `InternerTest`, and `KotlinToolingVersionTest`) must still pass.
