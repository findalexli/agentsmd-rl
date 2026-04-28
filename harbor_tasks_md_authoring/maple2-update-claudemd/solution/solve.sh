#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maple2

# Idempotency guard
if grep -qF "private readonly ILogger logger = Log.Logger.ForContext<MyClass>();" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -224,6 +224,33 @@ Dynamic scripting for map events:
 
 ## Key Patterns and Conventions
 
+### Logging
+
+Use Serilog for logging throughout the codebase:
+
+```csharp
+using Serilog;
+
+public class MyClass {
+    private readonly ILogger logger = Log.Logger.ForContext<MyClass>();
+
+    public void MyMethod() {
+        logger.Debug("Debug message with {Parameter}", value);
+        logger.Information("Info message");
+        logger.Warning("Warning message");
+        logger.Error(exception, "Error message");
+    }
+}
+```
+
+For static contexts or one-off logging:
+
+```csharp
+using Serilog;
+
+Log.Logger.ForContext<MyClass>().Debug("Message");
+```
+
 ### Dependency Injection (Autofac)
 
 Heavy use of property injection:
PATCH

echo "Gold patch applied."
