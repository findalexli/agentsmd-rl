# Fix Klib dump parsing qualified names adjacent to vararg symbol

## Problem

The klib ABI parser's `validIdentifierWithDotRegex` pattern incorrectly consumes qualified names that end with the vararg symbol (`...`). When parsing something like `kotlin/DoubleArray...`, the regex was matching the entire string including the `...` as part of the identifier, leaving nothing for the vararg parser to recognize.

## Affected File

`compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt`

Look for the `validIdentifierWithDotRegex` pattern definition. The issue is in how this regex handles the `...` suffix that indicates a vararg parameter.

## Expected Behavior

- `kotlin/DoubleArray...` should be parsed as:
  - Type name: `kotlin/DoubleArray`
  - Vararg indicator: `...` (isVararg = true)

- The regex needs to stop matching **before** the `...` sequence when it appears at the end of a qualified name.

## Related Test File

`compiler/util-klib-abi/test/org/jetbrains/kotlin/library/abi/parser/KlibParsingCursorExtensionsTest.kt`

There's already a test `parseValueParamVarargWithTypeParams` that tests a similar case. A new test case `parseValueParamVarargWithoutTypeParams` needs to be added to verify the fix works for qualified names without type parameters.

## Testing

Run the tests for `KlibParsingCursorExtensionsTest` to verify the fix works correctly:

```bash
./gradlew :compiler:util-klib-abi:test --tests "org.jetbrains.kotlin.library.abi.parser.KlibParsingCursorExtensionsTest"
```

## Notes

- The fix involves a negative lookahead in the regex pattern
- Don't modify the base `validIdentifierRegex` (without dots) - only the `validIdentifierWithDotRegex` needs the fix
- The repository uses Gradle for building
