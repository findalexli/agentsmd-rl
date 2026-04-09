# Task: Extend argument validation in splitByString tokenizer

## Problem

The `splitByString` tokenizer in ClickHouse does not properly validate its arguments when provided with an array of separator strings. Specifically, it fails to reject empty strings as separators, which could lead to unexpected behavior.

When calling `tokens('some text', 'splitByString', [''])` or `tokens('some text', 'splitByString', [' ', ''])`, the function should throw a `BAD_ARGUMENTS` error because an empty string cannot meaningfully be used as a separator.

## Files to modify

- `src/Interpreters/TokenizerFactory.cpp` - Look for the `registerTokenizers` function and the `SplitByStringTokenizer` registration code.

## What needs to change

In the tokenizer factory, where `SplitByStringTokenizer` is registered with an array argument:

1. When iterating over the array of separator strings, each separator should be validated to ensure it is not empty.

2. If an empty string separator is found, throw an exception with:
   - Error code: `BAD_ARGUMENTS`
   - Message: "Incorrect parameter of tokenizer 'splitByString': the empty string cannot be used as a separator"

3. The existing error message for empty separators array should also be updated for consistency:
   - Old: "separators cannot be empty"
   - New: "the separators argument cannot be empty"

## Style guidelines

When modifying the C++ code:
- Use Allman-style braces (opening brace on a new line)
- Keep consistent with the existing code patterns in the file

## Expected behavior after fix

The following queries should return `BAD_ARGUMENTS` error:
```sql
SELECT tokens('  a  bc d', 'splitByString', ['']);
SELECT tokens('  a  bc d', 'splitByString', [' ', '']);
```

## Testing hints

The fix is located in `TokenizerFactory.cpp` near the `SplitByStringTokenizer` registration. Look for where the array of separators is processed and add validation inside the loop that iterates over the array values.
