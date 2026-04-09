# Selenium .NET BiDi Event Deserialization Refactor

## Problem

The Selenium .NET BiDi (Bidirectional WebDriver Protocol) implementation currently deserializes event parameters in the background event processing thread (`EventDispatcher.ProcessEventsAwaiterAsync`). This approach:

1. Delays memory reuse at the transport layer
2. Adds complexity by passing around byte arrays and JSON type info
3. Defers error handling for unknown event types

## Goal

Refactor the event handling pipeline to **deserialize events immediately at the transport layer** (in `Broker.ProcessReceivedMessage`) before enqueueing them. This allows:

- Faster memory reuse by the transport layer
- Simpler event dispatcher that works with typed objects
- Earlier validation and logging of unknown event types

## Files to Modify

### 1. `dotnet/src/webdriver/BiDi/Broker.cs`

The `ProcessReceivedMessage` method currently:
- Tracks byte indices (`paramsStartIndex`, `paramsEndIndex`) to slice the raw message
- Passes byte data to `EventDispatcher.EnqueueEvent`

**Change to:**
- Use a `Utf8JsonReader` snapshot (`paramsReader`) when the "params" property is encountered
- Check if the event type is registered using a new method on `EventDispatcher`
- Deserialize the event args immediately using `JsonSerializer.Deserialize`
- Assign the `BiDi` instance to the event args
- Pass the deserialized `EventArgs` object (not bytes) to `EventDispatcher.EnqueueEvent`
- Move the warning log for unknown event types from `EventDispatcher` to here

### 2. `dotnet/src/webdriver/BiDi/EventDispatcher.cs`

**Rename:**
- The field `_events` → `_eventRegistrations` (be consistent everywhere)

**Add method:**
- `TryGetJsonTypeInfo(string eventName, out JsonTypeInfo jsonTypeInfo)` - allows Broker to check if an event type is registered before deserializing

**Change `EnqueueEvent` signature:**
- From: `EnqueueEvent(string method, ReadOnlyMemory<byte> jsonUtf8Bytes, IBiDi bidi)`
- To: `EnqueueEvent(string method, EventArgs eventArgs)`

**Change `PendingEvent` record struct:**
- From: `PendingEvent(string Method, ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, JsonTypeInfo TypeInfo)`
- To: `PendingEvent(string Method, EventArgs EventArgs)`

**Update `ProcessEventsAwaiterAsync`:**
- Remove the `JsonSerializer.Deserialize` call (now done in Broker)
- Remove the `eventArgs.BiDi = result.BiDi` assignment (now done in Broker)
- Just invoke handlers with the pre-deserialized event args

## Key Constraints

1. The warning log message for unknown events should now come from `Broker`, not `EventDispatcher`
2. The `isParams` boolean flag used to track the params end index is no longer needed
3. The `System.Diagnostics.CodeAnalysis` namespace should be used for the `NotNullWhen` attribute
4. Do NOT use `System.Text.Json` in `EventDispatcher` (it's no longer needed there)

## Testing

The existing tests should pass. The refactoring should not change any external behavior—only the internal processing order.

## Hints

- Look for patterns like `paramsStartIndex`, `paramsEndIndex`, `isParams` in `Broker.cs`
- Check how `EnqueueEvent` is called in `Broker.cs` to understand the new flow
- The `EventArgs.BiDi` property assignment moves from `EventDispatcher` to `Broker`
