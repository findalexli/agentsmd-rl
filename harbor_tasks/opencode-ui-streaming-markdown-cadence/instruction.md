# Streamed markdown feels choppy during assistant responses

## Problem

When the assistant is streaming a response, the rendered markdown text arrives in visible "bursts" rather than feeling like smooth, continuous typing. Long markdown answers and reasoning traces are particularly affected — you can see chunks of text appearing at once with noticeable pauses between them.

The issue is in the text rendering pipeline in `packages/ui/src/components/message-part.tsx`. The current approach uses a simple time-based throttle (`TEXT_RENDER_THROTTLE_MS = 100`) to limit how often the displayed text updates. This means:

1. Text accumulates in a buffer during the throttle window
2. When the window expires, the entire accumulated chunk is revealed at once
3. This creates a "staircase" effect — nothing visible for ~100ms, then a burst of text

The throttle is applied uniformly regardless of whether the stream is still active or has completed, and it doesn't account for the size of the pending text.

## Required Imports

The implementation must use these SolidJS primitives from `solid-js`:
- `createSignal`
- `createEffect`
- `onCleanup`
- `createMemo`

## Expected Behavior

- Streamed text should reveal in small, steady increments that feel like real-time typing
- Text must be revealed incrementally using substring/slice operations with position tracking (variables like `pos`, `shown`, `cursor`, or `idx`)
- The pacing should use step-based increments calculated with `Math.min`, `Math.ceil`, or `Math.floor`
- When backlog builds up, it should catch up quickly but still smoothly
- When the response is complete (not streaming), text should flush immediately without waiting
- The render pacing interval must be no more than 50ms (replace the current 100ms constant)
- Both assistant text parts and reasoning parts should feel consistent

## Implementation Requirements

- Create a new pacing function (to replace `createThrottledValue`) that:
  - Uses `createSignal` for reactive state (prefer `createStore` if multiple signals are needed; do NOT use multiple `createSignal` calls)
  - Uses `setTimeout` or `requestAnimationFrame` for scheduling
  - Accepts a second parameter (e.g., `live?: () => boolean`) to know whether the stream is still active (`streaming`, `live`, `isStreaming`, `isLive`, `active`, `isActive`, `running`, `flushed`, or `complete`)
  - Reveals text in small increments rather than all at once
  - Immediately flushes when not streaming
- Apply the pacing function to both components:
  - `PART_MAPPING["text"]` (TextPartDisplay)
  - `PART_MAPPING["reasoning"]` (ReasoningPartDisplay)
- Changed code must NOT use:
  - `any` type annotations
  - `try/catch` blocks
  - `else` statements

## Relevant Code

- `packages/ui/src/components/message-part.tsx`
  - `createThrottledValue()` — the current throttle implementation (to be replaced)
  - `TextPartDisplay` component (`PART_MAPPING["text"]`)
  - `ReasoningPartDisplay` component (`PART_MAPPING["reasoning"]`)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
