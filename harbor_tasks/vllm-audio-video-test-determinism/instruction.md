# Flaky audio-in-video CI tests due to non-deterministic generation

## Summary

Two tests in `tests/entrypoints/openai/chat_completion/test_audio_in_video.py` are intermittently failing in CI. The tests `test_online_audio_in_video` and `test_online_audio_in_video_multi_videos` assert that `finish_reason == "length"`, but sometimes the model completes its response naturally and returns `finish_reason='stop'` instead.

## Context

These tests exercise the OpenAI-compatible chat completion endpoint with video inputs that include audio tracks (`use_audio_in_video=True`). Each test runs two turns (to exercise the multimodal processor cache) and expects the model to hit the token limit before finishing its response.

The problem is that the generation parameters don't enforce deterministic output. Without controlling the sampling behavior, the output length varies across runs — sometimes the model finishes within the token budget, sometimes it doesn't.

The current token limit of 16 is too generous, giving the model enough room to complete a response naturally on some runs.

## Relevant files

- `tests/entrypoints/openai/chat_completion/test_audio_in_video.py` — the two flaky test functions

## Required changes

Both flaky test functions must be updated as follows:

1. **Deterministic output**: Set `temperature=0.0` on the `client.chat.completions.create()` call to force deterministic sampling.
2. **Token limit**: Reduce `max_tokens` (or `max_completion_tokens`) to a value **no greater than 8** so the model reliably hits the token limit before completing naturally.
3. **Loop variable name**: The `for` loop over the two turns must use `turn` (not `_`) as the loop variable.
4. **Debug output**: Add a `print()` call (not `logger.debug` or other logging) with an f-string that includes `finish_reason` accessed as an attribute on the choice object (e.g., `choice.finish_reason`). The print must appear before the assertion.

## Expected behavior

Both tests should reliably produce `finish_reason='length'` on every run, and include enough diagnostic output to debug failures if they recur.
