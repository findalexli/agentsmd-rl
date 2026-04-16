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

The drain mechanism and its synchronization infrastructure must be removed:
- Any method that blocks waiting for pending events to be processed must be removed entirely
- Sequence tracking fields that monitor enqueue/processing counts must be removed
- Lists or locks used specifically for drain coordination must be removed
- The event data structure should be changed to store the method name directly as a field

The handler management should be simplified:
- Instead of AddHandler/RemoveHandler methods with a snapshot-based iteration pattern, handlers should be exposed via a public property
- Handler iteration should use a thread-safe copying pattern (such as ToArray()) to avoid modification during iteration

The async task creation should be refactored:
- Task creation should use a TaskFactory with specific options (DenyChildAttach, None, Default)
- The internal task field should be renamed to reflect its emitter role
- The processing method should be renamed to indicate it returns an awaiter-style task

The subscription flow should be simplified:
- Subscribe should call the session provider before adding the handler, with direct list manipulation
- Unsubscribe should remove the handler without any drain wait

## File

Modify: `dotnet/src/webdriver/BiDi/EventDispatcher.cs`
