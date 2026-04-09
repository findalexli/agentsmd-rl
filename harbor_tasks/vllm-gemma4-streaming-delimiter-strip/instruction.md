# Fix invalid JSON in Gemma 4 streaming tool calls

## Problem

When using Gemma 4 with streaming tool calls enabled (`--tool-call-parser gemma4`), the streamed JSON arguments sometimes contain invalid characters that break JSON parsing on the client side.

The issue occurs when a token boundary happens to split the Gemma4 string delimiter (`<|"|>`) mid-sequence. Fragments like `<|` or `|>` leak into the streamed JSON argument text, producing output like `{"content": "Buy milk<|"}` which is not valid for downstream consumers expecting clean argument values.

The root cause is in the safe-prefix logic within the streaming argument emitter. The code withholds trailing characters that might shift as more tokens arrive, but it doesn't account for all characters that can appear as partial delimiter fragments.

## Expected Behavior

Streamed tool call arguments should always contain clean JSON values with no raw delimiter fragments. Partial delimiter characters should be withheld (along with other unstable trailing characters) until enough tokens have arrived to confirm the final value.

## Files to Look At

- `vllm/tool_parsers/gemma4_tool_parser.py` — the `_emit_argument_diff` method handles safe-prefix computation for streamed arguments. Look at the trailing character stripping logic.
