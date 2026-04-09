# Selenium .NET BiDi Broker Cancellation Fix

## Problem

The `ExecuteCommandAsync` method in `dotnet/src/webdriver/BiDi/Broker.cs` has a bug where the `ctsRegistration` (cancellation token registration) is disposed too early. This prevents commands from being properly cancelled when a timeout occurs.

## Symptom

When a command times out, the cancellation callback should fire and cancel the associated `TaskCompletionSource`. However, due to incorrect scoping of the `using var ctsRegistration`, the registration is disposed before the command completes, meaning the timeout cancellation never triggers.

## Code Location

The bug is in the `ExecuteCommandAsync` method in `dotnet/src/webdriver/BiDi/Broker.cs`. The method has the following structure:

1. Creates a `TaskCompletionSource` for the command result
2. Creates a `CancellationTokenSource` with timeout
3. Rents a buffer for sending the command
4. Serializes the command to the buffer
5. Registers a cancellation callback that should cancel the TCS when timeout fires
6. Sends the command via transport
7. Returns the result

## What Needs Fixing

The `ctsRegistration` (the cancellation token registration) is currently scoped inside a try block that ends before the command is fully sent and awaited. When the `using` declaration goes out of scope, the registration is disposed, disabling the cancellation mechanism.

The fix needs to restructure the try/catch/finally blocks so that:

1. **Serialization errors** are caught and the buffer is returned immediately (currently missing)
2. The **ctsRegistration** stays alive during the entire `await _transport.SendAsync()` call
3. The buffer management remains correct in all error paths

## Hints

- Look at how `ReturnBuffer(sendBuffer)` is called - there's currently only one call site in a finally block
- The `using var ctsRegistration = cts.Token.Register(...)` needs to be outside the try block that contains the transport send
- Consider what happens if JSON serialization fails - where is the buffer returned?
- The method should have two separate try blocks with proper error handling between them

## Expected Behavior

After the fix:
- If JSON serialization fails, the buffer should be returned immediately in a catch block
- The cancellation registration should remain active during the entire transport send operation
- If the transport send fails, the pending command should be cleaned up (existing behavior)
- The buffer should be returned in the finally block after the send completes (existing behavior)
