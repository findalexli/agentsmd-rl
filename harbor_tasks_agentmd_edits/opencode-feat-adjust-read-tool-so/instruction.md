# Fix error handling in Anthropic streaming message accumulation

## Problem

In `internal/llm/provider/anthropic.go`, the `stream()` function sends an error event to the channel when `accumulatedMessage.Accumulate(event)` fails. This causes the stream to terminate on recoverable accumulation errors, which is overly aggressive and interrupts the user experience.

The current code:
```go
err := accumulatedMessage.Accumulate(event)
if err != nil {
    eventChan <- ProviderEvent{Type: EventError, Error: err}
    continue
}
```

This sends an error event to the consumer, potentially breaking the streaming flow for minor issues that should just be logged.

## Expected Behavior

Instead of sending an error event, the function should:
1. Log a warning message with the error details
2. Continue processing subsequent events

This makes the stream more resilient to transient accumulation errors.

## Files to Look At

- `internal/llm/provider/anthropic.go` — The `stream()` function at line ~265 that handles message accumulation during streaming

## Implementation Hint

Use the existing `logging.Warn()` function from the `internal/logging` package to log the error instead of sending it as an event. The change should be at the location where `accumulatedMessage.Accumulate(event)` is called in the streaming loop.
