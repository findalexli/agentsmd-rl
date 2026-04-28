#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "When actors launch async operations via `PipeTo`, those operations can outlive t" "skills/akka-best-practices/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/akka-best-practices/SKILL.md b/skills/akka-best-practices/SKILL.md
@@ -933,3 +933,191 @@ public class MyService
 | Integration tests (multi-node) | Clustered |
 | Local development | LocalTest or Clustered (your choice) |
 | Production | Clustered |
+
+---
+
+## 9. Actor Logging
+
+### Use ILoggingAdapter, Not ILogger<T>
+
+In actors, use `ILoggingAdapter` from `Context.GetLogger()` instead of DI-injected `ILogger<T>`:
+
+```csharp
+public class MyActor : ReceiveActor
+{
+    private readonly ILoggingAdapter _log = Context.GetLogger();
+
+    public MyActor()
+    {
+        Receive<MyMessage>(msg =>
+        {
+            // ✅ Akka.NET ILoggingAdapter with semantic logging (v1.5.57+)
+            _log.Info("Processing message for user {UserId}", msg.UserId);
+            _log.Error(ex, "Failed to process {MessageType}", msg.GetType().Name);
+        });
+    }
+}
+```
+
+**Why ILoggingAdapter:**
+- Integrates with Akka's logging pipeline and supervision
+- Supports semantic/structured logging as of v1.5.57
+- Method names: `Info()`, `Debug()`, `Warning()`, `Error()` (not `Log*` variants)
+- No DI required - obtained directly from actor context
+
+**Don't inject ILogger<T>:**
+
+```csharp
+// ❌ Don't inject ILogger<T> into actors
+public class MyActor : ReceiveActor
+{
+    private readonly ILogger<MyActor> _logger; // Wrong!
+
+    public MyActor(ILogger<MyActor> logger)
+    {
+        _logger = logger;
+    }
+}
+```
+
+### Semantic Logging (v1.5.57+)
+
+As of Akka.NET v1.5.57, `ILoggingAdapter` supports semantic/structured logging with named placeholders:
+
+```csharp
+// Named placeholders for better log aggregation and querying
+_log.Info("Order {OrderId} processed for customer {CustomerId}", order.Id, order.CustomerId);
+
+// Prefer named placeholders over positional
+// ✅ Good: {OrderId}, {CustomerId}
+// ❌ Avoid: {0}, {1}
+```
+
+---
+
+## 10. Managing Async Operations with CancellationToken
+
+When actors launch async operations via `PipeTo`, those operations can outlive the actor if not properly managed. Use `CancellationToken` tied to the actor lifecycle.
+
+### Actor-Scoped CancellationTokenSource
+
+Cancel in-flight async work when the actor stops:
+
+```csharp
+public class DataSyncActor : ReceiveActor
+{
+    private CancellationTokenSource? _operationCts;
+
+    public DataSyncActor()
+    {
+        ReceiveAsync<StartSync>(HandleStartSyncAsync);
+    }
+
+    protected override void PostStop()
+    {
+        // Cancel any in-flight async work when actor stops
+        _operationCts?.Cancel();
+        _operationCts?.Dispose();
+        _operationCts = null;
+        base.PostStop();
+    }
+
+    private Task HandleStartSyncAsync(StartSync cmd)
+    {
+        // Cancel any previous operation, create new CTS
+        _operationCts?.Cancel();
+        _operationCts?.Dispose();
+        _operationCts = new CancellationTokenSource();
+        var ct = _operationCts.Token;
+
+        async Task<SyncResult> PerformSyncAsync()
+        {
+            try
+            {
+                ct.ThrowIfCancellationRequested();
+
+                // Pass token to all async operations
+                var data = await _repository.GetDataAsync(ct);
+                await _service.ProcessAsync(data, ct);
+
+                return new SyncResult(Success: true);
+            }
+            catch (OperationCanceledException) when (ct.IsCancellationRequested)
+            {
+                // Actor is stopping - graceful exit
+                return new SyncResult(Success: false, "Cancelled");
+            }
+        }
+
+        PerformSyncAsync().PipeTo(Self);
+        return Task.CompletedTask;
+    }
+}
+```
+
+### Linked CTS for Per-Operation Timeouts
+
+For external API calls that might hang, use linked CTS with short timeouts:
+
+```csharp
+private static readonly TimeSpan ApiTimeout = TimeSpan.FromSeconds(30);
+
+async Task<SyncResult> PerformSyncAsync()
+{
+    // Check actor-level cancellation
+    ct.ThrowIfCancellationRequested();
+
+    // Per-operation timeout linked to actor's CTS
+    SomeResult result;
+    using (var opCts = CancellationTokenSource.CreateLinkedTokenSource(ct))
+    {
+        opCts.CancelAfter(ApiTimeout);
+        result = await _externalApi.FetchDataAsync(opCts.Token);
+    }
+
+    // Process result...
+}
+```
+
+**How linked CTS works:**
+- Inherits cancellation from parent (actor stop → cancels immediately)
+- Adds its own timeout via `CancelAfter` (hung API → cancels after timeout)
+- Whichever fires first wins
+- Disposed after each operation (short-lived)
+
+### Graceful Timeout vs Shutdown Handling
+
+Distinguish between actor shutdown and operation timeout:
+
+```csharp
+try
+{
+    using var opCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
+    opCts.CancelAfter(ApiTimeout);
+    await _api.CallAsync(opCts.Token);
+}
+catch (OperationCanceledException) when (!ct.IsCancellationRequested)
+{
+    // Timeout (not actor death) - can retry or handle gracefully
+    _log.Warning("API call timed out, skipping item");
+}
+// If ct.IsCancellationRequested is true, let it propagate up
+```
+
+### Key Points
+
+| Practice | Description |
+|----------|-------------|
+| **Actor CTS in PostStop** | Always cancel and dispose in `PostStop()` |
+| **New CTS per operation** | Cancel previous before starting new work |
+| **Pass token everywhere** | EF Core queries, HTTP calls, etc. all accept `CancellationToken` |
+| **Linked CTS for timeouts** | External calls get short timeouts to prevent hanging |
+| **Check in loops** | Call `ct.ThrowIfCancellationRequested()` between iterations |
+| **Graceful handling** | Distinguish timeout vs shutdown in catch blocks |
+
+### When to Use
+
+- Any actor that launches async work via `PipeTo`
+- Long-running operations (sync jobs, batch processing)
+- External API calls that might hang
+- Database operations in loops
PATCH

echo "Gold patch applied."
