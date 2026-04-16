# Fix heap-buffer-overflow in leftPad/rightPad functions

The `leftPad` and `rightPad` functions have a heap-buffer-overflow vulnerability that triggers Address Sanitizer (ASan) errors when processing certain inputs.

## Problem Description

When padding strings with short pad strings (especially those under 16 characters), the code reads beyond allocated memory boundaries. The issue occurs in the padding character pattern storage mechanism which uses `memcpySmallAllowReadWriteOverflow15` for fast copying. This function requires 15 bytes of readable memory beyond the buffer's actual content, which the current container does not provide.

## Affected Code

- **File**: `src/Functions/padString.cpp`

## Requirements

The fix must satisfy the following requirements:

1. **Memory Safety**: The padding character storage must provide at least 15 bytes of readable memory padding beyond its size to safely work with `memcpySmallAllowReadWriteOverflow15`.

2. **Container Selection**: Use `PaddedPODArray<UInt8>` from `<Common/PODArray.h>` for the internal padding character storage. This container provides the required memory safety guarantees.

3. **String Expansion**: When expanding the padding pattern, use `insertFromItself()` method instead of string concatenation operators.

4. **Direct Access**: Access the container's data directly without `reinterpret_cast` - the container's `data()` method returns the appropriate pointer type.

5. **Empty Pad Handling**: Empty pad string checks must be handled in the main execution entry point (`executeImpl`) rather than in initialization code.

6. **Style Requirements**:
   - Use explicit comparison `num_chars == 0` instead of implicit boolean conversion
   - Use C++14 digit separator `1'000'000` for the `MAX_NEW_LENGTH` constant
   - Use `validateFunctionArguments()` helper for argument validation
   - Define `FunctionArgumentDescriptors` for argument validation

7. **Cleanup**: Remove unused error codes `ILLEGAL_TYPE_OF_ARGUMENT` and `NUMBER_OF_ARGUMENTS_DOESNT_MATCH` from the ErrorCodes namespace.

8. **Preservation**: Maintain existing UTF-8 support through `utf8_offsets` and preserve all existing functionality for both ASCII and UTF-8 padding operations.

## Constraints

- Follow ClickHouse C++ style: Allman braces (opening brace on new line)
- Don't use sleep for race conditions
- When writing comments about ASan findings, use "ASan" not "ASAN"
- When describing logical errors, use "exception" not "crash"
