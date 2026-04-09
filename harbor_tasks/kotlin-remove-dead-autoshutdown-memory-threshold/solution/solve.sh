#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency check)
if ! grep -q "COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE" compiler/daemon/daemon-common/src/org/jetbrains/kotlin/daemon/common/DaemonParams.kt; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/compiler/daemon/daemon-common/src/org/jetbrains/kotlin/daemon/common/DaemonParams.kt b/compiler/daemon/daemon-common/src/org/jetbrains/kotlin/daemon/common/DaemonParams.kt
index bacf149cf197b..36f9e1ad36d37 100644
--- a/compiler/daemon/daemon-common/src/org/jetbrains/kotlin/daemon/common/DaemonParams.kt
+++ b/compiler/daemon/daemon-common/src/org/jetbrains/kotlin/daemon/common/DaemonParams.kt
@@ -36,7 +36,6 @@ const val COMPILE_DAEMON_TIMEOUT_INFINITE_S: Int = 0
 const val COMPILE_DAEMON_DEFAULT_IDLE_TIMEOUT_S: Int = 7200 // 2 hours
 const val COMPILE_DAEMON_DEFAULT_UNUSED_TIMEOUT_S: Int = 60
 const val COMPILE_DAEMON_DEFAULT_SHUTDOWN_DELAY_MS: Long = 1000L // 1 sec
-const val COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE: Long = 0L
 const val COMPILE_DAEMON_FORCE_SHUTDOWN_DEFAULT_TIMEOUT_MS: Long = 10000L // 10 secs
 const val COMPILE_DAEMON_TIMEOUT_INFINITE_MS: Long = 0L
 const val COMPILE_DAEMON_IS_READY_MESSAGE = "Kotlin compile daemon is ready"
@@ -243,7 +242,6 @@ data class DaemonLogOptions(

 data class DaemonOptions(
     var runFilesPath: String = COMPILE_DAEMON_DEFAULT_RUN_DIR_PATH,
-    var autoshutdownMemoryThreshold: Long = COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE,
     var autoshutdownIdleSeconds: Int = COMPILE_DAEMON_DEFAULT_IDLE_TIMEOUT_S,
     var autoshutdownUnusedSeconds: Int = COMPILE_DAEMON_DEFAULT_UNUSED_TIMEOUT_S,
     var shutdownDelayMilliseconds: Long = COMPILE_DAEMON_DEFAULT_SHUTDOWN_DELAY_MS,
@@ -255,13 +253,6 @@ data class DaemonOptions(
     override val mappers: List<PropMapper<*, *, *>>
         get() = listOf(
             PropMapper(this, DaemonOptions::runFilesPath, fromString = String::trimQuotes),
-            PropMapper(
-                this,
-                DaemonOptions::autoshutdownMemoryThreshold,
-                fromString = String::toLong,
-                skipIf = { it == 0L },
-                mergeDelimiter = "="
-            ),
             // TODO: implement "use default" value without specifying default, so if client and server uses different defaults, it should not lead to many params in the cmd line; use 0 for it and used different val for infinite
             PropMapper(
                 this,
PATCH

echo "Patch applied successfully"
