# Fix heap-buffer-overflow in leftPad/rightPad functions

The `leftPad` and `rightPad` functions (defined in `src/Functions/padString.cpp`) have a heap-buffer-overflow vulnerability that triggers Address Sanitizer (ASan) errors.

## Problem

When padding strings with short pad strings (especially those < 16 characters), the code reads beyond allocated memory boundaries. The issue is in the `PaddingChars` class which stores the padding pattern in a `String` and uses `memcpySmallAllowReadWriteOverflow15` for fast copying - this function requires 15 bytes of read padding beyond the buffer size, which `std::string` does not provide.

## Where to look

- **Primary file**: `src/Functions/padString.cpp`
- **Key class**: `PaddingChars` - handles the padding character pattern
- **Key methods**:
  - `init()` - currently initializes pad_string with String concatenation
  - `appendTo()` - writes padding characters using writeSlice
  - `executeImpl()` - the main execution entry point

## Expected fix approach

The solution should use a container that provides the required memory padding. The codebase has `PaddedPODArray<UInt8>` which provides exactly the 15-byte read padding needed by `memcpySmallAllowReadWriteOverflow15`.

Key changes needed:
1. Change `pad_string` field from `String` to `PaddedPODArray<UInt8>`
2. Use `insert()` and `insertFromItself()` methods instead of `+=` for string expansion
3. Move empty pad string handling from `PaddingChars::init()` to `executeImpl()`
4. Update `numCharsInPadString()` to use `.size()` instead of `.length()`
5. Remove `reinterpret_cast` when accessing `pad_string.data()` (now returns `UInt8*` directly)

## Additional improvements included in the fix

The PR also includes these cleanup improvements:
- Replace manual argument validation with `validateFunctionArguments()` helper
- Remove unused error codes (`ILLEGAL_TYPE_OF_ARGUMENT`, `NUMBER_OF_ARGUMENTS_DOESNT_MATCH`)
- Use C++14 digit separator `1'000'000` for `MAX_NEW_LENGTH`
- Use explicit `num_chars == 0` comparison instead of `!num_chars`
- Reorder includes alphabetically
- Use proper constructor initialization list formatting (Allman style)

## Testing

The existing test file `tests/queries/0_stateless/04070_pad_string_asan_overflow.sql` demonstrates the issue with various pad string lengths. A correct fix should:
- Use `PaddedPODArray<UInt8>` for the pad string storage
- Handle empty pad strings properly
- Maintain UTF-8 support through `utf8_offsets`
- Preserve all existing functionality for both ASCII and UTF-8 padding operations

## Constraints

- Follow ClickHouse C++ style: Allman braces (opening brace on new line)
- Don't use sleep for race conditions
- When writing comments about ASan findings, use "ASan" not "ASAN"
- When describing logical errors, use "exception" not "crash"
