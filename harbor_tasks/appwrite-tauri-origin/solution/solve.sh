#!/bin/bash
set -e

cd /workspace/appwrite

# Check if already patched (idempotency)
if grep -q "SCHEME_TAURI = 'tauri'" src/Appwrite/Network/Platform.php; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/src/Appwrite/Network/Platform.php b/src/Appwrite/Network/Platform.php
index ea64ff98c1c..1cf5de91d14 100644
--- a/src/Appwrite/Network/Platform.php
+++ b/src/Appwrite/Network/Platform.php
@@ -35,6 +35,7 @@ class Platform
     public const SCHEME_ANDROID = 'appwrite-android';
     public const SCHEME_WINDOWS = 'appwrite-windows';
     public const SCHEME_LINUX = 'appwrite-linux';
+    public const SCHEME_TAURI = 'tauri';

     /**
      * @var array<string, string> Map scheme types to user-friendly platform names.
@@ -53,6 +54,7 @@ class Platform
         self::SCHEME_FIREFOX_EXTENSION => 'Web (Firefox Extension)',
         self::SCHEME_SAFARI_EXTENSION => 'Web (Safari Extension)',
         self::SCHEME_EDGE_EXTENSION => 'Web (Edge Extension)',
+        self::SCHEME_TAURI => 'Web (Tauri)',
     ];

     /**
diff --git a/src/Appwrite/Network/Validator/Origin.php b/src/Appwrite/Network/Validator/Origin.php
index 8b9974e990e..3c4e8a254aa 100644
--- a/src/Appwrite/Network/Validator/Origin.php
+++ b/src/Appwrite/Network/Validator/Origin.php
@@ -69,6 +69,7 @@ public function isValid($origin): bool
             Platform::SCHEME_FIREFOX_EXTENSION,
             Platform::SCHEME_SAFARI_EXTENSION,
             Platform::SCHEME_EDGE_EXTENSION,
+            Platform::SCHEME_TAURI,
         ];
         if (in_array($this->scheme, $webPlatforms, true)) {
             $validator = new Hostname($this->allowedHostnames);
diff --git a/tests/unit/Network/Validators/OriginTest.php b/tests/unit/Network/Validators/OriginTest.php
index 7a19daecbfc..64ce71951ba 100644
--- a/tests/unit/Network/Validators/OriginTest.php
+++ b/tests/unit/Network/Validators/OriginTest.php
@@ -73,6 +73,10 @@ public function testValues(): void
         $this->assertEquals(false, $validator->isValid('ms-browser-extension://com.company.appname'));
         $this->assertEquals('Invalid Origin. Register your new client (com.company.appname) as a new Web (Edge Extension) platform on your project console dashboard', $validator->getDescription());

+        $this->assertEquals(true, $validator->isValid('tauri://localhost'));
+        $this->assertEquals(false, $validator->isValid('tauri://example.com'));
+        $this->assertEquals('Invalid Origin. Register your new client (example.com) as a new Web (Tauri) platform on your project console dashboard', $validator->getDescription());
+
         $this->assertEquals(false, $validator->isValid('random-scheme://localhost'));
         $this->assertEquals('Invalid Scheme. The scheme used (random-scheme) in the Origin (random-scheme://localhost) is not supported. If you are using a custom scheme, please change it to `appwrite-callback-<PROJECT_ID>`', $validator->getDescription());
     }
PATCH

echo "Patch applied successfully"
