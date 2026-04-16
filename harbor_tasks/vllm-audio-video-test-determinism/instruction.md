# Fix flaky audio-in-video tests in CI

## Summary

The tests `test_online_audio_in_video` and `test_online_audio_in_video_multi_videos` in `tests/entrypoints/openai/chat_completion/test_audio_in_video.py` are intermittently failing in CI. These tests assert that model responses have `finish_reason == "length"` and `len(choices) == 1`, but the current generation parameters allow the model to complete naturally with `finish_reason="stop"` on some runs.

## Expected Behavior

Both test functions must reliably produce `finish_reason="length"` on every CI run. To achieve this determinism:

1. **Temperature**: The API call must use `temperature=0.0` to enforce deterministic sampling.

2. **Token limit**: The API call must set `max_tokens` (or `max_completion_tokens`) to a value no greater than 8, ensuring the model hits the token limit before completing naturally. The current value of 16 is too generous.

3. **Loop variable**: The `for` loop iterating over two turns must use `turn` (not `_` or any other name) as the loop variable. This is required for proper iteration context.

4. **Debug output**: Before the assertion checking `finish_reason`, the code must include diagnostic output that references `finish_reason`. This output must use a print statement (not logging) and must access `finish_reason` as an attribute on the choice object (e.g., `choice.finish_reason`).

## Constraints

- Both test functions must continue to pass `mm_processor_kwargs` with `use_audio_in_video=True`.
- The third test function `test_online_audio_in_video_interleaved` must remain unchanged.
- All existing repository pre-commit checks must pass (ruff lint/format, SPDX headers, forbidden imports, torch.cuda check, etc.).
