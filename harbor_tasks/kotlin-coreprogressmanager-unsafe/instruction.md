# Task: Remove sun.misc.Unsafe Usage from CoreProgressManager

## Problem

The `CoreProgressManager` class in the Kotlin compiler CLI uses `ConcurrentLongObjectMap` from the IntelliJ SDK, which internally relies on `sun.misc.Unsafe`. This is problematic because `sun.misc.Unsafe` is being phased out in modern JDK versions (see [JEP 471](https://openjdk.org/jeps/471)).

## Goal

Update `compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java` to replace the usage of `ConcurrentLongObjectMap` with the standard Java `ConcurrentHashMap`.

## Specific Requirements

1. **Remove imports**: Remove the imports for:
   - `com.intellij.util.Java11Shim`
   - `com.intellij.util.containers.ConcurrentLongObjectMap`

2. **Update field declarations**: Change the type of these two fields from `ConcurrentLongObjectMap<ProgressIndicator>` to `ConcurrentMap<Long, ProgressIndicator>`:
   - `currentIndicators`
   - `threadTopLevelIndicators`

3. **Update instantiation**: Replace the factory method calls:
   - `Java11Shim.Companion.getINSTANCE().createConcurrentLongObjectMap()`
   - With: `new ConcurrentHashMap<>()`

4. **Update JavaDoc**: Update the class-level JavaDoc comment to document this second workaround (the sun.misc.Unsafe / JEP 471 issue).

## Context

The `CoreProgressManager` class in the Kotlin CLI is a customized version of the IntelliJ SDK's original. The change from `ConcurrentLongObjectMap` to `ConcurrentHashMap` is not expected to have performance impact in the Kotlin compiler context, but it ensures compatibility with future JDK versions that will remove `sun.misc.Unsafe`.

The IntelliJ SDK's original `CoreProgressManager` was already fixed in version 253 (issue IJPL-191435), but Kotlin maintains its own copy that needs to be updated separately.
