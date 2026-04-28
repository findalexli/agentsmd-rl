#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dotnet-skills

# Idempotency guard
if grep -qF "public void Send(Message msg, Priority priority = Priority.Normal);  // Breaks b" "skills/csharp-api-design/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/csharp-api-design/SKILL.md b/skills/csharp-api-design/SKILL.md
@@ -57,11 +57,23 @@ The foundation of stable APIs: **never remove or modify, only extend**.
 ### Safe Changes (Any Release)
 
 ```csharp
-// ADD new overloads with default parameters
-public void Process(Order order, CancellationToken ct = default);
+// SAFE: Add NEW overload methods that delegate to existing methods
+// Existing method - do not modify its signature
+public void Process(Order order) { ... }
+// New overload - safe to add
+public void Process(Order order, CancellationToken ct)
+{
+    // implementation that handles cancellation
+}
 
-// ADD new optional parameters to existing methods
-public void Send(Message msg, Priority priority = Priority.Normal);
+// SAFE: Add NEW overloads for additional functionality
+// Existing method - do not modify
+public void Send(Message msg) { ... }
+// New overload - safe to add
+public void Send(Message msg, Priority priority)
+{
+    // implementation that handles priority
+}
 
 // ADD new types, interfaces, enums
 public interface IOrderValidator { }
@@ -89,6 +101,14 @@ public Order? GetOrder(string id);  // Was: public Order GetOrder()
 // CHANGE access modifiers
 internal class OrderProcessor { }  // Was: public
 
+// ADD optional parameters to EXISTING methods (binary incompatible!)
+// The compiled IL method signature changes - callers compiled against
+// the old signature will get MissingMethodException at runtime.
+// Optional parameter defaults are baked into the CALLER's assembly at compile time.
+public void Process(Order order, CancellationToken ct = default);  // Breaks binary compat!
+public void Send(Message msg, Priority priority = Priority.Normal);  // Breaks binary compat!
+// Correct approach: add a NEW overload method instead (see Safe Changes above)
+
 // ADD required parameters without defaults
 public void Process(Order order, ILogger logger);  // Breaks callers!
 ```
PATCH

echo "Gold patch applied."
