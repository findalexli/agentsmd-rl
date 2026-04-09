#!/bin/bash
set -e

REPO="ClickHouse"
cd /workspace/${REPO}

# Apply the fix for UDF registry loss during Keeper session expiry
patch -p1 << 'PATCH'
diff --git a/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp b/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
index 7ad70d710d6f..c85618efc716 100644
--- a/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
+++ b/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
@@ -10,6 +10,7 @@
 #include <Common/ZooKeeper/IKeeper.h>
 #include <Common/ZooKeeper/KeeperException.h>
 #include <Common/ZooKeeper/ZooKeeperCommon.h>
+#include <Common/ZooKeeper/ZooKeeperRetries.h>
 #include <Common/escapeForFileName.h>
 #include <Common/logger_useful.h>
 #include <Common/quoteString.h>
@@ -364,6 +365,17 @@ ASTPtr UserDefinedSQLObjectsZooKeeperStorage::tryLoadObject(

         return parseObjectData(object_data, object_type);
     }
+    catch (const zkutil::KeeperException & e)
+    {
+        if (Coordination::isHardwareError(e.code))
+        {
+            LOG_WARNING(log, "Keeper hardware error while loading user defined SQL object {}: {}",
+                backQuote(object_name), e.message());
+            throw; /// Re-throw hardware errors so the caller can handle them properly
+        }
+        tryLogCurrentException(log, fmt::format("while loading user defined SQL object {}", backQuote(object_name)));
+        return nullptr; /// Non-hardware Keeper errors — treat as missing
+    }
     catch (...)
     {
         tryLogCurrentException(log, fmt::format("while loading user defined SQL object {}", backQuote(object_name)));
@@ -414,15 +426,36 @@ void UserDefinedSQLObjectsZooKeeperStorage::refreshAllObjects(const zkutil::ZooK
 void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects(const zkutil::ZooKeeperPtr & zookeeper, UserDefinedSQLObjectType object_type)
 {
     LOG_DEBUG(log, "Refreshing all user-defined {} objects", object_type);
+
     Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type);

-    /// Read & parse all SQL objects from ZooKeeper
+    /// Read & parse all SQL objects from ZooKeeper.
+    /// Use ZooKeeperRetriesControl so that transient Keeper hiccups (brief connection
+    /// blips, session jitter) are retried with backoff instead of aborting the entire
+    /// refresh cycle and falling back to the 5-second sleep in processWatchQueue.
+    /// tryLoadObject re-throws Keeper hardware errors, which ZooKeeperRetriesControl
+    /// catches and retries automatically.  If retries are exhausted the exception
+    /// propagates to the caller, so we never reach setAllObjects with a partial set.
+    static constexpr UInt64 max_retries = 5;
+    static constexpr UInt64 initial_backoff_ms = 200;
+    static constexpr UInt64 max_backoff_ms = 5000;
+
     std::vector<std::pair<String, ASTPtr>> function_names_and_asts;
-    for (const auto & function_name : object_names)
+
+    ZooKeeperRetriesControl retries_ctl(
+        "refreshObjects",
+        log,
+        ZooKeeperRetriesInfo{max_retries, initial_backoff_ms, max_backoff_ms, /*query_status=*/nullptr});
+
+    retries_ctl.retryLoop([&]
     {
-        if (auto ast = tryLoadObject(zookeeper, UserDefinedSQLObjectType::Function, function_name))
-            function_names_and_asts.emplace_back(function_name, ast);
-    }
+        function_names_and_asts.clear();
+        for (const auto & function_name : object_names)
+        {
+            if (auto ast = tryLoadObject(zookeeper, UserDefinedSQLObjectType::Function, function_name))
+                function_names_and_asts.emplace_back(function_name, ast);
+        }
+    });

     setAllObjects(function_names_and_asts);
PATCH

# Idempotency check - verify the patch was applied
grep -q "ZooKeeperRetriesControl" src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp

echo "Fix applied successfully"
