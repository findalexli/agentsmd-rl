#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the fix for adding 'specification' field to functions and sites collections
patch -p1 << 'PATCH'
diff --git a/app/config/collections/projects.php b/app/config/collections/projects.php
index 6c417ae14..55dceb9b4 100644
--- a/app/config/collections/projects.php
+++ b/app/config/collections/projects.php
@@ -788,6 +788,17 @@ return [
                 'default' => null,
                 'filters' => [],
             ],
+            [
+                'array' => false,
+                '$id' => ID::custom('specification'),
+                'type' => Database::VAR_STRING,
+                'format' => '',
+                'size' => 128,
+                'signed' => false,
+                'required' => false,
+                'default' => APP_COMPUTE_SPECIFICATION_DEFAULT,
+                'filters' => [],
+            ],
             [
                 'array' => false,
                 '$id' => ID::custom('buildSpecification'),
@@ -1245,6 +1256,17 @@ return [
                 'array' => false,
                 'filters' => [],
             ],
+            [
+                'array' => false,
+                '$id' => ID::custom('specification'),
+                'type' => Database::VAR_STRING,
+                'format' => '',
+                'size' => 128,
+                'signed' => false,
+                'required' => false,
+                'default' => APP_COMPUTE_SPECIFICATION_DEFAULT,
+                'filters' => [],
+            ],
             [
                 'array' => false,
                 '$id' => ID::custom('buildSpecification'),
PATCH

# Idempotency check - verify the fix was applied
if grep -q "'\$id' => ID::custom('specification')" app/config/collections/projects.php; then
    echo "Fix applied successfully: 'specification' field added to collections"
else
    echo "ERROR: Fix was not applied correctly"
    exit 1
fi
