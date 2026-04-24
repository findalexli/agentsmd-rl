# Heap-Buffer-Overflow in leftPad/rightPad Functions

## Problem Description

The `leftPad` and `rightPad` string functions in ClickHouse have a heap-buffer-overflow vulnerability detected by AddressSanitizer (ASan).

### Symptom

When using `leftPad` or `rightPad` with pad strings, the code may read past the allocated buffer, triggering ASan heap-buffer-overflow errors. The issue is in the `PaddingChars` class which uses `memcpySmallAllowReadWriteOverflow15` - a function that requires at least 15 bytes of readable padding beyond the logical buffer size for safe operation.

### Technical Context

The `memcpySmallAllowReadWriteOverflow15` function is used in the padding expansion loop. This function requires 15 bytes of readable memory beyond the buffer's logical size for safe operation. Standard string containers do not provide this guarantee, which causes the heap-buffer-overflow when the padding functions are called.

### Required Fix

The fix must use a container type for `pad_string` that provides the required memory padding for safe reads with `memcpySmallAllowReadWriteOverflow15`. The container must:
- Provide at least 15 bytes of readable padding beyond its size
- Support efficient expansion for the padding loop
- Be compatible with the existing UTF8 handling code

Additionally, the empty pad string handling should be moved from the removed `init()` method into `executeImpl`, and argument validation should use the `validateFunctionArguments` helper with `FunctionArgumentDescriptors` instead of manual validation.

### Observable Changes

After the fix, the source file will show:
- A different container type for `pad_string` (providing required memory padding)
- Use of `validateFunctionArguments` helper with properly structured descriptors
- Removal of unused error code declarations (`ILLEGAL_TYPE_OF_ARGUMENT`, `NUMBER_OF_ARGUMENTS_DOESNT_MATCH`)
- Addition of `<memory>` and `<DataTypes/IDataType.h>` includes
- Updated constructor brace style (Allman style per ClickHouse CI requirements)
- Empty pad string handling in `executeImpl` method

### Testing

The fix should be tested with:
- Long pad strings (more than 16 characters)
- UTF8 pad strings for `leftPadUTF8`/`rightPadUTF8`
- Empty pad strings (should default to space)
- Various combinations of input strings and padding patterns

A reference test file `tests/queries/0_stateless/04070_pad_string_asan_overflow.sql` shows the test cases that should pass after the fix.
