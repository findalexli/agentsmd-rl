# Fix Use-After-Scope Bug in ClickHouse Parallel Object Type Deserialization

## Problem Description

There is a **use-after-scope bug** in ClickHouse's parallel deserialization code for Object types. When binary bulk state prefixes are deserialized in parallel using a thread pool, lambda functions capture local variables by reference and are scheduled for asynchronous execution via `trySchedule`. If the enclosing function exits (normally or via exception) before all scheduled tasks complete, the thread pool threads may dereference dangling references to stack locals that have gone out of scope.

## Verification Requirements

The fix must satisfy the following verifiable conditions:

1. **Tasks vector declaration**: The file must contain the exact declaration:
   ```
   std::vector<std::shared_ptr<DeserializationTask>> tasks;
   ```

2. **Task size variable**: The file must use a variable named `task_size` to compute the size of parallel work units.

3. **SCOPE_EXIT pattern**: The file must contain a `SCOPE_EXIT` block with the following structure (whitespace may vary):
   ```
   SCOPE_EXIT(
       for (const auto & task : tasks)
           task->tryExecute();
       for (const auto & task : tasks)
           task->wait();
   );
   ```

4. **Required comment**: A comment must contain ALL three of these exact phrases:
   - "Ensure all already-scheduled tasks are drained"
   - "any exit path (including exceptions)"
   - "pool threads do not dereference dangling references to stack locals"

5. **Placement**: The `SCOPE_EXIT` block must be placed after the `task_size` calculation and before the for loop that schedules the parallel tasks.

6. **Target file**: The fix must be applied to:
   `/workspace/ClickHouse/src/DataTypes/Serializations/SerializationObject.cpp`

## Symptom

When the function that spawns parallel deserialization tasks exits before all tasks complete, pool threads can access stack variables that have been destroyed. The code should ensure cleanup happens on all exit paths, including exceptions.