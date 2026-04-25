# Task: Fix Incorrect Argument Descriptions in leftPad/rightPad Functions

## Problem

The `leftPad` and `rightPad` SQL functions in ClickHouse have incorrect argument descriptions in their `FunctionArgumentDescriptors`. When a user passes the wrong type to one of these functions, the error message displays a type description that does not match what the argument's validator actually accepts, misleading users about what types are valid.

The function argument validation is implemented using `validateFunctionArguments` with `FunctionArgumentDescriptors` that define each argument's name, type validator, and a human-readable description string. The description strings currently do not accurately reflect the types that the corresponding validators accept.

## Task

In the `padString.cpp` file, locate the `FunctionArgumentDescriptors` for the pad functions and correct the description strings so they match the actual types their validators accept.

The three arguments that need corrected descriptions are:

1. The mandatory **"string"** argument — validated by `isStringOrFixedString`. The description should indicate the types this validator accepts.

2. The mandatory **"length"** argument — validated by `isInteger`. The description should indicate the types this validator accepts (unsigned integer types).

3. The optional **"pad_string"** argument — validated by `isString`. The description should indicate the type this validator accepts.

## Current Symptom

Users see error messages like:
- For the "string" argument: description says "Array" but the validator accepts String or FixedString
- For the "length" argument: description says "const UInt*" but should not include "const"
- For the "pad_string" argument: description says "Array" but the validator only accepts String

## Context

- This is a follow-up to a prior PR that introduced argument validation for these functions
- The change only affects the descriptive strings used in error messages — no logic changes are needed
- Follow the existing code style in the file (Allman brace style)
