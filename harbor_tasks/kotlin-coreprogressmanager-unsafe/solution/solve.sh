#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the fix for CoreProgressManager to avoid using sun.misc.Unsafe
# This replaces ConcurrentLongObjectMap with ConcurrentHashMap

patch -p1 <<'PATCH'
diff --git a/compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java b/compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java
index f2c94f9f7c7a8..ec01ad7c81a44 100644
--- a/compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java
+++ b/compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java
@@ -23,10 +23,8 @@ import com.intellij.openapi.progress.util.TitledIndicator;
 import com.intellij.openapi.util.*;
 import com.intellij.openapi.wm.ex.ProgressIndicatorEx;
 import com.intellij.util.ExceptionUtil;
-import com.intellij.util.Java11Shim;
 import com.intellij.util.SystemProperties;
 import com.intellij.util.concurrency.AppExecutorUtil;
-import com.intellij.util.containers.ConcurrentLongObjectMap;
 import com.intellij.util.ui.EDT;
 import org.jetbrains.annotations.*;

@@ -44,12 +42,18 @@ import static com.intellij.openapi.progress.impl.ProgressManagerScopeKt.ProgressM
 import static com.intellij.openapi.progress.impl.ProgressManagerScopeKt.ProgressManagerScope;

 /**
- * This class is a simplified version of the original one, which tries to avoid loading a specific class
+ * This class is a simplified version of the original one, which applies two workarounds:
+ *
+ * 1. Try to avoid loading a specific class
  * kotlinx/coroutines/internal/intellij/IntellijCoroutine from kotlinx.coroutines fork in a CLI environment.
  *
  * After IJPL-207644 has been fixed, since 253 we can hopefully remove the workaround, via setting
  * `ide.can.use.coroutines.fork` property to false.
  *
+ * 2. Replace `ConcurrentLongObjectMap` with `ConcurrentHashMap`: the former uses `sun.misc.Unsafe` which is
+ * being phased out in modern JDK versions: https://openjdk.org/jeps/471.
+ * The original version of this class is already fixed in 253 (IJPL-191435).
+ *
  * TODO: Remove it once KT-81457 is fixed
  */
 public class CoreProgressManager extends ProgressManager implements Disposable {
@@ -65,11 +69,11 @@ public class CoreProgressManager extends ProgressManager implements Disposable {
   // THashMap is avoided here because of tombstones overhead
   private static final Map<ProgressIndicator, Set<Thread>> threadsUnderIndicator = new HashMap<>(); // guarded by threadsUnderIndicator
   // the active indicator for the thread id
-  private static final ConcurrentLongObjectMap<ProgressIndicator> currentIndicators =
-    Java11Shim.Companion.getINSTANCE().createConcurrentLongObjectMap();
+  private static final ConcurrentMap<Long, ProgressIndicator> currentIndicators =
+    new ConcurrentHashMap<>();
   // top-level indicators for the thread id
-  private static final ConcurrentLongObjectMap<ProgressIndicator> threadTopLevelIndicators =
-    Java11Shim.Companion.getINSTANCE().createConcurrentLongObjectMap();
+  private static final ConcurrentMap<Long, ProgressIndicator> threadTopLevelIndicators =
+    new ConcurrentHashMap<>();
   // threads which are running under canceled indicator
   private static final Set<Thread> threadsUnderCanceledIndicator = new HashSet<>(); // guarded by threadsUnderIndicator
PATCH

echo "Fix applied successfully"
