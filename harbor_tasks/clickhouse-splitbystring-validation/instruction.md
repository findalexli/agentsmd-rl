# Task: Fix Empty String Validation in TokenizerFactory

## Problem Description

The `splitByString` tokenizer in ClickHouse does not properly validate its separator arguments. When an empty string is passed as a separator (either directly or within an array of separators), it can lead to unexpected behavior.

## What Needs to Be Fixed

The tokenizer factory needs to validate that:
1. Empty strings cannot be used as separators
2. When an array of separators is provided, each element must be validated to ensure it's not empty

## Where to Look

The relevant code is in:
- **File**: `src/Interpreters/TokenizerFactory.cpp`
- Look for the `registerTokenizers` function
- Find the code handling `SplitByStringTokenizer`

## Expected Behavior

When the `splitByString` tokenizer is created with an empty string separator, it should throw an exception with `ErrorCodes::BAD_ARGUMENTS` and a clear error message explaining that empty strings cannot be used as separators.

## Additional Notes

- The error message should clearly indicate the issue
- The validation should happen for each separator in the array, not just checking if the array itself is empty
- Follow the existing code style in the repository (Allman-style braces)
- Use proper terminology: refer to logical errors as "exceptions" not "crashes"
