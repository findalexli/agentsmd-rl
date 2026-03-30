# Fix Hermes tool parser when stream interval > 1

## Bug Description

The `Hermes2ProToolParser` in `vllm/tool_parsers/hermes_tool_parser.py` fails to correctly parse tool calls when the stream interval is greater than 1. When multiple tokens arrive in a single chunk (as happens with `--stream-interval 2` or higher), the parser's `extract_tool_calls_streaming` method produces incorrect or missing tool call deltas.

The root cause is that the old streaming implementation uses a token-by-token buffering strategy (`tool_call_delta_buffer`) that assumes each call receives exactly one token. When multiple tokens arrive at once, the buffer logic breaks: tool call start/end tags may span chunks incorrectly, partial JSON parsing fails to diff correctly, and content text can be lost or duplicated.

Specific symptoms with `stream_interval > 1`:
- Tool call names may not be emitted
- Tool call arguments are incomplete or malformed JSON
- Content text before a tool call may be lost
- Multiple sequential tool calls may not be correctly separated

## Expected Fix

Rewrite the streaming logic to be robust to multi-token chunks. Instead of relying on token-by-token buffering, the parser should:

1. Re-parse the full `current_text` on each invocation to find `<tool_call>...</tool_call>` regions
2. Track what has been sent to the client (content index, tool names, streamed arguments per tool)
3. Diff against previously sent state to emit only new content, tool names, or argument fragments
4. Handle partial `<tool_call>` and `</tool_call>` tags that may be split across chunks

The `longcat_tool_parser.py` subclass also needs its redundant token-array attributes removed since the base class no longer uses them.

## Files to Modify

- `vllm/tool_parsers/hermes_tool_parser.py` -- the main parser rewrite
- `vllm/tool_parsers/longcat_tool_parser.py` -- remove inherited token-array attributes
