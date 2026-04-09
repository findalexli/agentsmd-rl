# Qwen3 tool parsers return all parameter values as strings for Responses API tools

## Problem

When using the OpenAI Responses API tool format (`FunctionTool` with flat `.name` / `.parameters` structure) with the Qwen3Coder or Qwen3XML tool parsers, all tool call parameter values are returned as strings regardless of their declared type in the tool schema.

For example, if a tool declares a parameter `precision` with `"type": "integer"`, the parser returns `"3"` (a string) instead of `3` (an integer). Similarly, parameters of type `"object"` are returned as stringified JSON like `"{\"radius\": 5.0}"` instead of the parsed dict `{"radius": 5.0}`.

This only happens with Responses API tools. The standard Chat Completion tools (`ChatCompletionToolsParam`) with the nested `.function.name` / `.function.parameters` structure work correctly.

## Expected Behavior

Both Qwen3 tool parsers should correctly resolve parameter types from the tool schema regardless of whether the tools are provided in the Chat Completion format or the Responses API format. Integer parameters should be returned as integers, object parameters as dicts, etc.

## Files to Look At

- `vllm/tool_parsers/qwen3coder_tool_parser.py` — Qwen3Coder tool parser, handles XML-based tool call extraction and parameter type conversion
- `vllm/tool_parsers/qwen3xml_tool_parser.py` — Qwen3XML tool parser, similar structure with its own parameter type resolution
- `vllm/tool_parsers/utils.py` — Shared tool parser utilities including `_extract_tool_info` which already handles both tool formats
