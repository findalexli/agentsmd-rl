# Task: Add Async Support to TodoListMiddleware

## Problem Description

The `TodoListMiddleware` in `libs/langchain_v1/langchain/agents/middleware/todo.py` provides agents with todo list management capabilities through the `write_todos` tool. However, the current implementation only supports synchronous execution. When using async agent methods like `agent.ainvoke()`, the tool cannot be properly invoked because there's no async coroutine implementation registered.

## Expected Behavior

The `write_todos` tool should work correctly in both sync and async agent execution contexts. The middleware should support async agent workflows where `agent.ainvoke()` is called.

## Files to Modify

- `libs/langchain_v1/langchain/agents/middleware/todo.py` - Add async support to the todo middleware

## Key Areas to Investigate

1. Look at how the `write_todos` tool is defined in the `TodoListMiddleware.__init__` method
2. Examine the existing `_write_todos` function - understand what it does and how it works
3. Notice that `StructuredTool.from_function` accepts both `func` and `coroutine` parameters
4. The middleware currently only passes `func` but not `coroutine`

## Requirements

1. Create an async version of the `_write_todos` function (suggested name: `_awrite_todos`)
2. Register this async function as the `coroutine` parameter when creating the `StructuredTool`
3. Follow the existing patterns in the codebase for async implementations
4. Include proper type hints and docstrings as per project standards

## Testing

Your implementation should allow the `write_todos` tool to be used in async agent execution contexts. The tests will verify that:

1. The async function exists and is properly typed
2. The tool has the coroutine registered
3. The implementation follows the project's code quality standards (linting, type checking)
4. Existing tests continue to pass

## Notes

- The async implementation can delegate to the sync implementation (the sync function handles the actual work)
- The key is registering the coroutine with the `StructuredTool` so it can be invoked in async contexts
- Refer to the project's CLAUDE.md and AGENTS.md for code style and testing requirements
