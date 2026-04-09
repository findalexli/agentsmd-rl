#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the gold patch to fix the race condition in VectorDB collection creation
cat <<'PATCH' | git apply -
diff --git a/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php b/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php
index b85a8b30b47..a7e2d68eacf 100644
--- a/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php
+++ b/src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php
@@ -130,9 +130,11 @@ public function action(string $databaseId, string $collectionId, string $name, i
             $indexes[] = new Document($index);
         }
         try {
-            // passing null in creates only creates the metadata collection
             if (!$dbForDatabases->exists(null, Database::METADATA)) {
-                $dbForDatabases->create();
+                try {
+                    $dbForDatabases->create();
+                } catch (DuplicateException) {
+                }
             }
             $dbForDatabases->createCollection(
                 id: 'database_' . $database->getSequence() . '_collection_' . $collection->getSequence(),
PATCH

echo "Applied fix for VectorDB metadata initialization race condition"
