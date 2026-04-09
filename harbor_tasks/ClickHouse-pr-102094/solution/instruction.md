# Task: Extend Argument Validation in splitByString Tokenizer

## Problem

The `splitByString` tokenizer in ClickHouse does not properly validate its arguments. When an empty string is passed as one of the separators, it should be rejected with a clear error message.

## Background

In the `TokenizerFactory.cpp` file, there is a tokenizer registration for `splitByString` that accepts an array of separator strings. Currently, this code iterates through the array and converts each value to a string, but it does not check if any of those strings are empty. An empty string is not a valid separator and should be rejected.

## What You Need to Do

1. Locate the `TokenizerFactory.cpp` file in `src/Interpreters/`
2. Find the code that registers the `splitByString` tokenizer
3. Add validation to reject empty strings as separators
4. When an empty string is found, throw an exception with:
   - Error code: `BAD_ARGUMENTS`
   - A clear error message explaining that empty strings cannot be used as separators
5. Improve the existing error message for when the separators array is empty

## Requirements

- The fix should be inside the loop that processes each separator value
- The validation must happen before the value is added to the results
- Use Allman-style braces (opening brace on a new line)
- Follow the existing exception-throwing pattern in the file
- Use `ErrorCodes::BAD_ARGUMENTS` for the error code
- Include the tokenizer name in the error message using `SplitByStringTokenizer::getExternalName()`

## Files to Modify

- `src/Interpreters/TokenizerFactory.cpp`

## Notes

The error message should clearly indicate:
1. Which tokenizer the error is for
2. That empty strings cannot be used as separators
3. The improved message for empty separators array: "the separators argument cannot be empty"

When writing C++ code in this repository, always use Allman-style braces (opening brace on a new line) as enforced by the style check in CI.
