# Fix Use-After-Scope in Parallel Object Type Deserialization

## Problem

ClickHouse's parallel deserialization of Object types has a critical use-after-scope bug. When processing Object type data with parallel tasks, the system schedules work into a thread pool (`prefixes_deserialization_thread_pool`). These tasks capture references to stack-local variables (callbacks, getters, caches).

If an exception is thrown during task scheduling or later in the function, the stack unwinds and destroys those locals while pool threads may still be running — causing use-after-scope or use-after-free.

## Your Task

Add proper cleanup code to ensure all already-scheduled tasks are drained on every exit path (including exceptions), so pool threads do not dereference dangling references to stack locals.

**Key requirements:**

1. The cleanup must be triggered on all exit paths, including exceptions — use the appropriate ClickHouse idiom for scope-guarded cleanup
2. For each scheduled task, first execute any pending work, then wait for it to complete
3. Add a comment in the code explaining the purpose, containing this exact text: `Ensure all already-scheduled tasks are drained on any exit path`
4. Place the cleanup guard before the task scheduling loop so it protects against partial scheduling failures

## Constraints

- Do not modify the existing task scheduling logic
- The fix should handle all exit paths including exceptions
- Follow ClickHouse naming conventions
- Do not delete or relax any existing tests
