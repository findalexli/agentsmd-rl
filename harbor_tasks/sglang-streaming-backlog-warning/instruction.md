# Noisy per-request warning spam in streaming responses

## Problem

When the SGLang server handles streaming requests under moderate to high concurrency, the `_wait_one_response` method in `python/sglang/srt/managers/tokenizer_manager.py` emits a `WARNING`-level log message every time more than one chunk is pending in the output queue for a given request.

The message looks like:

```
WARNING - Streaming backlog: rid=..., draining N queued chunks. This may inflate P99 TBT for affected requests.
```

Under normal asyncio scheduling, it is perfectly expected for multiple chunks to accumulate between event-loop ticks. This is not an anomaly — it is standard behavior. The warning fires on nearly every streaming request at any reasonable concurrency level, flooding logs and making it difficult to spot genuinely important warnings.

## Expected behavior

The server should not log a warning for normal chunk batching during streaming. The drain loop that processes all pending chunks should still work correctly — it just shouldn't warn about doing its job.

## Relevant code

- `python/sglang/srt/managers/tokenizer_manager.py` — look at the `_wait_one_response` async method, specifically the section that drains `state.out_list` for streaming requests.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `black (Python formatter)`
