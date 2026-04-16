#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check - skip if patch already applied
if grep -q "ProcessEventsAwaiterAsync" dotnet/src/webdriver/BiDi/EventDispatcher.cs 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/dotnet/src/webdriver/BiDi/EventDispatcher.cs b/dotnet/src/webdriver/BiDi/EventDispatcher.cs
index 5a37ee58d9f7b..1a4e93006821c 100644
--- a/dotnet/src/webdriver/BiDi/EventDispatcher.cs
+++ b/dotnet/src/webdriver/BiDi/EventDispatcher.cs
@@ -34,18 +34,20 @@ internal sealed class EventDispatcher : IAsyncDisposable

     private readonly ConcurrentDictionary<string, EventRegistration> _events = new();

-    private readonly Channel<EventItem> _pendingEvents = Channel.CreateUnbounded<EventItem>(new()
+    private readonly Channel<PendingEvent> _pendingEvents = Channel.CreateUnbounded<PendingEvent>(new()
     {
         SingleReader = true,
         SingleWriter = true
     });

-    private readonly Task _processEventsTask;
+    private readonly Task _eventEmitterTask;
+
+    private static readonly TaskFactory _myTaskFactory = new(CancellationToken.None, TaskCreationOptions.DenyChildAttach, TaskContinuationOptions.None, TaskScheduler.Default);

     public EventDispatcher(Func<ISessionModule> sessionProvider)
     {
         _sessionProvider = sessionProvider;
-        _processEventsTask = Task.Run(ProcessEventsAsync);
+        _eventEmitterTask = _myTaskFactory.StartNew(ProcessEventsAwaiterAsync).Unwrap();
     }

     public async Task<Subscription> SubscribeAsync<TEventArgs>(string eventName, EventHandler eventHandler, SubscriptionOptions? options, JsonTypeInfo<TEventArgs> jsonTypeInfo, CancellationToken cancellationToken)
@@ -53,19 +55,11 @@ public async Task<Subscription> SubscribeAsync<TEventArgs>(string eventName, Eve
     {
         var registration = _events.GetOrAdd(eventName, _ => new EventRegistration(jsonTypeInfo));

-        registration.AddHandler(eventHandler);
+        var subscribeResult = await _sessionProvider().SubscribeAsync([eventName], new() { Contexts = options?.Contexts, UserContexts = options?.UserContexts }, cancellationToken).ConfigureAwait(false);

-        try
-        {
-            var subscribeResult = await _sessionProvider().SubscribeAsync([eventName], new() { Contexts = options?.Contexts, UserContexts = options?.UserContexts }, cancellationToken).ConfigureAwait(false);
+        registration.Handlers.Add(eventHandler);

-            return new Subscription(subscribeResult.Subscription, this, eventHandler);
-        }
-        catch
-        {
-            registration.RemoveHandler(eventHandler);
-            throw;
-        }
+        return new Subscription(subscribeResult.Subscription, this, eventHandler);
     }

     public async ValueTask UnsubscribeAsync(Subscription subscription, CancellationToken cancellationToken)
@@ -73,34 +67,15 @@ public async ValueTask UnsubscribeAsync(Subscription subscription, CancellationT
         if (_events.TryGetValue(subscription.EventHandler.EventName, out var registration))
         {
             await _sessionProvider().UnsubscribeAsync([subscription.SubscriptionId], null, cancellationToken).ConfigureAwait(false);
-
-            // Wait until all pending events for this method are dispatched
-            try
-            {
-                await registration.DrainAsync(cancellationToken).ConfigureAwait(false);
-            }
-            finally
-            {
-                registration.RemoveHandler(subscription.EventHandler);
-            }
+            registration.Handlers.Remove(subscription.EventHandler);
         }
     }

     public void EnqueueEvent(string method, ReadOnlyMemory<byte> jsonUtf8Bytes, IBiDi bidi)
     {
-        if (_events.TryGetValue(method, out var registration))
+        if (_events.TryGetValue(method, out var registration) && registration.TypeInfo is not null)
         {
-            if (_pendingEvents.Writer.TryWrite(new EventItem(jsonUtf8Bytes, bidi, registration)))
-            {
-                registration.IncrementEnqueued();
-            }
-            else
-            {
-                if (_logger.IsEnabled(LogEventLevel.Warn))
-                {
-                    _logger.Warn($"Failed to enqueue BiDi event with method '{method}' for processing. Event will be ignored.");
-                }
-            }
+            _pendingEvents.Writer.TryWrite(new PendingEvent(method, jsonUtf8Bytes, bidi, registration.TypeInfo));
         }
         else
         {
@@ -111,45 +86,34 @@ public void EnqueueEvent(string method, ReadOnlyMemory<byte> jsonUtf8Bytes, IBiD
         }
     }

-    private async Task ProcessEventsAsync()
+    private async Task ProcessEventsAwaiterAsync()
     {
         var reader = _pendingEvents.Reader;
-
         while (await reader.WaitToReadAsync().ConfigureAwait(false))
         {
-            while (reader.TryRead(out var evt))
+            while (reader.TryRead(out var result))
             {
                 try
                 {
-                    var eventArgs = (EventArgs)JsonSerializer.Deserialize(evt.JsonUtf8Bytes.Span, evt.Registration.TypeInfo)!;
-                    eventArgs.BiDi = evt.BiDi;
-
-                    foreach (var handler in evt.Registration.GetHandlersSnapshot())
+                    if (_events.TryGetValue(result.Method, out var registration))
                     {
-                        try
+                        // Deserialize on background thread instead of network thread (single parse)
+                        var eventArgs = (EventArgs)JsonSerializer.Deserialize(result.JsonUtf8Bytes.Span, result.TypeInfo)!;
+                        eventArgs.BiDi = result.BiDi;
+
+                        foreach (var handler in registration.Handlers.ToArray()) // copy handlers avoiding modified collection while iterating
                         {
                             await handler.InvokeAsync(eventArgs).ConfigureAwait(false);
                         }
-                        catch (Exception ex)
-                        {
-                            if (_logger.IsEnabled(LogEventLevel.Error))
-                            {
-                                _logger.Error($"Unhandled error processing BiDi event handler: {ex}");
-                            }
-                        }
                     }
                 }
                 catch (Exception ex)
                 {
                     if (_logger.IsEnabled(LogEventLevel.Error))
                     {
-                        _logger.Error($"Unhandled error deserializing BiDi event: {ex}");
+                        _logger.Error($"Unhandled error processing BiDi event handler: {ex}");
                     }
                 }
-                finally
-                {
-                    evt.Registration.IncrementProcessed();
-                }
             }
         }
     }
@@ -158,88 +122,16 @@ public async ValueTask DisposeAsync()
     {
         _pendingEvents.Writer.Complete();

-        await _processEventsTask.ConfigureAwait(false);
+        await _eventEmitterTask.ConfigureAwait(false);

         GC.SuppressFinalize(this);
     }

-    private sealed record EventItem(ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, EventRegistration Registration);
+    private readonly record struct PendingEvent(string Method, ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, JsonTypeInfo TypeInfo);

     private sealed class EventRegistration(JsonTypeInfo typeInfo)
     {
-        private long _enqueueSeq;
-        private long _processedSeq;
-        private readonly object _drainLock = new();
-        private readonly List<EventHandler> _handlers = [];
-        private List<(long TargetSeq, TaskCompletionSource<bool> Tcs)>? _drainWaiters;
-
         public JsonTypeInfo TypeInfo { get; } = typeInfo;
-
-        public void AddHandler(EventHandler handler)
-        {
-            lock (_drainLock) _handlers.Add(handler);
-        }
-
-        public void RemoveHandler(EventHandler handler)
-        {
-            lock (_drainLock) _handlers.Remove(handler);
-        }
-
-        public EventHandler[] GetHandlersSnapshot()
-        {
-            lock (_drainLock) return [.. _handlers];
-        }
-
-        public void IncrementEnqueued() => Interlocked.Increment(ref _enqueueSeq);
-
-        public void IncrementProcessed()
-        {
-            var processed = Interlocked.Increment(ref _processedSeq);
-
-            lock (_drainLock)
-            {
-                if (_drainWaiters is null) return;
-
-                for (var i = _drainWaiters.Count - 1; i >= 0; i--)
-                {
-                    if (_drainWaiters[i].TargetSeq <= processed)
-                    {
-                        _drainWaiters[i].Tcs.TrySetResult(true);
-                        _drainWaiters.RemoveAt(i);
-                    }
-                }
-
-                if (_drainWaiters.Count == 0) _drainWaiters = null;
-            }
-        }
-
-        public Task DrainAsync(CancellationToken cancellationToken)
-        {
-            lock (_drainLock)
-            {
-                var target = Volatile.Read(ref _enqueueSeq);
-                if (Volatile.Read(ref _processedSeq) >= target) return Task.CompletedTask;
-
-                var tcs = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
-                _drainWaiters ??= [];
-                _drainWaiters.Add((target, tcs));
-
-                // Double-check: processing may have caught up between the read and adding the waiter
-                if (Volatile.Read(ref _processedSeq) >= target)
-                {
-                    _drainWaiters.Remove((target, tcs));
-                    if (_drainWaiters.Count == 0) _drainWaiters = null;
-                    return Task.CompletedTask;
-                }
-
-                if (!cancellationToken.CanBeCanceled) return tcs.Task;
-
-                return tcs.Task.ContinueWith(
-                    static _ => { },
-                    cancellationToken,
-                    TaskContinuationOptions.None,
-                    TaskScheduler.Default);
-            }
-        }
+        public List<EventHandler> Handlers { get; } = [];
     }
 }
PATCH

echo "Patch applied successfully"
