#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the fix patch
cat <<'PATCH' | git apply -
diff --git a/app/init/resources/request.php b/app/init/resources/request.php
index 2bec4128826..156e1515018 100644
--- a/app/init/resources/request.php
+++ b/app/init/resources/request.php
@@ -1306,11 +1306,12 @@
                 $dsn = new DSN('mysql://' . $project->getAttribute('database'));
             }

-            $pool = $pools->get($databaseDSN->getHost());
+            $databaseHost = $databaseDSN->getHost();
+            $pool = $pools->get($databaseHost);

             $adapter = new DatabasePool($pool);
             $database = new Database($adapter, $cache);
-            $sharedTables = \explode(',', System::getEnv('_APP_DATABASE_SHARED_TABLES', ''));
+            $sharedTables = \array_filter(\explode(',', System::getEnv('_APP_DATABASE_SHARED_TABLES', '')));

             $database
                 ->setDatabase(APP_DATABASE)
@@ -1321,10 +1322,31 @@
                 ->setMaxQueryValues(APP_DATABASE_QUERY_MAX_VALUES);
             // inside pools authorization needs to be set first
             $database->getAdapter()->setSupportForAttributes($databaseType !== DOCUMENTSDB);
-            if (\in_array($dsn->getHost(), $sharedTables)) {
+
+            // For separate pools (documentsdb/vectorsdb), check their own shared tables config.
+            // If not configured, use dedicated mode to avoid cross-engine tenant type mismatches.
+            if ($databaseHost !== $dsn->getHost()) {
+                $dbTypeSharedTables = match ($databaseType) {
+                    DOCUMENTSDB => \array_filter(\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', ''))),
+                    VECTORSDB => \array_filter(\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', ''))),
+                    default => [],
+                };
+
+                if (\in_array($databaseHost, $dbTypeSharedTables)) {
+                    $database
+                        ->setSharedTables(true)
+                        ->setTenant($project->getSequence())
+                        ->setNamespace($databaseDSN->getParam('namespace'));
+                } else {
+                    $database
+                        ->setSharedTables(false)
+                        ->setTenant(null)
+                        ->setNamespace('_' . $project->getSequence());
+                }
+            } elseif (\in_array($dsn->getHost(), $sharedTables)) {
                 $database
                     ->setSharedTables(true)
-                    ->setTenant((int) $project->getSequence())
+                    ->setTenant($project->getSequence())
                     ->setNamespace($dsn->getParam('namespace'));
             } else {
                 $database
diff --git a/app/init/worker/message.php b/app/init/worker/message.php
index a444ada91d7..95477088ce2 100644
--- a/app/init/worker/message.php
+++ b/app/init/worker/message.php
@@ -202,7 +202,8 @@
             }

             $pools = $register->get('pools');
-            $pool = $pools->get($databaseDSN->getHost());
+            $databaseHost = $databaseDSN->getHost();
+            $pool = $pools->get($databaseHost);

             $adapter = new DatabasePool($pool);
             $database = new Database($adapter, $cache);
@@ -211,12 +212,32 @@
                 ->setAuthorization($authorization);
             $database->getAdapter()->setSupportForAttributes($databaseType !== DOCUMENTSDB);

-            $sharedTables = \explode(',', System::getEnv('_APP_DATABASE_SHARED_TABLES', ''));
+            $sharedTables = \array_filter(\explode(',', System::getEnv('_APP_DATABASE_SHARED_TABLES', '')));
+
+            // For separate pools (documentsdb/vectorsdb), check their own shared tables config.
+            // If not configured, use dedicated mode to avoid cross-engine tenant type mismatches.
+            if ($databaseHost !== $dsn->getHost()) {
+                $dbTypeSharedTables = match ($databaseType) {
+                    DOCUMENTSDB => \array_filter(\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', ''))),
+                    VECTORSDB => \array_filter(\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', ''))),
+                    default => [],
+                };

-            if (\in_array($dsn->getHost(), $sharedTables, true)) {
+                if (\in_array($databaseHost, $dbTypeSharedTables)) {
+                    $database
+                        ->setSharedTables(true)
+                        ->setTenant($projectDocument->getSequence())
+                        ->setNamespace($databaseDSN->getParam('namespace'));
+                } else {
+                    $database
+                        ->setSharedTables(false)
+                        ->setTenant(null)
+                        ->setNamespace('_' . $projectDocument->getSequence());
+                }
+            } elseif (\in_array($dsn->getHost(), $sharedTables, true)) {
                 $database
                     ->setSharedTables(true)
-                    ->setTenant((int) $projectDocument->getSequence())
+                    ->setTenant($projectDocument->getSequence())
                     ->setNamespace($dsn->getParam('namespace'));
             } else {
                 $database
diff --git a/src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php b/src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php
index 3585bc4477c..3d07c65250c 100644
--- a/src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php
+++ b/src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php
@@ -61,16 +61,16 @@ private function constructDatabaseDSNFromProjectDatabase(string $databasetype, $
                 $databaseKeys = System::getEnv('_APP_DATABASE_DOCUMENTSDB_KEYS', '');
                 $databaseOverride = System::getEnv('_APP_DATABASE_DOCUMENTSDB_OVERRIDE');
                 $dbScheme = System::getEnv('_APP_DB_HOST_DOCUMENTSDB', 'mongodb');
-                $databaseSharedTables = \explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', ''));
-                $databaseSharedTablesV1 = \explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1', ''));
+                $databaseSharedTables = \array_filter(\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', '')));
+                $databaseSharedTablesV1 = \array_filter(\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1', '')));
                 break;
             case VECTORSDB:
                 $databases = Config::getParam('pools-vectorsdb', []);
                 $databaseKeys = System::getEnv('_APP_DATABASE_VECTORSDB_KEYS', '');
                 $databaseOverride = System::getEnv('_APP_DATABASE_VECTORSDB_OVERRIDE');
                 $dbScheme = System::getEnv('_APP_DB_HOST_VECTORSDB', 'postgresql');
-                $databaseSharedTables = \explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', ''));
-                $databaseSharedTablesV1 = \explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES_V1', ''));
+                $databaseSharedTables = \array_filter(\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', '')));
+                $databaseSharedTablesV1 = \array_filter(\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES_V1', '')));
                 break;
             default:
                 // legacy/tablesdb
@@ -108,7 +108,7 @@ private function constructDatabaseDSNFromProjectDatabase(string $databasetype, $
         if ($index !== false) {
             $selectedDsn = $databases[$index];
         } else {
-            if (!empty($dsn)) {
+            if (!empty($dsn) && !empty($databaseSharedTables)) {
                 $beforeFilter = \array_values($databases);
                 if ($isSharedTablesV1) {
                     $databases = array_filter($databases, fn ($value) => \in_array($value, $databaseSharedTablesV1));
@@ -118,7 +118,10 @@ private function constructDatabaseDSNFromProjectDatabase(string $databasetype, $
                     $databases = array_filter($databases, fn ($value) => !\in_array($value, $databaseSharedTables));
                 }
             }
-            $selectedDsn = !empty($databases) ? $databases[array_rand($databases)] : '';
+            if (empty($databases)) {
+                throw new Exception(Exception::GENERAL_SERVER_ERROR, "No {$databasetype} database pool available for the current shared-tables mode");
+            }
+            $selectedDsn = $databases[array_rand($databases)];
         }

         if (\in_array($selectedDsn, $databaseSharedTables)) {
PATCH

# Idempotency check: verify distinctive line from patch is present
if ! grep -q "No.*database pool available for the current shared-tables mode" /workspace/appwrite/src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php; then
    echo "Error: Patch was not applied successfully"
    exit 1
fi

echo "Fix applied successfully"
