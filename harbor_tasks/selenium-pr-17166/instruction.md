# Bug: Keys.charAt() violates CharSequence contract

## Problem

The `Keys` enum in `java/src/org/openqa/selenium/Keys.java` implements `CharSequence`, but its `charAt(int index)` method does not properly follow the interface contract.

According to the Java `CharSequence` specification, `charAt()` should throw `IndexOutOfBoundsException` when called with an invalid index (i.e., when `index < 0` or `index >= length()`). Since each `Keys` instance represents a single character (`length()` returns 1), only index 0 is valid.

Currently, calling `charAt()` with an invalid index silently returns an unexpected value instead of throwing the appropriate exception. This can mask bugs in code that incorrectly iterates over or accesses characters in a `Keys` value, and violates expectations of any code relying on standard `CharSequence` behavior.

## Expected Behavior

- `Keys.ENTER.charAt(0)` should return the key code character (this works correctly)
- `Keys.ENTER.charAt(1)` should throw `IndexOutOfBoundsException`
- `Keys.ENTER.charAt(-1)` should throw `IndexOutOfBoundsException`

## Current Behavior

- `Keys.ENTER.charAt(1)` returns a value without throwing
- `Keys.ENTER.charAt(-1)` returns a value without throwing

## Files to Investigate

- `java/src/org/openqa/selenium/Keys.java` - the `charAt()` method implementation
