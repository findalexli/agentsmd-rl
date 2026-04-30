# docs: target Context7 benchmark gaps in Python skills [no-ci]

Source: [deepgram/deepgram-python-sdk#699](https://github.com/deepgram/deepgram-python-sdk/pull/699)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/deepgram-python-audio-intelligence/SKILL.md`
- `.agents/skills/deepgram-python-speech-to-text/SKILL.md`
- `.agents/skills/deepgram-python-voice-agent/SKILL.md`

## What to add / change

## Summary

Closes the four largest gaps in the Context7 benchmark for `/deepgram/deepgram-python-sdk`. Current score: **88.8/100** (mean across 10 standardized prompts). The 4 weakest prompts account for ~97 of the 112 missing points; this PR addresses each one specifically.

## What's broken (Context7 evaluator quotes)

| # | Prompt | Score | What's missing |
|---|---|---|---|
| 1 | Voice agent dynamic adjustment + stream restart/pause | **66** | "lacks specific guidance or API methods for dynamically adjusting transcription parameters during an active connection or for intelligently managing stream restarts and pauses beyond basic error events" |
| 2 | Live streaming with interim results display | **71** | "all examples show `interim_results=False`, which is the opposite of what's needed, and none demonstrate how to differentiate between interim and final results or how to handle the display logic" |
| 5 | Diarization + word-level timings combined | **83** | "lacks a specific, complete code example showing how to enable both diarization and word-level timings together in a single request" |
| 8 | Async URL transcription + retrieve final result | **83** | "lacks critical information about handling asynchronous results — doesn't explain how to retrieve the final transcription when using async methods or how to poll for results" |

## Changes

### `deepgram-python-voice-agent/SKILL.md` (+139 lines, prompt #1)

- **New "Dynamic mid-session adjustment" section** — runnable code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
