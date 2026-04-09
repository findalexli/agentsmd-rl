# Task: Fix Empty Separator Validation in splitByString Tokenizer

## Problem

The `splitByString` tokenizer in ClickHouse does not properly validate that separator strings are non-empty. When an empty string is passed as a separator (e.g., `['']`), the code currently accepts it without raising an error, which can lead to unexpected behavior.

## Goal

Add validation in `src/Interpreters/TokenizerFactory.cpp` to reject empty strings as separators and throw an appropriate exception with error code `BAD_ARGUMENTS`.

## Details

The relevant code is in the `registerTokenizers` function in `TokenizerFactory.cpp`, specifically in the `splitByString` tokenizer registration. The code currently iterates over an array of separator strings and adds them to a vector without checking if any are empty.

Look for the loop that processes the `array` of separator values. You need to:

1. Check each separator value to ensure it is not an empty string
2. Throw an exception with `ErrorCodes::BAD_ARGUMENTS` if an empty string is found
3. Use a clear error message like: "Incorrect parameter of tokenizer 'splitByString': the empty string cannot be used as a separator"

Additionally, while you're in this area, you should also improve the existing error message for when the entire separators array is empty - change "separators cannot be empty" to "the separators argument cannot be empty" for consistency.

## Files to Modify

- `src/Interpreters/TokenizerFactory.cpp` - Add validation in the `splitByString` tokenizer registration

## Testing

There are existing tests in `tests/queries/0_stateless/03403_function_tokens.sql` that should pass after your fix. You may need to add test cases there for the empty separator scenarios.

## Code Style

Follow ClickHouse conventions:
- Use Allman-style braces (opening brace on a new line)
- Use `Exception` with `ErrorCodes::BAD_ARGUMENTS`
