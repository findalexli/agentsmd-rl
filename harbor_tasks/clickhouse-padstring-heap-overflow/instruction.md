# Fix Heap-Buffer-Overflow in leftPad/rightPad Functions

## Problem Description

The `leftPad` and `rightPad` string functions in ClickHouse have a heap-buffer-overflow vulnerability. The issue occurs in `src/Functions/padString.cpp` when handling padding strings.

### The Bug

The `PaddingChars` class stores the pad string and expands it by doubling until it reaches at least 16 characters (for performance). The expansion uses `memcpySmallAllowReadWriteOverflow15` which requires 15 extra bytes of readable padding beyond the buffer size.

The original implementation uses `std::string` for the pad string storage, which doesn't provide this padding guarantee. When the code reads past the string's allocated memory during the expansion loop, it causes a heap-buffer-overflow detected by AddressSanitizer.

### Key Code Areas

**File:** `src/Functions/padString.cpp`

**The PaddingChars class:** Stores and expands the pad string for efficient copying during padding operations.

**Critical issue location:**
- Constructor that initializes pad_string
- The expansion loop that doubles the pad string until >= 16 chars
- The `appendTo` method that calls `writeSlice` (which uses `memcpySmallAllowReadWriteOverflow15`)

### What You Need to Do

1. **Change the storage type** for `pad_string` from `String` to a type that provides the required memory padding
2. **Update all code** that interacts with `pad_string` to use the new storage type's API
3. **Handle empty pad strings** correctly (should default to space character)
4. **Update UTF8 handling** to work with the new storage type
5. **Refactor argument validation** to use the standard helper function
6. **Follow ClickHouse coding conventions:**
   - Use Allman brace style (opening brace on new line)
   - Use `ASan` not `ASAN` in any comments
   - Add new test file instead of extending existing ones

### Testing

The fix should include regression tests that exercise:
- `leftPad` and `rightPad` with long pad strings (>16 chars)
- `leftPadUTF8` and `rightPadUTF8` with UTF8 pad strings
- Various combinations of input strings and padding patterns

### References

- The fix involves `PaddedPODArray` which provides 15 bytes of read padding
- Look at how other functions in ClickHouse handle similar padding requirements
- Check `validateFunctionArguments` for argument validation patterns
