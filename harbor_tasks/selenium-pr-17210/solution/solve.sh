#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for PR #17210 - Thread safe events registration
patch -p1 <<'PATCH'
diff --git a/dotnet/src/webdriver/BiDi/EventDispatcher.cs b/dotnet/src/webdriver/BiDi/EventDispatcher.cs
index 1b1bfe964dc4a..b8a136b8c84d 100644
--- a/dotnet/src/webdriver/BiDi/EventDispatcher.cs
+++ b/dotnet/src/webdriver/BiDi/EventDispatcher.cs
@@ -55,7 +55,7 @@ public async Task<Subscription> SubscribeAsync<TEventArgs>(string eventName, Even

         var subscribeResult = await _sessionProvider().SubscribeAsync([eventName], new() { Contexts = options?.Contexts, UserContexts = options?.UserContexts }, cancellationToken).ConfigureAwait(false);

-        registration.Handlers.Add(eventHandler);
+        registration.AddHandler(eventHandler);

         return new Subscription(subscribeResult.Subscription, this, eventHandler);
     }
@@ -65,7 +65,7 @@ public async ValueTask UnsubscribeAsync(Subscription subscription, CancellationT
         if (_events.TryGetValue(subscription.EventHandler.EventName, out var registration))
         {
             await _sessionProvider().UnsubscribeAsync([subscription.SubscriptionId], null, cancellationToken).ConfigureAwait(false);
-            registration.Handlers.Remove(subscription.EventHandler);
+            registration.RemoveHandler(subscription.EventHandler);
         }
     }

@@ -99,7 +99,7 @@ private async Task ProcessEventsAwaiterAsync()
                         var eventArgs = (EventArgs)JsonSerializer.Deserialize(result.JsonUtf8Bytes.Span, result.TypeInfo)!;
                         eventArgs.BiDi = result.BiDi;

-                        foreach (var handler in registration.Handlers.ToArray()) // copy handlers avoiding modified collection while iterating
+                        foreach (var handler in registration.GetHandlers()) // copy-on-write array, safe to iterate
                         {
                             await handler.InvokeAsync(eventArgs).ConfigureAwait(false);
                         }
@@ -129,7 +129,21 @@ public async ValueTask DisposeAsync()

     private sealed class EventRegistration(JsonTypeInfo typeInfo)
     {
+        private readonly object _lock = new();
+        private volatile EventHandler[] _handlers = [];
+
         public JsonTypeInfo TypeInfo { get; } = typeInfo;
-        public List<EventHandler> Handlers { get; } = [];
+
+        public EventHandler[] GetHandlers() => _handlers;
+
+        public void AddHandler(EventHandler handler)
+        {
+            lock (_lock) _handlers = [.. _handlers, handler];
+        }
+
+        public void RemoveHandler(EventHandler handler)
+        {
+            lock (_lock) _handlers = Array.FindAll(_handlers, h => h != handler);
+        }
     }
 }

diff --git a/dotnet/test/common/BiDi/Session/SessionTests.cs b/dotnet/test/common/BiDi/Session/SessionTests.cs
index 3ed387a8f686d..c9d5d5fa3cb7b 100644
--- a/dotnet/test/common/BiDi/Session/SessionTests.cs
+++ b/dotnet/test/common/BiDi/Session/SessionTests.cs
@@ -36,7 +36,7 @@ public async Task CanGetStatus()
     }

     [Test]
-    public async Task ShouldRespectTimeout()
+    public void ShouldRespectTimeout()
     {
         Assert.That(
             () => bidi.StatusAsync(new() { Timeout = TimeSpan.FromMicroseconds(1) }),
@@ -44,7 +44,7 @@ public async Task ShouldRespectTimeout()
     }

     [Test]
-    public async Task ShouldRespectCancellationToken()
+    public void ShouldRespectCancellationToken()
     {
         using var cts = new CancellationTokenSource(TimeSpan.FromMicroseconds(1));
PATCH

# Verify the distinctive line is present
grep -q "copy-on-write array, safe to iterate" dotnet/src/webdriver/BiDi/EventDispatcher.cs
echo "Patch applied successfully"
