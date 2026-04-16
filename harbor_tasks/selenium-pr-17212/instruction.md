# BiDi Event Deserialization Refactoring

The Selenium .NET WebDriver's BiDi (Browser Interface for Debugging) implementation currently deserializes events on a background thread in `EventDispatcher`. This causes memory inefficiency, delayed validation, and mixed responsibilities.

## Problem

When `EventDispatcher` receives raw JSON bytes from the `Broker`, it holds them in memory and deserializes them on a background thread via `ProcessEventsAwaiterAsync`. This approach:
- Prevents the transport layer from reusing memory buffers
- Defers validation of event type mappings until background processing
- Mixes event routing with JSON deserialization concerns

## Goal

Move event deserialization to the transport layer (`Broker`) so that events are deserialized immediately when received and the `EventDispatcher` receives already-deserialized `EventArgs` objects.

## Required Changes

### Broker.cs

The network message processor (`dotnet/src/webdriver/BiDi/Broker.cs`) must be updated to deserialize events on the network thread before passing to the event dispatcher:

1. **Capture a `Utf8JsonReader` snapshot** for the event parameters (the variable should be named `paramsReader`, captured via `paramsReader = reader`)
2. **Validate event type mapping exists** by calling `_eventDispatcher.TryGetJsonTypeInfo(method, out var jsonTypeInfo)` before deserializing
3. **Deserialize on the network thread** using `JsonSerializer.Deserialize(ref paramsReader, jsonTypeInfo)`
4. **Log a warning** containing the phrase `"no event type mapping was found"` when no type mapping exists for an event
5. **Remove the old byte-index tracking** approach (the `paramsStartIndex` and `paramsEndIndex` variables)

### EventDispatcher.cs

The event queuing system (`dotnet/src/webdriver/BiDi/EventDispatcher.cs`) must be refactored to work with deserialized events:

1. **Add a lookup method** `TryGetJsonTypeInfo` with the exact signature:
   ```csharp
   public bool TryGetJsonTypeInfo(string eventName, [NotNullWhen(true)] out JsonTypeInfo? jsonTypeInfo)
   ```
   This requires importing `System.Diagnostics.CodeAnalysis` for the `[NotNullWhen(true)]` attribute.

2. **Rename the internal field** from `_events` to `_eventRegistrations` (a `ConcurrentDictionary<string, EventRegistration>`)

3. **Update `EnqueueEvent`** to accept `EventArgs` directly with the signature:
   ```csharp
   public void EnqueueEvent(string method, EventArgs eventArgs)
   ```
   The old signature that accepted `ReadOnlyMemory<byte>` and `IBiDi` should be removed.

4. **Simplify `PendingEvent`** to the struct:
   ```csharp
   private readonly record struct PendingEvent(string Method, EventArgs EventArgs);
   ```

## Files to Modify

- `dotnet/src/webdriver/BiDi/Broker.cs` - Move deserialization to network thread
- `dotnet/src/webdriver/BiDi/EventDispatcher.cs` - Accept deserialized events, add type lookup
