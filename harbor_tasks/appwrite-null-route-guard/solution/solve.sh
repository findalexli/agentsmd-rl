#!/bin/bash
set -e

cd /workspace/appwrite

# Idempotency check: if already patched, skip
if grep -q "if (\$route === null)" app/controllers/shared/api.php; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch - first just the api.php part
cat <<'PATCH' | git apply -
diff --git a/app/controllers/shared/api.php b/app/controllers/shared/api.php
index 5166429e324..8254a22ac0d 100644
--- a/app/controllers/shared/api.php
+++ b/app/controllers/shared/api.php
@@ -98,6 +98,9 @@
     ->inject('authorization')
     ->action(function (Http $utopia, Request $request, Database $dbForPlatform, Database $dbForProject, Audit $queueForAudits, Document $project, User $user, ?Document $session, array $servers, string $mode, Document $team, ?Key $apiKey, Authorization $authorization) {
         $route = $utopia->getRoute();
+        if ($route === null) {
+            throw new AppwriteException(AppwriteException::GENERAL_ROUTE_NOT_FOUND);
+        }

         /**
          * Handle user authentication and session validation.
@@ -489,6 +492,10 @@
         $request->setUser($user);

         $route = $utopia->getRoute();
+        if ($route === null) {
+            throw new AppwriteException(AppwriteException::GENERAL_ROUTE_NOT_FOUND);
+        }
+
         $path = $route->getMatchedPath();
         $databaseType = match (true) {
             str_contains($path, '/documentsdb') => DATABASE_TYPE_DOCUMENTSDB,
PATCH

# Apply the test patch separately (with fuzz factor for whitespace)
cat <<'TESTPATCH' | git apply --ignore-whitespace -
diff --git a/tests/e2e/General/HTTPTest.php b/tests/e2e/General/HTTPTest.php
index 450e4f23786..38137b1320a 100644
--- a/tests/e2e/General/HTTPTest.php
+++ b/tests/e2e/General/HTTPTest.php
@@ -122,6 +122,14 @@ public function testDefaultOAuth2()
         $this->assertEquals(200, $response['headers']['status-code']);
     }

+    public function testConsoleRootWithoutRouteDoesNotFatal()
+    {
+        $response = $this->client->call(Client::METHOD_GET, '/console/', $this->getHeaders());
+
+        $this->assertEquals(404, $response['headers']['status-code']);
+        $this->assertEquals('general_route_not_found', $response['body']['type']);
+    }
+
     public function testCors()
     {

TESTPATCH

echo "Patch applied successfully."
