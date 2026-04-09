#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the fix for adding beforeCreateGitDeployment hook
patch -p1 <<'PATCH'
diff --git a/src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php b/src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php
index 04e2dbd4067..ae730c3f747 100644
--- a/src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php
+++ b/src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php
@@ -70,6 +70,8 @@ protected function createGitDeployments(
                     throw new Exception(Exception::PROJECT_NOT_FOUND, 'Repository references non-existent project');
                 }

+                $this->beforeCreateGitDeployment($project, $repository, $dbForPlatform, $authorization);
+
                 try {
                     $dsn = new DSN($project->getAttribute('database'));
                     $databaseName = $dsn->getHost();
@@ -561,6 +563,10 @@ protected function createGitDeployments(
         }
     }

+    protected function beforeCreateGitDeployment(Document $project, Document $repository, Database $dbForPlatform, Authorization $authorization): void
+    {
+    }
+
     protected function getBuildQueueName(Document $project, Database $dbForPlatform, Authorization $authorization): string
     {
         return System::getEnv('_APP_BUILDS_QUEUE_NAME', Event::BUILDS_QUEUE_NAME);
PATCH

# Verify the patch was applied
grep -q "beforeCreateGitDeployment" src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php
echo "Patch applied successfully"
