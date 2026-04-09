# Channel model refactor: Explicit states/simplify

## Problem

The current channel model uses a state machine with generic states that don't clearly represent the channel's operational phase:
- `idle` (0) - channel is idle
- `offer` (1) - ambiguous: could be sender or receiver making offer (distinguished by `v` being nil or non-nil)
- `accepted` (2) - offer was accepted
- `closed` (3) - channel is closed

This design relies on pointer nullity (`v *T`) to distinguish between sender and receiver offers, which is error-prone and doesn't work well with empty slices/structs. The code also uses separate helper methods (`BufferedTrySend`, `UnbufferedTrySend`, etc.) that create unnecessary complexity.

## Expected Behavior

Refactor the channel model to use explicit, self-documenting state constants that align with the mathematical representation:
- `Buffered` (0) - buffered channel state
- `Idle` (1) - unbuffered channel idle
- `SndWait` (2) - sender is waiting to complete exchange
- `RcvWait` (3) - receiver is waiting to complete exchange
- `SndDone` (4) - sender has completed exchange
- `RcvDone` (5) - receiver has completed exchange
- `Closed` (6) - channel is closed

Key changes:
1. Replace `v *T` with `v T` (value instead of pointer)
2. Unify `TrySend` and `TryReceive` to handle both buffered and unbuffered channels via switch statements on state
3. Remove helper methods: `BufferedTrySend`, `BufferedTryReceive`, `UnbufferedTrySend`, `UnbufferedTryReceive`
4. Refactor `Send` and `Receive` to use simple for loops around `TrySend`/`TryReceive` instead of `Select1`
5. Replace if-else chains with switch statements for state handling

## Files to Look At

- `model/channel/channel.go` - main channel implementation file
