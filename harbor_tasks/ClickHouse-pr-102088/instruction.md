# Fix heap-buffer-overflow in leftPad/rightPad functions

## Problem

The `leftPad` and `rightPad` SQL functions in ClickHouse have a heap-buffer-overflow vulnerability. When padding strings with a custom pad string, the code reads beyond the allocated memory buffer.

## Affected File

- `src/Functions/padString.cpp` - Contains the `PaddingChars` class and `FunctionPadString` implementation

## Symptoms

The issue manifests when:
1. Using `leftPad()`, `rightPad()`, `leftPadUTF8()`, or `rightPadUTF8()` functions
2. With a non-empty pad string argument
3. When the function needs to copy portions of the pad string multiple times

Example queries that trigger the bug:
```sql
SELECT leftPad('x', 100, 'abcdefghijklmnopq');
SELECT rightPad('x', 100, 'abc');
SELECT leftPadUTF8('x', 50, 'абвгдежзиклмнопрс');
```

## Root Cause

The `PaddingChars` class stores the pad string in a `std::String` member. The `writeSlice` function (called by `appendTo`) uses `memcpySmallAllowReadWriteOverflow15` which requires 15 extra bytes of read padding beyond the data size. Standard `std::String` doesn't provide this padding guarantee, leading to heap-buffer-overflow when the function copies portions of the pad string.

## The Fix

Change the `pad_string` member in the `PaddingChars` class from `String` to `PaddedPODArray<UInt8>`, which provides the required 15 bytes of read padding. Additionally:

1. Use `insert()` to copy the initial pad string data into the PaddedPODArray
2. Use `insertFromItself()` instead of `operator+=` for duplicating the string
3. Move the empty pad string handling from the constructor to `executeImpl`
4. Update `getReturnTypeImpl` to use `validateFunctionArguments()` helper
5. Change references from `length()` to `size()` for PaddedPODArray compatibility

## Testing

The upstream test file `tests/queries/0_stateless/04070_pad_string_asan_overflow.sql` contains test cases that exercise the padding logic with various pad string lengths and both ASCII and UTF-8 content.

## Agent Configuration

When modifying code:
- Use Allman-style braces (opening brace on a new line)
- Wrap ClickHouse SQL function names in backticks (e.g., `leftPad`)
- Use `size()` method for PaddedPODArray instead of `length()`
