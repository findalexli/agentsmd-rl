#!/usr/bin/env bash
set -euo pipefail

cd /workspace/selenium

# Idempotency: if the patch is already applied, skip.
if grep -q "Use constructor with timeout parameter" java/src/org/openqa/selenium/bidi/BiDi.java; then
  echo "Gold patch already applied; nothing to do."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/java/src/org/openqa/selenium/bidi/BiDi.java b/java/src/org/openqa/selenium/bidi/BiDi.java
index f1e56397f8815..29062233e1aa7 100644
--- a/java/src/org/openqa/selenium/bidi/BiDi.java
+++ b/java/src/org/openqa/selenium/bidi/BiDi.java
@@ -30,6 +30,14 @@ public class BiDi implements Closeable {
   private final Duration timeout;
   private final Connection connection;

+  /**
+   * @deprecated Use constructor with timeout parameter: {@link #BiDi(Connection, Duration)}
+   */
+  @Deprecated(forRemoval = true)
+  public BiDi(Connection connection) {
+    this(connection, Duration.ofSeconds(30));
+  }
+
   public BiDi(Connection connection, Duration timeout) {
     this.connection = Require.nonNull("WebSocket connection", connection);
     this.timeout = Require.nonNull("WebSocket timeout", timeout);
PATCH

echo "Gold patch applied."
