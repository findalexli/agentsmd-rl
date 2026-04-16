# Speed Up TodoListMiddleware Initialization

## Problem

The `TodoListMiddleware` class in `libs/langchain_v1/langchain/agents/middleware/todo.py` has slow initialization. The `@tool` decorator and function defined dynamically inside `__init__` creates overhead on each instantiation.

## Symptom

- Initialization is slow when many `TodoListMiddleware` instances are created
- Dynamic tool creation inside `__init__` causes performance overhead

## Goal

Optimize `TodoListMiddleware` initialization so tool creation does not happen inside `__init__`.

## Requirements

The solution must achieve:

1. **Fast instantiation**: 100 instantiations should complete in under 1 second
2. **`middleware.tools[0]` is a `StructuredTool`**: The tool is properly typed with name `"write_todos"`
3. **`WriteTodosInput` is a valid Pydantic model**: The input schema is defined with a `todos` property in its JSON schema
4. **Direct imports, not `TYPE_CHECKING`**: All imports are at module level

## What to Change

The current code uses `TYPE_CHECKING` blocks for some imports and creates the tool dynamically inside `__init__` with the `@tool` decorator. The solution should:

- Move imports to module level (not conditionally under `TYPE_CHECKING`)
- Remove `from __future__ import annotations`
- Define a standalone function for the tool logic
- Use `StructuredTool.from_function()` with `args_schema=WriteTodosInput` and `infer_schema=False` to create the tool

## File to Modify

`libs/langchain_v1/langchain/agents/middleware/todo.py`

## Verification

After changes:
- `TodoListMiddleware()` should instantiate without errors
- `middleware.tools[0]` should be a `StructuredTool` instance named `"write_todos"`
- `WriteTodosInput` should be a valid Pydantic model with `todos` in its schema
- 100 instantiations should complete in under 1 second
- All existing unit tests should pass
- Lint checks should pass