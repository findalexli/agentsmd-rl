# Streaming chat completions with n>1 produce corrupted tool calls

## Summary

When using the OpenAI-compatible chat completion endpoint with `stream=True`, `n > 1`, and tool calling enabled, all choices beyond the first produce corrupted or empty tool calls. The server logs show `IncompleteJSONError` exceptions. The same request with `n=1` works correctly.

## Context

The `chat_completion_stream_generator` method in `vllm/entrypoints/openai/chat_completion/serving.py` initializes per-choice state (token-ID history and tool-call parser instances) when streaming with automatic tool choice. This state is supposed to be independent for each choice so that each choice's tool-call tokens are parsed separately.

However, the current initialization causes all choices to inadvertently share the same mutable state. When choice 0's tokens are appended to its history, choices 1 through n-1 see the same mutations. Similarly, all choices feed tokens into the same parser instance, so the parser's internal state (partial JSON buffer, brace depth, etc.) is corrupted by interleaved tokens from different choices.

## Relevant files

- `vllm/entrypoints/openai/chat_completion/serving.py` — the `chat_completion_stream_generator` method, specifically the initialization of `all_previous_token_ids` and `tool_parsers` around lines 548–570

## Expected behavior

Each of the `n` choices should maintain fully independent token-ID histories and parser instances, so that streaming tool calls are correctly extracted for every choice.
