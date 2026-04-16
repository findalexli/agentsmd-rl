# Memory Leak in Tracer run_map with External RunTree Objects

## Problem

When a LangSmith `@traceable` function invokes a LangChain `Runnable` or LangGraph subgraph, the callback manager's `_configure` function injects the external `RunTree` into the `LangChainTracer`'s `run_map` so that child runs can resolve their parent for proper trace nesting.

However, since this `RunTree` was created outside the tracer's callback lifecycle, it is never removed from `run_map`. The entry persists indefinitely, retaining the full `RunTree` and its entire child tree.

In applications with nested subgraph invocations, this causes `RunTree` objects to accumulate linearly with every call, resulting in a memory leak.

## Affected Files

- `libs/core/langchain_core/callbacks/manager.py` - Where external RunTrees are injected into the handler's `run_map`
- `libs/core/langchain_core/tracers/core.py` - Core tracer implementation with tracer state management
- `libs/core/langchain_core/tracers/base.py` - Base tracer with trace completion handling (both sync and async versions)
- `libs/core/langchain_core/tracers/langchain.py` - LangChainTracer that copies state when creating new tracers

## Required Implementation

The fix must implement reference counting for externally-injected run IDs:

1. **Add `_external_run_ids` attribute**: The `LangChainTracer` and `_TracerCore` must have a `_external_run_ids` attribute that is a `dict` mapping run ID strings to integer reference counts.

2. **Track external runs on injection**: When `_configure` in `callbacks/manager.py` injects an external `RunTree` into `handler.run_map`, it must also add the run ID to `_external_run_ids` with an initial count.

3. **Increment refcount when children start**: When the tracer starts a child run whose parent is an external run ID in `_external_run_ids`, increment that parent's reference count.

4. **Decrement and cleanup when children end**: When the tracer finishes a child run, if its parent is in `_external_run_ids`, decrement the count and remove the external parent from `run_map` when the count reaches zero.

5. **Handle sibling children correctly**: A single external parent may have multiple sibling children (e.g., from a chain like `prompt | llm`). The external parent must remain in `run_map` until ALL its children complete, not be removed when the first child finishes.

6. **Preserve state when copying**: When `LangChainTracer.copy_with_metadata_defaults()` creates a new tracer, it must share the `_external_run_ids` dictionary with the new instance (similar to how `run_map` and `order_map` are shared).

7. **Support both sync and async**: The reference counting logic must work for both synchronous and asynchronous tracer code paths.

## Expected Behavior

After a `@traceable` parent function invokes a LangChain `Runnable` and all children complete:
1. The external parent `RunTree` should be removed from `run_map`
2. `tracer.run_map` should be empty (or contain only runs managed by the tracer's own lifecycle)
3. Multiple sibling children should not cause premature cleanup of the parent before all siblings finish
4. Memory usage should remain flat across repeated invocations (no accumulation of `RunTree` objects in `run_map`)

## Testing

Tests for this fix are located in `tests/unit_tests/runnables/test_tracing_interops.py` and include:
- `test_traceable_parent_run_map_cleanup()` - Verifies external RunTree is cleaned up after its single child finishes
- `test_traceable_parent_run_map_cleanup_with_sibling_children()` - Verifies external parent survives until ALL sibling children finish
- `test_traceable_parent_run_map_no_runttree_accumulation()` - Verifies RunTree objects don't accumulate across multiple calls

To verify the fix works correctly:
1. Create a tracer with a mocked LangSmith client (no real API calls)
2. Define a `@traceable` parent function that invokes a LangChain `Runnable`
3. After execution completes, verify that `tracer.run_map` is empty
4. For chains with multiple steps, verify the parent survives until ALL children finish
5. Test that memory doesn't grow across multiple invocations

## Constraints

- Use mocked clients (no real API calls needed)
- Tests must be deterministic and not flaky
- The fix must handle both sync and async code paths
- The `_configure` function must remain importable and callable
