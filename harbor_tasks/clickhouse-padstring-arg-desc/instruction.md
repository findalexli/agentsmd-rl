# Task: Fix Incorrect Argument Descriptions in leftPad/rightPad Functions

## Problem

The `leftPad` and `rightPad` SQL functions in ClickHouse have incorrect argument descriptions in their `FunctionArgumentDescriptors`. When a user passes the wrong type to one of these functions, the error message displays an incorrect type description, misleading users about what types are actually accepted.

The function argument validation is implemented using `validateFunctionArguments` with `FunctionArgumentDescriptors` that define each argument's name, type validator, and a human-readable description string. The description strings currently do not accurately reflect the types that the corresponding validators accept.

## Correct Argument Descriptions

The `FunctionArgumentDescriptors` for these functions define three arguments. Their description strings should be corrected to match the actual types their validators accept:

1. The mandatory **"string"** argument — validated by `isStringOrFixedString`. The description string should read `"String or FixedString"`.

2. The mandatory **"length"** argument — validated by `isInteger`. The description string should read `"UInt*"`.

3. The optional **"pad_string"** argument — validated by `isString`. The description string should read `"String"`.

## Context

- This is a follow-up to a prior PR that introduced argument validation for these functions
- The change only affects the descriptive strings used in error messages — no logic changes are needed
- Follow the existing code style in the file (Allman brace style)
