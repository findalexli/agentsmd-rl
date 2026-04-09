# Add channel model to new goose

## Problem

The goose project needs a channel model implementation for the "new" branch to support Perennial verification. The channel model is currently missing from the new goose implementation, which blocks specs/proofs from being ported over.

## Expected Behavior

Add the channel model implementation that includes:

1. **Dependencies**: Add `goose-lang/primitive` and `goose-lang/std` to go.mod and go.sum
2. **Channel implementation**: Create `model/channel/channel.go` with a generic `Channel[T]` struct implementing:
   - Unbuffered and buffered channel semantics
   - Send/Receive operations (blocking and non-blocking)
   - Close operations
   - Select statement modeling (Select1-Select5)
   - State machine for unbuffered channel synchronization
3. **Documentation**: Create `model/channel/README.md` explaining the model characteristics and state diagram

## Files to Look At

- `go.mod` — Add required dependencies
- `go.sum` — Add dependency checksums
- `model/channel/channel.go` — New file: Channel model implementation
- `model/channel/README.md` — New file: Documentation with state diagram

## Implementation Notes

The channel model should:
- Use a generic struct in Go
- Store a buffered ring queue for buffered channels
- Use 4 boolean flags (as ChannelState enum) for unbuffered channel synchronization
- Branch on buffer capacity to determine buffered vs unbuffered behavior
- Provide TryReceive and TrySend functions for select statements
- Include a state machine diagram in the README
