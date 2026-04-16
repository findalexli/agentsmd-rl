#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the gold patch for realtime error handling
cat <<'PATCH' | git apply -
diff --git a/src/Appwrite/Event/Realtime.php b/src/Appwrite/Event/Realtime.php
index 419863191e1..747fd786f90 100644
--- a/src/Appwrite/Event/Realtime.php
+++ b/src/Appwrite/Event/Realtime.php
@@ -4,6 +4,7 @@

 use Appwrite\Messaging\Adapter;
 use Appwrite\Messaging\Adapter\Realtime as RealtimeAdapter;
+use Utopia\Console;
 use Utopia\Database\Document;
 use Utopia\Database\Exception;

@@ -96,17 +97,21 @@ class Realtime extends Event
             : [$target['projectId'] ?? $this->getProject()->getId()];

         foreach ($projectIds as $projectId) {
-            $this->realtime->send(
-                projectId: $projectId,
-                payload: $this->getRealtimePayload(),
-                events: $allEvents,
-                channels: $target['channels'],
-                roles: $target['roles'],
-                options: [
-                    'permissionsChanged' => $target['permissionsChanged'],
-                    'userId' => $this->getParam('userId')
-                ]
-            );
+            try {
+                $this->realtime->send(
+                    projectId: $projectId,
+                    payload: $this->getRealtimePayload(),
+                    events: $allEvents,
+                    channels: $target['channels'],
+                    roles: $target['roles'],
+                    options: [
+                        'permissionsChanged' => $target['permissionsChanged'],
+                        'userId' => $this->getParam('userId')
+                    ]
+                );
+            } catch (\Exception $e) {
+                Console::error('Realtime send failed: '.$e->getMessage());
+            }
         }

         return true;
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "Console::error('Realtime send failed:" src/Appwrite/Event/Realtime.php && echo "Patch applied successfully"
