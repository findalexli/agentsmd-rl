# Heap-Buffer-Overflow in leftPad/rightPad Functions

## Problem Description

The `leftPad` and `rightPad` string functions in ClickHouse have a heap-buffer-overflow vulnerability detected by AddressSanitizer.

### Symptom

When using `leftPad` or `rightPad` with pad strings, the code may read past the allocated buffer, triggering ASan heap-buffer-overflow errors. The issue is in `src/Functions/padString.cpp` in the `PaddingChars` class.

### Technical Context

The padding expansion loop uses `memcpySmallAllowReadWriteOverflow15` which requires at least 15 bytes of readable padding beyond the logical buffer size. Standard string containers do not provide this guarantee.

### Requirements

The fix must:

1. Use a container type for `pad_string` in the `PaddingChars` class that provides the required memory padding for safe reads
2. Handle empty pad strings in `executeImpl` (set to space character `" "`)
3. Use `validateFunctionArguments` with properly structured `FunctionArgumentDescriptors` for both mandatory and optional arguments
4. Use `chassert` (not exceptions) after validating column constness
5. Use explicit comparison `num_chars == 0` rather than implicit bool conversion
6. Use C++14 digit separators for readability (e.g., `1'000'000` instead of `1000000`)
7. Use `size()` method for character count (not `length()`) when working with the pad string container
8. Include headers `<memory>` and `<DataTypes/IDataType.h>` as needed
9. Follow ClickHouse Allman brace style (opening brace on new line)
10. Remove unused error code declarations (`ILLEGAL_TYPE_OF_ARGUMENT`, `NUMBER_OF_ARGUMENTS_DOESNT_MATCH`)
11. Use `insertFromItself` for container expansion instead of concatenation operators

### Testing

The fix should be tested with:
- Long pad strings (more than 16 characters)
- UTF8 pad strings for `leftPadUTF8`/`rightPadUTF8`
- Empty pad strings (should default to space)
- Various combinations of input strings and padding patterns