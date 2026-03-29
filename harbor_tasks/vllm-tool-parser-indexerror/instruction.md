# Fix IndexError in OpenAI Tool Parser During Streaming

## Bug Description

In `vllm/entrypoints/openai/chat_completion/serving.py`, the `chat_completion_stream_generator` method has two related bugs in the streaming tool-call finalization logic (around lines 1089-1110):

1. **`index` referenced before assignment**: The variable `index` is only assigned inside an `else` branch (when `tool_parser` is None), but it is used unconditionally later. When `tool_parser` is not None but no tool calls were detected, `index` may be referenced before assignment.

2. **IndexError on `prev_tool_call_arr`**: The code calls `_should_check_for_unstreamed_tool_arg_tokens` and then accesses tool parser state even when no tool calls were actually detected by partial parsing (`auto_tools_called` is False). This can cause an `IndexError` when trying to access elements of `prev_tool_call_arr` that don't exist.

## What to Fix

In the `chat_completion_stream_generator` method, find the section that handles the final streaming chunk (around line 1089-1110 where `auto_tools_called` and `index` are set). Make the following corrections:

- Initialize `index = 0` **before** the `if tool_parser:` block so it always has a default value regardless of which branch executes.
- Ensure the check for unstreamed tool argument tokens only runs when tool calls were actually detected by partial parsing (i.e., when `auto_tools_called` is True), not just when a `tool_parser` exists.

## Acceptance Criteria

- `index` is always initialized before use, regardless of whether `tool_parser` is set.
- The unstreamed tool arg token check is guarded by `auto_tools_called` being True.
- The file remains syntactically valid Python.
- Existing streaming logic is preserved (no removal of core functionality).
