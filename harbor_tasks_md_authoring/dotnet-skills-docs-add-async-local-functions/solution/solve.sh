#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "| **Exception handling** | Cleaner try/catch structure without `AggregateExcepti" "skills/csharp-concurrency-patterns/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/csharp-concurrency-patterns/SKILL.md b/skills/csharp-concurrency-patterns/SKILL.md
@@ -608,6 +608,97 @@ var results = new ConcurrentBag<Result>();
 
 ---
 
+## Prefer Async Local Functions
+
+Use async local functions instead of `Task.Run(async () => ...)` or `ContinueWith()`:
+
+### Don't: Anonymous Async Lambda
+
+```csharp
+private void HandleCommand(MyCommand cmd)
+{
+    var self = Self;
+
+    _ = Task.Run(async () =>
+    {
+        // Lots of async work here...
+        var result = await DoWorkAsync();
+        return new WorkCompleted(result);
+    }).PipeTo(self);
+}
+```
+
+### Do: Async Local Function
+
+```csharp
+private void HandleCommand(MyCommand cmd)
+{
+    async Task<WorkCompleted> ExecuteAsync()
+    {
+        // Lots of async work here...
+        var result = await DoWorkAsync();
+        return new WorkCompleted(result);
+    }
+
+    ExecuteAsync().PipeTo(Self);
+}
+```
+
+### Avoid ContinueWith for Sequencing
+
+**Don't:**
+```csharp
+someTask
+    .ContinueWith(t => ProcessResult(t.Result))
+    .ContinueWith(t => SendNotification(t.Result));
+```
+
+**Do:**
+```csharp
+async Task ProcessAndNotifyAsync()
+{
+    var result = await someTask;
+    var processed = await ProcessResult(result);
+    await SendNotification(processed);
+}
+
+ProcessAndNotifyAsync();
+```
+
+### Why This Matters
+
+| Benefit | Description |
+|---------|-------------|
+| **Readability** | Named functions are self-documenting; anonymous lambdas obscure intent |
+| **Debugging** | Stack traces show meaningful function names instead of `<>c__DisplayClass` |
+| **Exception handling** | Cleaner try/catch structure without `AggregateException` unwrapping |
+| **Scope clarity** | Local functions make captured variables explicit |
+| **Testability** | Easier to extract and unit test the async logic |
+
+### Akka.NET Example
+
+When using `PipeTo` in actors, async local functions keep the pattern clean:
+
+```csharp
+private void HandleSync(StartSync cmd)
+{
+    async Task<SyncResult> PerformSyncAsync()
+    {
+        await using var scope = _scopeFactory.CreateAsyncScope();
+        var service = scope.ServiceProvider.GetRequiredService<ISyncService>();
+
+        var count = await service.SyncAsync(cmd.EntityId);
+        return new SyncResult(cmd.EntityId, count);
+    }
+
+    PerformSyncAsync().PipeTo(Self);
+}
+```
+
+This is cleaner than wrapping everything in `Task.Run(async () => ...)`.
+
+---
+
 ## Quick Reference: Which Tool When?
 
 | Need | Tool | Example |
PATCH

echo "Gold patch applied."
