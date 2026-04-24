# Fix Use-After-Scope Bug in ClickHouse Parallel Object Type Deserialization

## Problem Description

There is a **use-after-scope bug** in ClickHouse's parallel deserialization code for Object types. The bug is in the `deserializeBinaryBulkStatePrefix` function in `SerializationObject.cpp`.

When binary bulk state prefixes are deserialized in parallel using a thread pool, lambda functions capture local variables by reference and are scheduled for asynchronous execution via `trySchedule`. If the enclosing function exits (normally or via exception) before all scheduled tasks complete, the thread pool threads may dereference dangling references to stack locals that have gone out of scope.

## The Bug Pattern

The code spawns parallel tasks using a thread pool pattern similar to:

```cpp
// Simplified representation of the bug pattern
for (size_t i = 0; i < num_tasks; ++i)
{
    auto task = std::make_shared<DeserializationTask>(...);
    thread_pool->trySchedule([task, &local_ref] { ... });  // Captures reference to local
    tasks.push_back(task);
}
// Missing: cleanup on scope exit - if function exits here, locals are destroyed
// but thread pool threads may still be accessing &local_ref
```

## Your Task

Add a cleanup mechanism that ensures all already-scheduled tasks complete before the function exits on **any exit path** (normal return or exception). This prevents pool threads from dereferencing dangling references to stack locals.

The fix should:
1. Be placed after the `task_size` calculation (where parallel work is divided)
2. Be placed before the loop that schedules the parallel tasks
3. Ensure cleanup happens automatically when the function scope exits
4. Call `tryExecute()` on each task, then `wait()` on each task (in that order)

## Target File

`/workspace/ClickHouse/src/DataTypes/Serializations/SerializationObject.cpp`

Look for the `deserializeBinaryBulkStatePrefix` function and the code that creates parallel `DeserializationTask` objects.

## Hints

- ClickHouse likely has a scope guard mechanism (commonly named `SCOPE_EXIT` or similar)
- The fix should iterate over the tasks collection and call `tryExecute()` followed by `wait()`
- Consider what happens if an exception is thrown after some tasks are scheduled but before all complete
