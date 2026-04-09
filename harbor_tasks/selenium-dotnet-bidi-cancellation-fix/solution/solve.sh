#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check: if already patched, exit
if grep -q "ReturnBuffer(sendBuffer);" dotnet/src/webdriver/BiDi/Broker.cs; then
    echo "Already patched"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/dotnet/src/webdriver/BiDi/Broker.cs b/dotnet/src/webdriver/BiDi/Broker.cs
index 278e6e46160b4..9611f3cadcec1 100644
--- a/dotnet/src/webdriver/BiDi/Broker.cs
+++ b/dotnet/src/webdriver/BiDi/Broker.cs
@@ -143,34 +143,39 @@ public async Task<TResult> ExecuteCommandAsync<TCommand, TResult>(TCommand com
             {
                 JsonSerializer.Serialize(writer, command, jsonCommandTypeInfo);
             }
+        }
+        catch
+        {
+            ReturnBuffer(sendBuffer);
+            throw;
+        }

-            var commandInfo = new CommandInfo(tcs, jsonResultTypeInfo);
-            _pendingCommands[command.Id] = commandInfo;
+        var commandInfo = new CommandInfo(tcs, jsonResultTypeInfo);
+        _pendingCommands[command.Id] = commandInfo;

-            using var ctsRegistration = cts.Token.Register(() =>
-            {
-                tcs.TrySetCanceled(cts.Token);
-                _pendingCommands.TryRemove(command.Id, out _);
-            });
+        using var ctsRegistration = cts.Token.Register(() =>
+        {
+            tcs.TrySetCanceled(cts.Token);
+            _pendingCommands.TryRemove(command.Id, out _);
+        });

-            try
+        try
+        {
+            if (_logger.IsEnabled(LogEventLevel.Trace))
             {
-                if (_logger.IsEnabled(LogEventLevel.Trace))
-                {
 #if NET8_0_OR_GREATER
-                    _logger.Trace($"BiDi SND --> {System.Text.Encoding.UTF8.GetString(sendBuffer.WrittenMemory.Span)}");
+                _logger.Trace($"BiDi SND --> {System.Text.Encoding.UTF8.GetString(sendBuffer.WrittenMemory.Span)}");
 #else
-                    _logger.Trace($"BiDi SND --> {System.Text.Encoding.UTF8.GetString(sendBuffer.WrittenMemory.ToArray())}");
+                _logger.Trace($"BiDi SND --> {System.Text.Encoding.UTF8.GetString(sendBuffer.WrittenMemory.ToArray())}");
 #endif
-                }
-
-                await _transport.SendAsync(sendBuffer.WrittenMemory, cts.Token).ConfigureAwait(false);
-            }
-            catch
-            {
-                _pendingCommands.TryRemove(command.Id, out _);
-                throw;
             }
+
+            await _transport.SendAsync(sendBuffer.WrittenMemory, cts.Token).ConfigureAwait(false);
+        }
+        catch
+        {
+            _pendingCommands.TryRemove(command.Id, out _);
+            throw;
         }
         finally
         {
PATCH

echo "Patch applied successfully"
