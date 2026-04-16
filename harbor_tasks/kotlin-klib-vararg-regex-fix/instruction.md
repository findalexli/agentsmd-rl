# KT-85149: Fix Klib dump parsing qualified names adjacent to vararg symbol

## Problem

The Klib dump parser has a bug when parsing value parameters that contain both:
1. A qualified type name with dots (e.g., `kotlin/DoubleArray`)
2. A vararg symbol (`...`) immediately following the type name

For example, the input `kotlin/DoubleArray...` is not being parsed correctly. The parser should identify:
- Type class name: `kotlin/DoubleArray`
- isVararg: `true`

However, the current implementation is incorrectly consuming the vararg symbol as part of the qualified name. Specifically, the regex in `validIdentifierWithDotRegex` (located in `compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt`) allows `.` characters without restriction, causing it to consume the `...` vararg symbol as part of the type name instead of stopping before it.

## What to Do

1. Examine the `validIdentifierWithDotRegex` pattern in `Cursor.kt`
2. Identify why it's incorrectly consuming the `...` vararg symbol as part of qualified names
3. Modify the regex so it stops matching before the `...` sequence while still allowing dots in type names like `kotlin/DoubleArray`
4. Ensure the fix works for parsing inputs like `kotlin/DoubleArray...` correctly, where the type is `kotlin/DoubleArray` and the parameter is marked as a vararg

## Context

The `validIdentifierWithDotRegex` is used when parsing qualified names that may contain dots (like `kotlin/DoubleArray`). The regex should match the type name but stop before the vararg symbol `...`.

The existing `validIdentifierRegex` (without dots) in the same file already handles similar cases correctly and can be used as a reference for how to prevent unwanted character consumption.

## Testing

The repository uses Gradle for building and testing. You can run tests with:

```bash
./gradlew :compiler:util-klib-abi:test --no-daemon
```

Make sure your fix allows parsing inputs like `kotlin/DoubleArray...` correctly, where the type is `kotlin/DoubleArray` and the parameter is marked as a vararg.
