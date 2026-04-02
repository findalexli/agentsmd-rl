# Flaky audio-in-video CI tests due to non-deterministic generation

## Summary

Two tests in `tests/entrypoints/openai/chat_completion/test_audio_in_video.py` are intermittently failing in CI. The tests `test_online_audio_in_video` and `test_online_audio_in_video_multi_videos` assert that `finish_reason == "length"`, but sometimes the model completes its response naturally and returns `finish_reason='stop'` instead.

## Context

These tests exercise the OpenAI-compatible chat completion endpoint with video inputs that include audio tracks (`use_audio_in_video=True`). Each test runs two turns (to exercise the multimodal processor cache) and expects the model to hit the token limit before finishing its response.

The problem is that the generation parameters don't enforce deterministic output. Without controlling the sampling behavior, the output length varies across runs — sometimes the model finishes within the token budget, sometimes it doesn't.

Additionally, the current token limit may be too generous, giving the model enough room to complete a response naturally on some runs.

## Relevant files

- `tests/entrypoints/openai/chat_completion/test_audio_in_video.py` — the two flaky test functions

## Expected behavior

Both tests should reliably produce `finish_reason='length'` on every run, and include enough diagnostic output to debug failures if they recur.
