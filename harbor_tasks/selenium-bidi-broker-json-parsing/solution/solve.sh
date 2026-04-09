#!/bin/bash
set -e

cd /workspace/selenium

# Check if already patched (idempotency check)
if grep -q 'ValueTextEquals("id"u8)' dotnet/src/webdriver/BiDi/Broker.cs; then
    echo "Already patched"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/dotnet/src/webdriver/BiDi/Broker.cs b/dotnet/src/webdriver/BiDi/Broker.cs
index 0886574e30e8f..f9e34da0a15ff 100644
--- a/dotnet/src/webdriver/BiDi/Broker.cs
+++ b/dotnet/src/webdriver/BiDi/Broker.cs
@@ -118,71 +118,79 @@ public async ValueTask DisposeAsync()

     private void ProcessReceivedMessage(byte[] data)
     {
+        const int TypeSuccess = 1;
+        const int TypeEvent = 2;
+        const int TypeError = 3;
+
         long? id = default;
-        string? type = default;
+        int messageType = 0;
         string? method = default;
         string? error = default;
         string? message = default;
         Utf8JsonReader resultReader = default;
-        long paramsStartIndex = 0;
-        long paramsEndIndex = 0;
-
-        Utf8JsonReader reader = new(new ReadOnlySpan<byte>(data));
-        reader.Read();
+        int paramsStartIndex = 0;
+        int paramsEndIndex = 0;

+        Utf8JsonReader reader = new(data);
         reader.Read(); // "{"

+        reader.Read();
+
         while (reader.TokenType == JsonTokenType.PropertyName)
         {
-            string? propertyName = reader.GetString();
-            reader.Read();
+            bool isParams = false;

-            switch (propertyName)
+            if (reader.ValueTextEquals("id"u8))
             {
-                case "id":
-                    id = reader.GetInt64();
-                    break;
-
-                case "type":
-                    type = reader.GetString();
-                    break;
-
-                case "method":
-                    method = reader.GetString();
-                    break;
-
-                case "result":
-                    resultReader = reader; // snapshot
-                    break;
-
-                case "params":
-                    paramsStartIndex = reader.TokenStartIndex;
-                    break;
-
-                case "error":
-                    error = reader.GetString();
-                    break;
-
-                case "message":
-                    message = reader.GetString();
-                    break;
+                reader.Read();
+                id = reader.GetInt64();
             }
-
-            if (propertyName == "params")
+            else if (reader.ValueTextEquals("type"u8))
+            {
+                reader.Read();
+                if (reader.ValueTextEquals("success"u8)) messageType = TypeSuccess;
+                else if (reader.ValueTextEquals("event"u8)) messageType = TypeEvent;
+                else if (reader.ValueTextEquals("error"u8)) messageType = TypeError;
+            }
+            else if (reader.ValueTextEquals("method"u8))
             {
-                reader.Skip();
-                paramsEndIndex = reader.BytesConsumed;
+                reader.Read();
+                method = reader.GetString();
+            }
+            else if (reader.ValueTextEquals("result"u8))
+            {
+                reader.Read();
+                resultReader = reader; // snapshot
+            }
+            else if (reader.ValueTextEquals("params"u8))
+            {
+                reader.Read();
+                paramsStartIndex = (int)reader.TokenStartIndex;
+                isParams = true;
+            }
+            else if (reader.ValueTextEquals("error"u8))
+            {
+                reader.Read();
+                error = reader.GetString();
+            }
+            else if (reader.ValueTextEquals("message"u8))
+            {
+                reader.Read();
+                message = reader.GetString();
             }
             else
             {
-                reader.Skip();
+                reader.Read();
             }
+
+            reader.Skip();
+            if (isParams) paramsEndIndex = (int)reader.BytesConsumed;
             reader.Read();
         }

-        switch (type)
+        switch (messageType)
         {
-            case "success":
+            case TypeSuccess:
                 if (id is null) throw new BiDiException("The remote end responded with 'success' message type, but missed required 'id' property.");

                 if (_pendingCommands.TryGetValue(id.Value, out var command))
@@ -213,13 +221,13 @@ private void ProcessReceivedMessage(byte[] data)

                 break;

-            case "event":
+            case TypeEvent:
                 if (method is null) throw new BiDiException($"The remote end responded with 'event' message type, but missed required 'method' property. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
-                var paramsJsonData = new ReadOnlyMemory<byte>(data, (int)paramsStartIndex, (int)(paramsEndIndex - paramsStartIndex));
+                var paramsJsonData = new ReadOnlyMemory<byte>(data, paramsStartIndex, paramsEndIndex - paramsStartIndex);
                 _eventDispatcher.EnqueueEvent(method, paramsJsonData, _bidi);
                 break;

-            case "error":
+            case TypeError:
                 if (id is null) throw new BiDiException($"The remote end responded with 'error' message type, but missed required 'id' property. Message content: {System.Text.Encoding.UTF8.GetString(data)}");

                 if (_pendingCommands.TryGetValue(id.Value, out var errorCommand))
@@ -235,6 +243,14 @@ private void ProcessReceivedMessage(byte[] data)
                     }
                 }

+                break;
+
+            default:
+                if (_logger.IsEnabled(LogEventLevel.Warn))
+                {
+                    _logger.Warn($"The remote end responded with unknown message type. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
+                }
+
                 break;
         }
     }
PATCH

echo "Patch applied successfully"
