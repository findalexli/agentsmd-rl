# Optimize BiDi Transport Interface

## Problem

The BiDi (Bidirectional WebDriver protocol) transport layer in Selenium .NET uses inefficient memory patterns:

1. **ITransport.SendAsync** accepts `byte[]` which forces allocations when slicing or passing subsets of data
2. The method returns `Task` which allocates even for synchronous completions
3. **Broker.cs** uses `SetResult`/`SetException` which can throw if the task is already completed (race condition)
4. **WebSocketTransport** uses `ArraySegment<byte>` wrapper which is unnecessary on modern .NET

## Files to Modify

- `dotnet/src/webdriver/BiDi/ITransport.cs` - The transport interface
- `dotnet/src/webdriver/BiDi/WebSocketTransport.cs` - WebSocket implementation
- `dotnet/src/webdriver/BiDi/Broker.cs` - Command handling

## Requirements

### ITransport Interface Changes
- Change `SendAsync` signature from `Task SendAsync(byte[] data, ...)` to `ValueTask SendAsync(ReadOnlyMemory<byte> data, ...)`
- Keep `ReceiveAsync` unchanged (it already returns `Task<byte[]>` which is fine)

### WebSocketTransport Implementation
- Update `SendAsync` to accept `ReadOnlyMemory<byte>` and return `ValueTask`
- Add conditional compilation (`#if NET8_0_OR_GREATER`) to use the optimized WebSocket.SendAsync overload on .NET 8+
- For .NET 8+: pass `ReadOnlyMemory<byte>` directly to `WebSocket.SendAsync`
- For older .NET: extract `ArraySegment<byte>` using `MemoryMarshal.TryGetArray`, falling back to `ToArray()` if needed
- Update the trace logging to work with both code paths

### Broker Thread Safety
- Replace `command.TaskCompletionSource.SetResult(...)` with `TrySetResult(...)`
- Replace `command.TaskCompletionSource.SetException(...)` with `TrySetException(...)`

## Expected Behavior

After the changes:
- The code compiles without errors
- No behavioral changes for consumers (interface is internal)
- Reduced allocations when sending BiDi commands
- Thread-safe task completion (no race conditions)
- Works on both .NET 8+ and older frameworks

## Notes

- Use `System.Runtime.InteropServices.MemoryMarshal.TryGetArray` to extract ArraySegment
- The `Encoding.UTF8.GetString` overloads differ between .NET versions
- All changes are within the `dotnet/src/webdriver/BiDi/` directory
