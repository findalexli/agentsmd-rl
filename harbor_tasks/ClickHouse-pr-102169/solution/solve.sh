#!/bin/bash
# Apply the fix for ZooKeeper session renewal in UDF retry loop
# PR: https://github.com/ClickHouse/ClickHouse/pull/102169

set -e

cd /workspace/ClickHouse

# Check if already applied (idempotency)
if grep -q "Renew the session on retry -- the previous one may have expired" src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp 2>/dev/null; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the patch
cat <<'PATCH' | git apply -
diff --git a/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp b/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
index c85618efc716..5cc3339d9885 100644
--- a/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
+++ b/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp
@@ -427,20 +427,19 @@ void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects(const zkutil::ZooKeep
 {
     LOG_DEBUG(log, "Refreshing all user-defined {} objects", object_type);

-    Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type);
-
     /// Read & parse all SQL objects from ZooKeeper.
-    /// Use ZooKeeperRetriesControl so that transient Keeper hiccups (brief connection
-    /// blips, session jitter) are retried with backoff instead of aborting the entire
-    /// refresh cycle and falling back to the 5-second sleep in processWatchQueue.
     /// tryLoadObject re-throws Keeper hardware errors, which ZooKeeperRetriesControl
-    /// catches and retries automatically.  If retries are exhausted the exception
-    /// propagates to the caller, so we never reach setAllObjects with a partial set.
+    /// catches and retries automatically.  On retry we obtain a fresh session via
+    /// zookeeper_getter (the provided handle may point to an expired session) and
+    /// re-fetch the object list, so that watches are set on the live session.
+    /// If retries are exhausted the exception propagates to the caller, so we never
+    /// reach setAllObjects with a partial set.
     static constexpr UInt64 max_retries = 5;
     static constexpr UInt64 initial_backoff_ms = 200;
     static constexpr UInt64 max_backoff_ms = 5000;

     std::vector<std::pair<String, ASTPtr>> function_names_and_asts;
+    zkutil::ZooKeeperPtr current_zookeeper = zookeeper;

     ZooKeeperRetriesControl retries_ctl(
         "refreshObjects",
@@ -449,10 +448,16 @@ void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects(const zkutil::ZooKeep

     retries_ctl.retryLoop([&]
     {
+        /// Renew the session on retry -- the previous one may have expired.
+        if (retries_ctl.isRetry())
+            current_zookeeper = zookeeper_getter.getZooKeeper().first;
+
+        Strings object_names = getObjectNamesAndSetWatch(current_zookeeper, object_type);
+
         function_names_and_asts.clear();
         for (const auto & function_name : object_names)
         {
-            if (auto ast = tryLoadObject(zookeeper, UserDefinedSQLObjectType::Function, function_name))
+            if (auto ast = tryLoadObject(current_zookeeper, UserDefinedSQLObjectType::Function, function_name))
                 function_names_and_asts.emplace_back(function_name, ast);
         }
     });
PATCH

echo "Fix applied successfully"
