# Task: Add async support to TodoListMiddleware

## Problem

The `TodoListMiddleware` in `langchain.agents.middleware.todo` provides a `write_todos` tool that can be called by agents. However, when an async agent calls this tool, execution fails because the tool has no async handler registered.

## Observed Behavior

When an async agent invokes the `write_todos` tool, the call fails or returns an error. The middleware has a sync implementation (`_write_todos`) but lacks a corresponding async implementation.

## Expected Behavior

The `write_todos` tool must support both sync and async invocation. When called from an async agent, it should behave identically to the sync version.

## Requirements

The fix must satisfy all of the following:

1. **Async function requirement**: Add an async function to the todo middleware module at `libs/langchain_v1/langchain/agents/middleware/todo.py`. This function must:
   - Accept `runtime` and `todos` parameters
   - Return a `Command` object
   - Be a proper async coroutine (not a sync function that returns a coroutine)
   - Have a docstring

2. **Tool registration**: The `write_todos` tool in `TodoListMiddleware` must have its `coroutine` attribute set to the new async function. The tool is identified by name `"write_todos"`.

3. **Correct delegation**: The async function must produce the same result as calling `_write_todos(runtime, todos)`.

4. **Code quality**: The implementation must pass:
   - `ruff check` linting
   - `ruff format --diff` formatting
   - `mypy` type checking
   - All existing middleware unit tests

5. **Import compatibility**: The module must remain importable and export `TodoListMiddleware`, `_write_todos`, `Todo`, `WriteTodosInput`, and `PlanningState`.

## Verification

The fix is correct when:
- `asyncio.iscoroutinefunction(new_async_function)` returns `True`
- `write_todos_tool.coroutine is new_async_function` is `True`
- An async agent can call `write_todos` and receive correct results
- All upstream tests pass