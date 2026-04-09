#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if already patched
if grep -q "Keeper hardware error while loading user defined SQL object" src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the fix patch
cat <<'PATCH' | patch -p1
diff --git a/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp b/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
index 15a829f7cde0..ee91cb39522f 100644
--- a/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
+++ b/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
@@ -9,6 +9,8 @@
 #include <Common/Exception.h>
 #include <Common/ZooKeeper/IKeeper.h>
 #include <Common/ZooKeeper/KeeperException.h>
+#include <Common/ZooKeeper/ZooKeeperCommon.h>
+#include <Common/ZooKeeper/ZooKeeperRetries.h>
 #include <Common/escapeForFileName.h>
 #include <Common/logger_useful.h>
 #include <Common/quoteString.h>
@@ -358,6 +360,17 @@ ASTPtr UserDefinedSQLObjectsZooKeeperStorage::tryLoadObject(

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
@@ -408,15 +421,36 @@ void UserDefinedSQLObjectsZooKeeperStorage::refreshAllObjects(const zkutil::ZooK
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

echo "Patch applied successfully"
