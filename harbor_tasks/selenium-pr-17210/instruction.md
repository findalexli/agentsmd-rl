# Task: Thread-Safe Events Registration in .NET BiDi EventDispatcher

## Problem

The `EventDispatcher` class in the Selenium .NET BiDi implementation has a thread-safety issue with event handler management. Currently, event handlers are stored in a `List<EventHandler>` which is not thread-safe. When multiple threads concurrently register/unregister handlers while events are being processed, this can cause:

1. Race conditions during handler addition/removal
2. `InvalidOperationException` when the collection is modified while being iterated
3. Potential data corruption in the handler list

## Files to Modify

- `dotnet/src/webdriver/BiDi/EventDispatcher.cs` - The main file containing the `EventDispatcher` class and its nested `EventRegistration` class

## Required Changes

Refactor the `EventRegistration` class to use a thread-safe copy-on-write pattern:

1. Replace the `List<EventHandler> Handlers` property with a volatile `EventHandler[]` array field
2. Add a private `object` lock field for synchronization
3. Implement `GetHandlers()` method that returns the current array
4. Implement `AddHandler(EventHandler)` that uses `lock` and creates a new array with the handler appended
5. Implement `RemoveHandler(EventHandler)` that uses `lock` and creates a new array with the handler filtered out
6. Update `ProcessEventsAwaiterAsync()` to use `GetHandlers()` instead of `Handlers.ToArray()`
7. Update `SubscribeAsync()` to use `AddHandler()` instead of `Handlers.Add()`
8. Update `UnsubscribeAsync()` to use `RemoveHandler()` instead of `Handlers.Remove()`

## Key Implementation Details

- The copy-on-write pattern means every modification creates a new array, avoiding modification-during-iteration issues
- Use `lock (_lock)` to ensure thread-safe updates to the array reference
- The `volatile` keyword ensures the array reference is always read from main memory
- Handler iteration in `ProcessEventsAwaiterAsync` should use the returned array directly (it's already a copy)

## Testing Your Fix

The .NET project should build successfully:
```bash
cd /workspace/selenium
dotnet build dotnet/src/webdriver/webdriver.csproj -c Release
```

## Reference

According to the repository's agent configuration:
- Maintain API/ABI compatibility (internal refactoring, public API unchanged)
- The codebase is migrating to async patterns
- Use XML documentation for public APIs
