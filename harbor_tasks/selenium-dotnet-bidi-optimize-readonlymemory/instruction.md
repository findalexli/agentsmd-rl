# Optimize Selenium .NET BiDi Transport with ReadOnlyMemory

## Problem

The Selenium .NET BiDi (Bidirectional protocol) transport layer needs performance optimization. Currently, the `ITransport` interface and its `WebSocketTransport` implementation use `byte[]` arrays for sending data, which causes unnecessary allocations and copying. Additionally, the `Broker` class uses non-thread-safe methods to complete `TaskCompletionSource` operations.

## Files to Modify

1. **`dotnet/src/webdriver/BiDi/ITransport.cs`** - The transport interface
2. **`dotnet/src/webdriver/BiDi/WebSocketTransport.cs`** - WebSocket implementation
3. **`dotnet/src/webdriver/BiDi/Broker.cs`** - Message broker

## Required Changes

### 1. ITransport Interface

Change the `SendAsync` method signature to use modern .NET memory primitives:
- Return type should be `ValueTask` instead of `Task`
- Data parameter should be `ReadOnlyMemory<byte>` instead of `byte[]`

### 2. WebSocketTransport Implementation

Update the `SendAsync` implementation with conditional compilation:
- For **.NET 8 and later**: Use the native `ReadOnlyMemory<byte>` overload of `WebSocket.SendAsync`
- For **older .NET versions**: Use `MemoryMarshal.TryGetArray` to extract an `ArraySegment<byte>` from the `ReadOnlyMemory<byte>`
- Update the trace logging to work with both code paths

### 3. Broker Thread Safety

In `Broker.cs`, change the `TaskCompletionSource` completion methods to their thread-safe variants:
- Change `SetResult` to `TrySetResult`
- Change `SetException` to `TrySetException`

This prevents race conditions where multiple threads might try to complete the same task.

## Testing

Your changes should:
1. Compile successfully with `dotnet build`
2. Maintain the existing behavior (no functional changes, only performance/robustness)
3. Use proper conditional compilation directives (`#if NET8_0_OR_GREATER`)

## Hints

- The `MemoryMarshal.TryGetArray` method can extract an underlying array from a `ReadOnlyMemory<byte>`
- When using `ArraySegment`, you need to account for `Offset` and `Count` when converting to string for logging
- `TrySetResult` and `TrySetException` are safer in concurrent scenarios than their non-Try counterparts
