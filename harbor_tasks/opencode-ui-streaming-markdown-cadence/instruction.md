# Streamed markdown feels choppy during assistant responses

## Problem

When the assistant is streaming a response, the rendered markdown text arrives in visible "bursts" rather than feeling like smooth, continuous typing. Long markdown answers and reasoning traces are particularly affected — you can see chunks of text appearing at once with noticeable pauses between them.

The issue is in the text rendering pipeline in `packages/ui/src/components/message-part.tsx`. The current approach uses a simple time-based throttle (100ms) to limit how often the displayed text updates. This means:

1. Text accumulates in a buffer during the throttle window
2. When the window expires, the entire accumulated chunk is revealed at once
3. This creates a "staircase" effect — nothing visible for ~100ms, then a burst of text

The throttle is applied uniformly regardless of whether the stream is still active or has completed, and it doesn't account for the size of the pending text.

## Expected behavior

- Streamed text should reveal in small, steady increments that feel like real-time typing
- When backlog builds up, it should catch up quickly but still smoothly
- When the response is complete (not streaming), text should flush immediately
- Both assistant text parts and reasoning parts should feel consistent

## Relevant code

- `packages/ui/src/components/message-part.tsx`
  - `createThrottledValue()` — the current throttle implementation
  - `TextPartDisplay` component (search for `PART_MAPPING["text"]`)
  - `ReasoningPartDisplay` component (search for `PART_MAPPING["reasoning"]`)
