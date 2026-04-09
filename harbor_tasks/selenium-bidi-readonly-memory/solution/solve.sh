#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for the BiDi ReadOnlyMemory optimization
cat > /tmp/fix.patch << 'PATCH'
diff --git a/dotnet/src/webdriver/BiDi/Broker.cs b/dotnet/src/webdriver/BiDi/Broker.cs
index c1f02b398b50c..0886574e30e8f 100644
--- a/dotnet/src/webdriver/BiDi/Broker.cs
+++ b/dotnet/src/webdriver/BiDi/Broker.cs
@@ -192,11 +192,11 @@ private void ProcessReceivedMessage(byte[] data)
                         var commandResult = JsonSerializer.Deserialize(ref resultReader, command.JsonResultTypeInfo)
                             ?? throw new BiDiException("Remote end returned null command result in the 'result' property.");

-                        command.TaskCompletionSource.SetResult((EmptyResult)commandResult);
+                        command.TaskCompletionSource.TrySetResult((EmptyResult)commandResult);
                     }
                     catch (Exception ex)
                     {
-                        command.TaskCompletionSource.SetException(ex);
+                        command.TaskCompletionSource.TrySetException(ex);
                     }
                     finally
                     {
@@ -224,7 +224,7 @@ private void ProcessReceivedMessage(byte[] data)

                 if (_pendingCommands.TryGetValue(id.Value, out var errorCommand))
                 {
-                    errorCommand.TaskCompletionSource.SetException(new BiDiException($"{error}: {message}"));
+                    errorCommand.TaskCompletionSource.SetException(new BiDiException($"{error}: {message}"));
                     _pendingCommands.TryRemove(id.Value, out _);
                 }
                 else
diff --git a/dotnet/src/webdriver/BiDi/ITransport.cs b/dotnet/src/webdriver/BiDi/ITransport.cs
index f202535253c7b..b40f531ad249b 100644
--- a/dotnet/src/webdriver/BiDi/ITransport.cs
+++ b/dotnet/src/webdriver/BiDi/ITransport.cs
@@ -23,5 +23,5 @@ interface ITransport : IAsyncDisposable
 {
     Task<byte[]> ReceiveAsync(CancellationToken cancellationToken);

-    Task SendAsync(byte[] data, CancellationToken cancellationToken);
+    ValueTask SendAsync(ReadOnlyMemory<byte> data, CancellationToken cancellationToken);
 }
diff --git a/dotnet/src/webdriver/BiDi/WebSocketTransport.cs b/dotnet/src/webdriver/BiDi/WebSocketTransport.cs
index 6b0920500b6d3..11466bc17bbb2 100644
--- a/dotnet/src/webdriver/BiDi/WebSocketTransport.cs
+++ b/dotnet/src/webdriver/BiDi/WebSocketTransport.cs
@@ -96,18 +96,32 @@ public async Task<byte[]> ReceiveAsync(CancellationToken cancellationToken)
         }
     }

-    public async Task SendAsync(byte[] data, CancellationToken cancellationToken)
+    public async ValueTask SendAsync(ReadOnlyMemory<byte> data, CancellationToken cancellationToken)
     {
         await _socketSendSemaphoreSlim.WaitAsync(cancellationToken).ConfigureAwait(false);

         try
         {
+#if NET8_0_OR_GREATER
             if (_logger.IsEnabled(LogEventLevel.Trace))
             {
-                _logger.Trace($"BiDi SND --> {Encoding.UTF8.GetString(data)}");
+                _logger.Trace($"BiDi SND --> {Encoding.UTF8.GetString(data.Span)}");
             }

-            await _webSocket.SendAsync(new ArraySegment<byte>(data), WebSocketMessageType.Text, true, cancellationToken).ConfigureAwait(false);
+            await _webSocket.SendAsync(data, WebSocketMessageType.Text, true, cancellationToken).ConfigureAwait(false);
+#else
+            if (!System.Runtime.InteropServices.MemoryMarshal.TryGetArray(data, out ArraySegment<byte> segment))
+            {
+                segment = new ArraySegment<byte>(data.ToArray());
+            }
+
+            if (_logger.IsEnabled(LogEventLevel.Trace))
+            {
+                _logger.Trace($"BiDi SND --> {Encoding.UTF8.GetString(segment.Array!, segment.Offset, segment.Count)}");
+            }
+
+            await _webSocket.SendAsync(segment, WebSocketMessageType.Text, true, cancellationToken).ConfigureAwait(false);
+#endif
         }
         finally
         {
PATCH

# Apply the patch
git apply /tmp/fix.patch

# Idempotency check: verify the distinctive line exists
grep -q "ValueTask SendAsync(ReadOnlyMemory<byte> data" dotnet/src/webdriver/BiDi/ITransport.cs
echo "Patch applied successfully"
