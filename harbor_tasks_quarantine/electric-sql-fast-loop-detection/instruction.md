# Task: Add fast-loop detection to the Elixir client

## What is broken

The Elixir client (`packages/elixir-client`) has no protection against servers or CDNs that cause repeated HTTP 200 responses at the same offset without progress. When this happens, the client loops indefinitely, hammering the server.

The TypeScript client already has fast-loop detection that handles this case. The Elixir client is missing it.

## Symptom

A buggy proxy or CDN that returns `200 OK` with the same `last_offset` value repeatedly — but never sends an `up-to-date` control message — causes the client to poll forever without detecting that no progress is being made. After the first detection the client clears its caches and retries; after several consecutive detections it raises an error instead of continuing indefinitely.

## What to implement

Implement fast-loop detection in the Elixir client that mirrors the TypeScript client's behavior. The implementation must modify two files:

- `packages/elixir-client/lib/electric/client/shape_state.ex` — core detection logic
- `packages/elixir-client/lib/electric/client/stream.ex` — integration with the fetch loop

### Behavior requirements

The fast-loop detection must:

1. Track recent request offsets within a sliding window. When enough requests occur at the same offset within that window, a fast-loop condition is detected.
2. On first detection: immediately clear the shape handle and reset the offset (backoff = 0) so the client can re-subscribe from scratch.
3. On subsequent detections: apply exponential backoff before retrying.
4. After several consecutive fast-loop detections without any progress, raise a `Client.Error` instead of continuing to poll.
5. When the stream transitions to live/up-to-date mode, reset all fast-loop tracking state.

### Required interface

The implementation must expose the following in `ShapeState`:

- A function `check_fast_loop/1` — takes the current shape state and returns either an updated state or signals that a fast-loop condition was detected (via `{:ok, state}`, `{:backoff, ms, state}`, or `{:error, message}`).
- A function `clear_fast_loop/1` — resets all fast-loop tracking state.

The `ShapeState` struct must be extended with fields to track recent requests and consecutive detection count.

Module attributes define the detection thresholds (window size, request count threshold, max consecutive count).

### Stream integration

In `stream.ex`, the fetch path must call `check_fast_loop` to invoke detection on each iteration. When transitioning to live/up-to-date mode, it must call `clear_fast_loop` to reset tracking.

## Verification

After implementation:
- A test file `test/electric/client/shape_state_test.exs` should exist with 8 passing tests
- Run `mix test` in `packages/elixir-client` — all existing tests must continue to pass
- Run `mix format --check-formatted` — formatting should be clean
- Run `mix compile --force --all-warnings --warnings-as-errors` — no warnings

## What not to do

- Do not modify test files
- Do not change the existing API surface of the client
- Do not add dependencies