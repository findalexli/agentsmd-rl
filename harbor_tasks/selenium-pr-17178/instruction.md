# BiDi EventDispatcher Simplification

The `EventDispatcher` class in `dotnet/src/webdriver/BiDi/EventDispatcher.cs` has become overly complex due to a blocking drain mechanism that waits for pending events during unsubscription. This approach introduces potential deadlock risks and tightly couples event registration with event processing state.

## Goal

Simplify the `EventDispatcher` by removing the blocking drain infrastructure while preserving core event handling functionality.

## What Must Be Preserved

The simplified implementation must retain:
- `internal sealed class EventDispatcher` implementing `IAsyncDisposable`
- `Channel<T>` for pending events (type parameter may change)
- `ConcurrentDictionary<string, EventRegistration>` for event storage
- `SubscribeAsync`, `UnsubscribeAsync`, `EnqueueEvent`, `DisposeAsync` methods
- `EventRegistration` nested class structure
- Thread-safe handler iteration (must remain safe under concurrent modification)
- Proper async task lifecycle management

## Required Simplifications

### 1. Remove the drain mechanism

The drain mechanism and its synchronization infrastructure must be removed entirely:
- **Remove** the `DrainAsync` method from `EventRegistration`
- **Remove** sequence tracking fields: `_enqueueSeq` and `_processedSeq`
- **Remove** drain coordination objects: `_drainLock` and `_drainWaiters`

### 2. Rename the event data structure

The channel's data structure must be replaced:
- **Remove** `record EventItem(ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, EventRegistration Registration)`
- **Add** a `readonly record struct PendingEvent(string Method, ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, JsonTypeInfo TypeInfo)`
  - The `Method` field (a `string`) must be the first parameter — this stores the method name directly
  - Replace `Registration` field with `TypeInfo` field

### 3. Simplify handler management

Replace the `AddHandler`/`RemoveHandler`/`GetHandlersSnapshot` pattern:
- **Remove** `AddHandler(EventHandler handler)` method
- **Remove** `RemoveHandler(EventHandler handler)` method
- **Remove** `EventHandler[] GetHandlersSnapshot()` method
- **Add** public property `public List<EventHandler> Handlers { get; } = []` on `EventRegistration`

Handler iteration in the processing loop must use `.ToArray()` to create a thread-safe snapshot:
```csharp
foreach (var handler in registration.Handlers.ToArray()) // copy handlers avoiding modified collection while iterating
```

### 4. Refactor async task creation

Rename the internal task field and use `TaskFactory`:
- **Rename** `_processEventsTask` to `_eventEmitterTask`
- **Add** a static `TaskFactory` field:
  ```csharp
  private static readonly TaskFactory _myTaskFactory = new(CancellationToken.None, TaskCreationOptions.DenyChildAttach, TaskContinuationOptions.None, TaskScheduler.Default);
  ```
- **Change** task creation to use `TaskFactory.StartNew()`:
  ```csharp
  _eventEmitterTask = _myTaskFactory.StartNew(ProcessEventsAwaiterAsync).Unwrap();
  ```

### 5. Rename the processing method

- **Rename** `ProcessEventsAsync` to `ProcessEventsAwaiterAsync`

### 6. Simplify subscription flow

In `SubscribeAsync`, call the session provider before adding the handler:
```csharp
var subscribeResult = await _sessionProvider().SubscribeAsync([eventName], new() { Contexts = options?.Contexts, UserContexts = options?.UserContexts }, cancellationToken).ConfigureAwait(false);
registration.Handlers.Add(eventHandler);
return new Subscription(subscribeResult.Subscription, this, eventHandler);
```

In `UnsubscribeAsync`, remove the handler directly without any drain wait:
```csharp
registration.Handlers.Remove(subscription.EventHandler);
```

### 7. Update EnqueueEvent

Simplify the enqueue logic:
```csharp
if (_events.TryGetValue(method, out var registration) && registration.TypeInfo is not null)
{
    _pendingEvents.Writer.TryWrite(new PendingEvent(method, jsonUtf8Bytes, bidi, registration.TypeInfo));
}
```

### 8. Update event processing loop

The `ProcessEventsAwaiterAsync` method should:
- Read from `_pendingEvents` channel
- Use `result.Method` to look up registration
- Use `result.TypeInfo` (not `evt.Registration.TypeInfo`) for deserialization
- Use `result.BiDi` (not `evt.BiDi`) for setting on event args

## File to Modify

`dotnet/src/webdriver/BiDi/EventDispatcher.cs`