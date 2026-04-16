#!/bin/bash
# Gold solution for selenium-bidi-deserialization-refactor
set -e

cd /workspace/selenium

# Idempotency check - look for the new TryGetJsonTypeInfo method
if grep -q "TryGetJsonTypeInfo" dotnet/src/webdriver/BiDi/EventDispatcher.cs 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --verbose <<'PATCH'
diff --git a/dotnet/src/webdriver/BiDi/Broker.cs b/dotnet/src/webdriver/BiDi/Broker.cs
index abc123..def456 100644
--- a/dotnet/src/webdriver/BiDi/Broker.cs
+++ b/dotnet/src/webdriver/BiDi/Broker.cs
@@ -125,8 +125,7 @@ internal sealed class Broker : IAsyncDisposable
         string? error = default;
         string? message = default;
         Utf8JsonReader resultReader = default;
-        int paramsStartIndex = 0;
-        int paramsEndIndex = 0;
+        Utf8JsonReader paramsReader = default;

         Utf8JsonReader reader = new(data);
         reader.Read(); // "{"
@@ -135,8 +134,6 @@ internal sealed class Broker : IAsyncDisposable

         while (reader.TokenType == JsonTokenType.PropertyName)
         {
-            bool isParams = false;
-
             if (reader.ValueTextEquals("id"u8))
             {
                 reader.Read();
@@ -162,8 +159,7 @@ internal sealed class Broker : IAsyncDisposable
             else if (reader.ValueTextEquals("params"u8))
             {
                 reader.Read();
-                paramsStartIndex = (int)reader.TokenStartIndex;
-                isParams = true;
+                paramsReader = reader; // snapshot
             }
             else if (reader.ValueTextEquals("error"u8))
             {
@@ -181,7 +177,6 @@ internal sealed class Broker : IAsyncDisposable
             }

             reader.Skip();
-            if (isParams) paramsEndIndex = (int)reader.BytesConsumed;
             reader.Read();
         }

@@ -220,8 +215,23 @@ internal sealed class Broker : IAsyncDisposable

             case TypeEvent:
                 if (method is null) throw new BiDiException($"The remote end responded with 'event' message type, but missed required 'method' property. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
-                var paramsJsonData = new ReadOnlyMemory<byte>(data, paramsStartIndex, paramsEndIndex - paramsStartIndex);
-                _eventDispatcher.EnqueueEvent(method, paramsJsonData, _bidi);
+
+                if (!_eventDispatcher.TryGetJsonTypeInfo(method, out var jsonTypeInfo))
+                {
+                    if (_logger.IsEnabled(LogEventLevel.Warn))
+                    {
+                        _logger.Warn($"Received BiDi event with method '{method}', but no event type mapping was found. Event will be ignored. Message content: {System.Text.Encoding.UTF8.GetString(data)}");
+                    }
+
+                    break;
+                }
+
+                var eventArgs = JsonSerializer.Deserialize(ref paramsReader, jsonTypeInfo) as EventArgs
+                    ?? throw new BiDiException("Remote end returned null event args in the 'params' property.");
+
+                eventArgs.BiDi = _bidi;
+
+                _eventDispatcher.EnqueueEvent(method, eventArgs);
                 break;

             case TypeError:
diff --git a/dotnet/src/webdriver/BiDi/EventDispatcher.cs b/dotnet/src/webdriver/BiDi/EventDispatcher.cs
index abc123..def456 100644
--- a/dotnet/src/webdriver/BiDi/EventDispatcher.cs
+++ b/dotnet/src/webdriver/BiDi/EventDispatcher.cs
@@ -18,7 +18,7 @@
 // </copyright>

 using System.Collections.Concurrent;
-using System.Text.Json;
+using System.Diagnostics.CodeAnalysis;
 using System.Text.Json.Serialization.Metadata;
 using System.Threading.Channels;
 using OpenQA.Selenium.BiDi.Session;
@@ -32,7 +32,7 @@ internal sealed class EventDispatcher : IAsyncDisposable

     private readonly Func<ISessionModule> _sessionProvider;

-    private readonly ConcurrentDictionary<string, EventRegistration> _events = new();
+    private readonly ConcurrentDictionary<string, EventRegistration> _eventRegistrations = new();

     private readonly Channel<PendingEvent> _pendingEvents = Channel.CreateUnbounded<PendingEvent>(new()
     {
@@ -50,7 +50,7 @@ internal sealed class EventDispatcher : IAsyncDisposable
     public async Task<Subscription> SubscribeAsync<TEventArgs>(string eventName, EventHandler eventHandler, SubscriptionOptions? options, JsonTypeInfo<TEventArgs> jsonTypeInfo, CancellationToken cancellationToken)
         where TEventArgs : EventArgs
     {
-        var registration = _events.GetOrAdd(eventName, _ => new EventRegistration(jsonTypeInfo));
+        var registration = _eventRegistrations.GetOrAdd(eventName, _ => new EventRegistration(jsonTypeInfo));

         var subscribeResult = await _sessionProvider().SubscribeAsync([eventName], new() { Contexts = options?.Contexts, UserContexts = options?.UserContexts }, cancellationToken).ConfigureAwait(false);

@@ -61,26 +61,16 @@ internal sealed class EventDispatcher : IAsyncDisposable

     public async ValueTask UnsubscribeAsync(Subscription subscription, CancellationToken cancellationToken)
     {
-        if (_events.TryGetValue(subscription.EventHandler.EventName, out var registration))
+        if (_eventRegistrations.TryGetValue(subscription.EventHandler.EventName, out var registration))
         {
             await _sessionProvider().UnsubscribeAsync([subscription.SubscriptionId], null, cancellationToken).ConfigureAwait(false);
             registration.RemoveHandler(subscription.EventHandler);
         }
     }

-    public void EnqueueEvent(string method, ReadOnlyMemory<byte> jsonUtf8Bytes, IBiDi bidi)
+    public void EnqueueEvent(string method, EventArgs eventArgs)
     {
-        if (_events.TryGetValue(method, out var registration) && registration.TypeInfo is not null)
-        {
-            _pendingEvents.Writer.TryWrite(new PendingEvent(method, jsonUtf8Bytes, bidi, registration.TypeInfo));
-        }
-        else
-        {
-            if (_logger.IsEnabled(LogEventLevel.Warn))
-            {
-                _logger.Warn($"Received BiDi event with method '{method}', but no event type mapping was found. Event will be ignored.");
-            }
-        }
+        _pendingEvents.Writer.TryWrite(new PendingEvent(method, eventArgs));
     }

     private async Task ProcessEventsAwaiterAsync()
@@ -92,15 +82,11 @@ internal sealed class EventDispatcher : IAsyncDisposable
             {
                 try
                 {
-                    if (_events.TryGetValue(result.Method, out var registration))
+                    if (_eventRegistrations.TryGetValue(result.Method, out var registration))
                     {
-                        // Deserialize on background thread instead of network thread (single parse)
-                        var eventArgs = (EventArgs)JsonSerializer.Deserialize(result.JsonUtf8Bytes.Span, result.TypeInfo)!;
-                        eventArgs.BiDi = result.BiDi;
-
                         foreach (var handler in registration.GetHandlers()) // copy-on-write array, safe to iterate
                         {
-                            await handler.InvokeAsync(eventArgs).ConfigureAwait(false);
+                            await handler.InvokeAsync(result.EventArgs).ConfigureAwait(false);
                         }
                     }
                 }
@@ -122,7 +108,19 @@ internal sealed class EventDispatcher : IAsyncDisposable
         GC.SuppressFinalize(this);
     }

-    private readonly record struct PendingEvent(string Method, ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, JsonTypeInfo TypeInfo);
+    public bool TryGetJsonTypeInfo(string eventName, [NotNullWhen(true)] out JsonTypeInfo? jsonTypeInfo)
+    {
+        if (_eventRegistrations.TryGetValue(eventName, out var registration))
+        {
+            jsonTypeInfo = registration.TypeInfo;
+            return true;
+        }
+
+        jsonTypeInfo = null;
+        return false;
+    }
+
+    private readonly record struct PendingEvent(string Method, EventArgs EventArgs);

     private sealed class EventRegistration(JsonTypeInfo typeInfo)
     {
PATCH

echo "Patch applied successfully."
