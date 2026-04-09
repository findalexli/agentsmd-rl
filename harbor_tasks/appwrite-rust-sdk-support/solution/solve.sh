#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the gold patch for Rust SDK support
cat <<'PATCH' | git apply -
diff --git a/app/config/sdks.php b/app/config/sdks.php
index 1a808aa10a9..13fb444216d 100644
--- a/app/config/sdks.php
+++ b/app/config/sdks.php
@@ -494,6 +494,25 @@
                 'gitBranch' => 'dev',
                 'changelog' => \realpath(__DIR__ . '/../../docs/sdks/swift/CHANGELOG.md'),
             ],
+            [
+                'key' => 'rust',
+                'name' => 'Rust',
+                'version' => '0.1.0',
+                'url' => 'https://github.com/appwrite/sdk-for-rust',
+                'package' => 'https://crates.io/crates/appwrite',
+                'enabled' => true,
+                'beta' => true,
+                'dev' => true,
+                'hidden' => false,
+                'family' => APP_SDK_PLATFORM_SERVER,
+                'prism' => 'rust',
+                'source' => \realpath(__DIR__ . '/../sdks/server-rust'),
+                'gitUrl' => 'git@github.com:appwrite/sdk-for-rust.git',
+                'gitRepoName' => 'sdk-for-rust',
+                'gitUserName' => 'appwrite',
+                'gitBranch' => 'dev',
+                'changelog' => \realpath(__DIR__ . '/../../docs/sdks/rust/CHANGELOG.md'),
+            ],
             [
                 'key' => 'graphql',
                 'name' => 'GraphQL',

diff --git a/src/Appwrite/Platform/Tasks/SDKs.php b/src/Appwrite/Platform/Tasks/SDKs.php
index 70d5e6ded57..a7a5f0278f5 100644
--- a/src/Appwrite/Platform/Tasks/SDKs.php
+++ b/src/Appwrite/Platform/Tasks/SDKs.php
@@ -21,6 +21,7 @@
 use Appwrite\SDK\Language\ReactNative;
 use Appwrite\SDK\Language\REST;
 use Appwrite\SDK\Language\Ruby;
+use Appwrite\SDK\Language\Rust;
 use Appwrite\SDK\Language\Swift;
 use Appwrite\SDK\Language\Web;
 use Appwrite\SDK\SDK;
@@ -301,6 +302,9 @@ public function action(?string $platform, ?string $sdk, ?string $version, ?strin
                         $config = new Kotlin();
                         $warning = $warning . "\n\n > This is the Kotlin SDK for integrating with Appwrite from your Kotlin server-side code. If you're looking for the Android SDK you should check [appwrite/sdk-for-android](https://github.com/appwrite/sdk-for-android)";
                         break;
+                    case 'rust':
+                        $config = new Rust();
+                        break;
                     case 'graphql':
                         $config = new GraphQL();
                         break;
PATCH

# Verify the patch was applied
grep -q "'key' => 'rust'" app/config/sdks.php && echo "Rust SDK config added"
grep -q "use Appwrite\\SDK\\Language\\Rust;" src/Appwrite/Platform/Tasks/SDKs.php && echo "Rust import added"
grep -q "case 'rust':" src/Appwrite/Platform/Tasks/SDKs.php && echo "Rust case added"
