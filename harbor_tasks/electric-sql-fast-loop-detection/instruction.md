# Task: Add fast-loop detection to the Elixir client

## What is broken

The Elixir client (`packages/elixir-client`) has no protection against servers or CDNs that cause repeated HTTP 200 responses at the same offset without progress. When this happens, the client loops indefinitely, hammering the server.

The TypeScript client already has fast-loop detection that handles this case. The Elixir client is missing it.

## Symptom

A buggy proxy or CDN that returns `200 OK` with the same `last_offset` value repeatedly — but never sends an `up-to-date` control message — causes the client to poll forever without detecting that no progress is being made.

## What to implement

Implement fast-loop detection in the Elixir client that mirrors the TypeScript client's behavior. The implementation must modify two files:

- `packages/elixir-client/lib/electric/client/shape_state.ex` — core detection logic
- `packages/elixir-client/lib/electric/client/stream.ex` — integration with the fetch loop

### Behavior requirements

The fast-loop detection must:

1. Track recent request offsets within a sliding window of **500 ms**. When **5 or more** requests occur at the same offset within that window, a fast-loop condition is detected.
2. On first detection: immediately clear the shape handle and reset the offset (backoff = 0) so the client can re-subscribe from scratch.
3. On subsequent detections: apply exponential backoff before retrying.
4. After **5 consecutive** fast-loop detections without any progress, raise a `Client.Error` instead of continuing to poll.
5. When the stream transitions to live/up-to-date mode, reset all fast-loop tracking state.

### Required interface

The implementation must expose the following in `ShapeState`:

- A function `check_fast_loop/1` with spec `@spec check_fast_loop(t())` — takes the current shape state and returns either an updated state or signals that a fast-loop condition was detected.
- A function `clear_fast_loop/1` — resets all fast-loop tracking state.

The `ShapeState` struct must be extended with:
- `recent_requests: []` — list tracking recent request offsets within the sliding window
- `fast_loop_consecutive_count: 0` — counter for consecutive fast-loop detections

Module attributes for the detection thresholds:
- `@fast_loop_window_ms 500`
- `@fast_loop_threshold 5`
- `@fast_loop_max_count 5`

### Stream integration

In `stream.ex`, the fetch path must call `check_fast_loop(stream)` to invoke detection on each iteration. When transitioning to live/up-to-date mode, it must call `ShapeState.clear_fast_loop` to reset tracking.

## Verification

After implementation:
- Run `mix test test/electric/client/shape_state_test.exs` — this test file should report **8 tests**, all passing
- Run `mix test` in `packages/elixir-client` — all existing tests must continue to pass
- Run `mix format --check-formatted` — formatting should be clean
- Run `mix compile --force --all-warnings --warnings-as-errors` — no warnings

## What not to do

- Do not modify test files
- Do not change the existing API surface of the client
- Do not add dependencies
