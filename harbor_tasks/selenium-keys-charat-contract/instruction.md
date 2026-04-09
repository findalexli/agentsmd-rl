# Fix Keys.charAt() to Enforce CharSequence Contract

## Problem

The `Keys` class in `java/src/org/openqa/selenium/Keys.java` implements `CharSequence`, but its `charAt(int index)` method violates the contract. Currently, when called with an invalid index (anything other than 0), it silently returns the null character (`'\0'`) instead of throwing `IndexOutOfBoundsException`.

This can mask bugs and produces incorrect comparisons when `Keys` objects are used in string operations.

## Expected Behavior

Per the `CharSequence` interface contract:
- `length()` returns `1` (each `Keys` enum value represents a single character)
- `charAt(0)` returns the key code
- `charAt(index != 0)` throws `IndexOutOfBoundsException`

## Task

Fix the `charAt()` method in `java/src/org/openqa/selenium/Keys.java` to:
1. Throw `IndexOutOfBoundsException` for any index other than 0
2. Include the index value and length in the exception message (e.g., `"Index: 5, Length: 1"`)
3. Continue to return the `keyCode` for valid index 0

## Files to Modify

- `java/src/org/openqa/selenium/Keys.java` - Modify the `charAt(int index)` method

## Notes

- `Keys` represents a single Unicode PUA (Private Use Area) character
- The class is an enum, and each enum constant has a `keyCode` field
- The fix should be minimal - only the `charAt()` method logic needs to change
- Look at the `length()` method for context on how the class views its size
