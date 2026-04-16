# Fix use-after-scope in parallel Object type deserialization

## Problem Description

The `deserializeBinaryBulkStatePrefix` function in `src/DataTypes/Serializations/SerializationObject.cpp` has a memory safety bug when using thread pools for parallel deserialization of Object types.

When tasks are scheduled in a thread pool and reference stack-local variables (`tasks` and `caches` vectors), if an exception is thrown after task scheduling but before completion, the stack frame is destroyed while pool threads may still be accessing those variables, leading to dangling references.

## Your Task

Fix the use-after-scope bug by ensuring automatic cleanup of scheduled tasks when the function exits (including due to exceptions), preventing pool threads from dereferencing stack-local data after the stack frame is destroyed.

## Verification Criteria

Your fix will be verified against the following requirements:

1. **RAII cleanup mechanism**: The solution must use an automatic cleanup mechanism (not manual try-catch blocks) to ensure task cleanup happens on all function exit paths
2. **Task completion**: All scheduled tasks must be properly cleaned up (executed and waited on) before the function returns or throws
3. **Descriptive comment**: A comment must explain the purpose of the cleanup (preventing dangling references when exceptions occur)
4. **No timing-based synchronization**: The fix must not use sleep() or other timing-based approaches
5. **Correct placement**: The cleanup code must be positioned after task_size calculation
6. **Code style**: Allman brace style, no tabs, no trailing whitespace

## Constraints

- The target file is `src/DataTypes/Serializations/SerializationObject.cpp`
- The function is `deserializeBinaryBulkStatePrefix` in the `SerializationObject` class
- Follow the existing code style (Allman braces)
- The code must compile without syntax errors
- Header file must have `#pragma once` in the first line

## What Not To Do

- Do not use sleep() or other timing-based synchronization
- Do not add manual try-catch blocks for flow control
- Do not skip cleanup on error paths

## How to Verify

After applying your fix:
1. The file should compile without syntax errors
2. No tabs or trailing whitespace should be introduced
3. The header file should have `#pragma once` in the first line
4. The cleanup code must be properly structured and positioned