# Fix use-after-scope in parallel Object type deserialization

## Problem Description

The `deserializeBinaryBulkStatePrefix` function in `src/DataTypes/Serializations/SerializationObject.cpp` has a memory safety bug when using thread pools for parallel deserialization of Object types.

When tasks are scheduled in a thread pool and reference stack-local variables (`tasks` and `caches` vectors), if an exception is thrown after task scheduling but before completion, the stack frame is destroyed while pool threads may still be accessing those variables, leading to dangling references.

## The Bug

In the parallel deserialization code path:
1. Tasks are created and scheduled in a thread pool
2. These tasks hold references to stack-local vectors (`tasks` and `caches`)
3. If an exception occurs during task scheduling or execution, the function exits
4. The stack frame is destroyed, but pool threads may still be accessing the now-dangling references
5. This leads to use-after-scope memory corruption

## Required Fix

You must ensure that when `deserializeBinaryBulkStatePrefix` exits (including due to exceptions), all already-scheduled tasks are properly drained (executed and waited on) before the stack frame is destroyed.

### Specific Requirements

1. **Automatic cleanup mechanism**: Use ClickHouse's `SCOPE_EXIT` macro (already available in the codebase) to register cleanup code that runs on all exit paths. The `SCOPE_EXIT` macro should be placed:
   - After the `task_size = std::max(...)` calculation
   - Before the `for (size_t i = 0; i != num_tasks; ++i)` loop that schedules tasks

2. **Task draining**: The cleanup code must:
   - Call `tryExecute()` on each task in the `tasks` vector
   - Call `wait()` on each task in the `tasks` vector
   - Use range-based for loops: `for (const auto & task : tasks)`

3. **Explanatory comment**: Include a comment before the `SCOPE_EXIT` block that explains:
   - Why the cleanup is needed (prevent dangling references to stack locals)
   - That it handles all exit paths including exceptions
   - Reference to task draining or pool thread safety

4. **No timing-based synchronization**: Do not use `sleep()`, `usleep()`, `nanosleep()`, `sleep_for()`, or `this_thread::sleep` - these are unacceptable for fixing race conditions in ClickHouse.

5. **Code style requirements**:
   - Use spaces, not tabs
   - No trailing whitespace
   - Follow existing code style (Allman braces where applicable)

6. **Header file**: Ensure `src/DataTypes/Serializations/SerializationObject.h` has `#pragma once` as its first line.

### Verification Checklist

After your fix:
- [ ] Code compiles without syntax errors
- [ ] No tabs or trailing whitespace in the modified file
- [ ] `SCOPE_EXIT` macro is used for cleanup
- [ ] Both `tryExecute()` and `wait()` are called on all tasks in the cleanup code
- [ ] A comment explains the purpose (preventing dangling references on exception)
- [ ] No sleep calls are used
- [ ] Header file has `#pragma once` as first line

## Example Pattern

The fix should follow this pattern (conceptual - adapt to the actual code context):

```cpp
size_t task_size = std::max(structure_state_concrete->sorted_dynamic_paths->size() / num_tasks, 1ul);

/// <comment explaining the need for cleanup on exception>
SCOPE_EXIT(
    for (const auto & task : tasks)
        task->tryExecute();
    for (const auto & task : tasks)
        task->wait();
);

for (size_t i = 0; i != num_tasks; ++i)
{
    // ... task scheduling code ...
}
```

## Constraints

- Target file: `src/DataTypes/Serializations/SerializationObject.cpp`
- Target function: `deserializeBinaryBulkStatePrefix` in the `SerializationObject` class
- Must not use manual try-catch blocks for flow control
- Must not use sleep-based synchronization
