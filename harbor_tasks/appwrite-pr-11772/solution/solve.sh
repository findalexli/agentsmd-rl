#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the fix for VectorsDB metadata bootstrap race condition
patch -p1 <<'PATCH'
diff --git a/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php b/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php
index a7e2d68eacf..58433c7deb8 100644
--- a/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php
+++ b/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php
@@ -130,10 +130,25 @@ public function action(string $databaseId, string $collectionId, string $name, i
             $indexes[] = new Document($index);
         }
         try {
-            if (!$dbForDatabases->exists(null, Database::METADATA)) {
+            // Bootstrap the database metadata without a separate existence
+            // check to avoid races when multiple first collections are created
+            // concurrently for the same VectorsDB database.
+            for ($attempt = 0; $attempt < 5; $attempt++) {
                 try {
                     $dbForDatabases->create();
+                    break;
                 } catch (DuplicateException) {
+                    break;
+                } catch (\Throwable $e) {
+                    if ($dbForDatabases->exists(null, Database::METADATA)) {
+                        break;
+                    }
+
+                    if ($attempt === 4) {
+                        throw $e;
+                    }
+
+                    \usleep(100_000);
                 }
             }
             $dbForDatabases->createCollection(
PATCH

# Verify the patch was applied
grep -q "Bootstrap the database metadata without a separate existence" src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php && echo "Patch applied successfully"
