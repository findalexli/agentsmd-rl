# Heap-Buffer-Overflow in leftPad/rightPad Functions

## Problem Description

The `leftPad` and `rightPad` string functions in ClickHouse have a heap-buffer-overflow vulnerability detected by AddressSanitizer (ASan).

### Symptom

When using `leftPad` or `rightPad` with pad strings, the code reads past the allocated buffer, triggering ASan heap-buffer-overflow errors. The issue is in the `PaddingChars` class which handles padding character storage and expansion.

### Root Cause

The padding expansion loop uses `memcpySmallAllowReadWriteOverflow15`, a function that requires at least 15 bytes of readable memory beyond the buffer's logical size for safe operation. The current `pad_string` member uses `String` (i.e., `std::string`), which does not provide this padding guarantee. This leads to out-of-bounds reads when the padding functions are called.

Additionally, the pad string expansion uses `+=` string concatenation (`pad_string += pad_string`), which is incompatible with container types that provide memory padding.

### Required Changes

1. **Storage type**: Change the `pad_string` member in the `PaddingChars` class to a container type that provides the required memory padding for safe reads with `memcpySmallAllowReadWriteOverflow15`. The `String` type must not be used for this member.

2. **Expansion method**: Replace the `pad_string += pad_string` concatenation in the expansion loop with a method compatible with the new container type.

3. **Constructor restructuring**: Remove the `init()` method and move its initialization logic directly into the constructor. Empty pad string handling should be moved to `executeImpl`.

4. **Argument validation**: Replace the manual argument validation code with the ClickHouse `validateFunctionArguments` helper using `FunctionArgumentDescriptors`.

### Testing

The fix should be tested with:
- Long pad strings (more than 16 characters)
- UTF-8 pad strings for `leftPadUTF8`/`rightPadUTF8`
- Empty pad strings (should default to space character)
- Various combinations of input strings and padding patterns
