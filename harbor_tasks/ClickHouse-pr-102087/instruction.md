# Fix heap-buffer-overflow in leftPad/rightPad functions

## Problem

The `leftPad` and `rightPad` string functions in ClickHouse have a heap-buffer-overflow vulnerability that can be detected by Address Sanitizer (ASan). The issue is in how padding characters are stored and copied in the `PaddingChars` class in `src/Functions/padString.cpp`.

The padding logic uses `memcpySmallAllowReadWriteOverflow15` which requires 15 extra bytes of read padding beyond the buffer size. The current implementation uses a regular `String` class which doesn't provide this padding, leading to out-of-bounds reads when the pad string is shorter than 16 bytes and needs to be repeated.

## Symptoms

- ASan reports heap-buffer-overflow when running queries like:
  - `SELECT leftPad('x', 100, 'abc')`
  - `SELECT rightPad('x', 50, 'абвгдежзиклмнопрс')` (UTF8 variant)
- The overflow happens in the `writeSlice` function called from `PaddingChars::appendTo`

## What needs to be fixed

The `padString.cpp` file needs to be modified to:

1. Store the pad string in a container that provides 15 bytes of read padding (`PaddedPODArray<UInt8>` instead of `String`)
2. Update the constructor to initialize this container properly
3. Move the empty pad string handling logic from a separate `init()` method to the main execution function
4. Use `insertFromItself` instead of `operator+=` for duplicating the pad string content (since `PaddedPODArray` has different semantics)
5. Use `validateFunctionArguments` helper for argument validation instead of manual checks

## File to modify

- `src/Functions/padString.cpp` - Contains the `PaddingChars` class and `FunctionPadString` class

## References

- Look at how other functions use `PaddedPODArray` for similar purposes
- The `writeSlice` function and `memcpySmallAllowReadWriteOverflow15` are defined in the GatherUtils/Algorithms headers
- Check how `validateFunctionArguments` is used in other functions for argument validation

## Notes

- The fix should maintain the same behavior for all edge cases (empty strings, UTF8, etc.)
- When writing C++ code, use Allman-style braces (opening brace on a new line)
- The expected output for test queries is provided in the test files
