# Fix Argument Descriptions for leftPad/rightPad Functions

## Symptom

When users call `leftPad` or `rightPad` with incorrect argument types, the error messages display misleading argument descriptions that do not match the actual expected types.

Specifically:
- The first argument (the string to pad) shows an error description of "Array" but actually accepts String or FixedString types
- The second argument (the target length) shows an error description containing "const UInt*" but should show "UInt*"
- The third argument (the padding string) shows an error description of "Array" but actually accepts String type

## Expected Behavior

When `leftPad` or `rightPad` functions report type errors, the argument descriptions in the error messages should accurately describe what types are actually accepted:
- The string argument should be described as accepting "String or FixedString"
- The length argument should be described as "UInt*" (without a "const " prefix)
- The padding string argument should be described as "String"

## Affected Functions

The issue affects the `leftPad` and `rightPad` SQL functions. These are implemented in the Functions directory of the source code.

## Requirements

1. Locate where these functions define their argument descriptors
2. Update the description strings so they accurately reflect the actual accepted types
3. Ensure the old incorrect descriptions no longer appear in error messages
