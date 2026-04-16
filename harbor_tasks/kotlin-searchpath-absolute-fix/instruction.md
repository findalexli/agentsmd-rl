# Fix SearchPathType Arguments to Resolve to Absolute Paths

## Problem

The Kotlin build tools API is not resolving `SearchPathType` arguments to absolute paths before joining them with path separators. This affects the following compiler arguments:
- `classpath` (CLASSPATH)
- `klibLibraries` (X_KLIB)
- `javaModulePath` (X_MODULE_PATH)

When relative paths are passed to the compiler through these arguments, they are joined directly without being resolved to absolute paths first. This causes inconsistent behavior depending on the working directory. The `PathListType` handling already correctly resolves paths to absolute before joining; `SearchPathType` should do the same.

## Required Behavior

For each affected SearchPathType argument (X_KLIB, X_MODULE_PATH, CLASSPATH), the code must resolve each path to an absolute path before joining them with the system path separator. The arguments should use `absolutePathStringOrThrow()` to convert relative paths to absolute.

In the generated code, when retrieving SearchPathType arguments like `get(X_KLIB)`, `get(X_MODULE_PATH)`, or `get(CLASSPATH)`, the result must be mapped through `absolutePathStringOrThrow()` before calling `joinToString` with the path separator.

## Files to Modify

1. **compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt**
   - This is the code generator that produces the argument mapping code

2. **compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt**
   - Generated file with handling for X_KLIB, X_MODULE_PATH, and CLASSPATH

3. **compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt**
   - Generated file with two sections (for different compiler versions)
   - Both sections have handling for X_KLIB, X_MODULE_PATH, and CLASSPATH

## Verification

After your fix:
- All three files should contain `absolutePathStringOrThrow` calls for the affected arguments (X_KLIB, X_MODULE_PATH, CLASSPATH)
- The Kotlin files should have valid syntax (can be parsed by kotlinc)
- SearchPathType arguments should not use raw `joinToString` without first resolving paths to absolute

## Context

- Issue: KT-85556
- This is a Build Tools API (BTA) fix
- The repository uses Gradle for building
- Related to the Kotlin compiler's JVM argument handling
