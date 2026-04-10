#!/bin/bash
set -e

cd /workspace/appwrite

# Check if already patched (idempotency) - look for unique() in the param() default value specifically
if grep -q "param('variableId', 'unique()'" src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php; then
    echo "Already patched"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php b/src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php
index 8dbc7200453..8b6dc67b4f3 100644
--- a/src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php
+++ b/src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php
@@ -53,7 +53,7 @@ public function __construct()
                     )
                 ],
             ))
-            ->param('variableId', '', fn (Database $dbForProject) => new CustomId(false, $dbForProject->getAdapter()->getMaxUIDLength()), 'Variable ID. Choose a custom ID or generate a random ID with `ID.unique()`. Valid chars are a-z, A-Z, 0-9, period, hyphen, and underscore. Can\'t start with a special char. Max length is 36 chars.', false, ['dbForProject'])
+            ->param('variableId', 'unique()', fn (Database $dbForProject) => new CustomId(false, $dbForProject->getAdapter()->getMaxUIDLength()), 'Variable ID. Choose a custom ID or generate a random ID with `ID.unique()`. Valid chars are a-z, A-Z, 0-9, period, hyphen, and underscore. Can\'t start with a special char. Max length is 36 chars.', true, ['dbForProject'])
             ->param('key', null, new Text(Database::LENGTH_KEY), 'Variable key. Max length: ' . Database::LENGTH_KEY  . ' chars.')
             ->param('value', null, new Text(8192, 0), 'Variable value. Max length: 8192 chars.')
             ->param('secret', true, new Boolean(), 'Secret variables can be updated or deleted, but only projects can read them during build and runtime.', true)
PATCH

echo "Patch applied successfully"
