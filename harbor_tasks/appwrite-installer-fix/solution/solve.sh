#!/bin/bash
set -e

cd /workspace/appwrite

# Check if already patched (idempotency check)
if grep -q "Runtime::enableCoroutine(SWOOLE_HOOK_ALL)" src/Appwrite/Platform/Installer/Server.php 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/src/Appwrite/Platform/Installer/Http/Installer/Install.php b/src/Appwrite/Platform/Installer/Http/Installer/Install.php
index e29222a7033..fa978892d3b 100644
--- a/src/Appwrite/Platform/Installer/Http/Installer/Install.php
+++ b/src/Appwrite/Platform/Installer/Http/Installer/Install.php
@@ -321,6 +321,28 @@ public function action(
                 }
             };

+            $responseSent = false;
+            $onComplete = function () use ($wantsStream, $swooleResponse, $response, $installId, $state, &$responseSent) {
+                if ($responseSent) {
+                    return;
+                }
+                $responseSent = true;
+                $state->updateGlobalLock($installId, Server::STATUS_COMPLETED);
+                if ($wantsStream) {
+                    $this->writeSseEvent($swooleResponse, 'done', ['installId' => $installId, 'success' => true]);
+                    usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
+                    $swooleResponse->write(": keepalive\n\n");
+                    usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
+                    $swooleResponse->end();
+                } else {
+                    $response->json([
+                        'success' => true,
+                        'installId' => $installId,
+                        'message' => 'Installation completed successfully',
+                    ]);
+                }
+            };
+
             $installer->performInstallation(
                 $httpPort ?: $config->getDefaultHttpPort(),
                 $httpsPort ?: $config->getDefaultHttpsPort(),
@@ -331,23 +353,11 @@ public function action(
                 $progress,
                 $retryStep,
                 $config->isUpgrade(),
-                $account
+                $account,
+                $onComplete,
             );

-            if ($wantsStream) {
-                $this->writeSseEvent($swooleResponse, 'done', ['installId' => $installId, 'success' => true]);
-                usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
-                $swooleResponse->write(": keepalive\n\n");
-                usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
-                $swooleResponse->end();
-            } else {
-                $response->json([
-                    'success' => true,
-                    'installId' => $installId,
-                    'message' => 'Installation completed successfully',
-                ]);
-            }
-            $state->updateGlobalLock($installId, Server::STATUS_COMPLETED);
+            $onComplete();
         } catch (\Throwable $e) {
             $this->handleInstallationError($e, $installId, $wantsStream, $response, $swooleResponse, $state);
         }
diff --git a/src/Appwrite/Platform/Installer/Server.php b/src/Appwrite/Platform/Installer/Server.php
index 17edfaac721..8996b9a4c34 100644
--- a/src/Appwrite/Platform/Installer/Server.php
+++ b/src/Appwrite/Platform/Installer/Server.php
@@ -6,6 +6,7 @@
 use Appwrite\Platform\Installer\Runtime\Config;
 use Appwrite\Platform\Installer\Runtime\State;
 use Swoole\Http\Server as SwooleServer;
+use Swoole\Runtime;
 use Utopia\Http\Adapter\Swoole\Request;
 use Utopia\Http\Adapter\Swoole\Response;
 use Utopia\Http\Adapter\Swoole\Server as SwooleAdapter;
@@ -129,6 +130,8 @@ private function printInstallerUrl(string $host, string $port): void

     private function startSwooleServer(string $host, int $port, ?string $readyFile = null): void
     {
+        Runtime::enableCoroutine(SWOOLE_HOOK_ALL);
+
         $this->state->clearStaleLock();

         // Preload static files into memory
diff --git a/src/Appwrite/Platform/Tasks/Install.php b/src/Appwrite/Platform/Tasks/Install.php
index eab6babc669..a1cc1d094ed 100644
--- a/src/Appwrite/Platform/Tasks/Install.php
+++ b/src/Appwrite/Platform/Tasks/Install.php
@@ -7,6 +7,7 @@
 use Appwrite\Platform\Installer\Runtime\State;
 use Appwrite\Platform\Installer\Server as InstallerServer;
 use Appwrite\Utopia\View;
+use Swoole\Coroutine;
 use Utopia\Auth\Proofs\Password;
 use Utopia\Auth\Proofs\Token;
 use Utopia\Config\Config;
@@ -211,13 +212,14 @@ public function action(
         }

         // If interactive and web mode enabled, start web server
-        if ($interactive === 'Y' && Console::isInteractive()) {
+        // Skip the web installer when explicit CLI params are provided
+        if ($interactive === 'Y' && Console::isInteractive() && !$this->hasExplicitCliParams()) {
             Console::success('Starting web installer...');
             Console::info('Open your browser at: http://localhost:' . InstallerServer::INSTALLER_WEB_PORT);
             Console::info('Press Ctrl+C to cancel installation');

             $detectedDb = ($existingInstallation && isset($existingDatabase)) ? $existingDatabase : null;
-            $this->startWebServer($defaultHttpPort, $defaultHttpsPort, $organization, $image, $noStart, $vars, $isUpgrade, $detectedDb);
+            $this->startWebServer($defaultHttpPort, $defaultHttpsPort, $organization, $image, $noStart, $vars, $isUpgrade || $existingInstallation, $detectedDb);
             return;
         }

@@ -510,7 +512,8 @@ public function performInstallation(
         ?callable $progress = null,
         ?string $resumeFromStep = null,
         bool $isUpgrade = false,
-        array $account = []
+        array $account = [],
+        ?callable $onComplete = null,
     ): void {
         $isLocalInstall = $this->isLocalInstall();
         $this->applyLocalPaths($isLocalInstall, false);
@@ -633,8 +636,24 @@ public function performInstallation(
                     $this->createInitialAdminAccount($account, $progress, $apiUrl, $domain);
                 }

-                // Track installs
-                $this->trackSelfHostedInstall($input, $isUpgrade, $version, $account);
+                // Signal completion before tracking so the SSE stream
+                // finishes and the frontend can redirect immediately.
+                if ($onComplete) {
+                    try {
+                        $onComplete();
+                    } catch (\Throwable) {
+                    }
+                }
+
+                // Run tracking in a coroutine when inside a Swoole
+                // request so it doesn't block the worker.
+                if (Coroutine::getCid() !== -1) {
+                    go(function () use ($input, $isUpgrade, $version, $account) {
+                        $this->trackSelfHostedInstall($input, $isUpgrade, $version, $account);
+                    });
+                } else {
+                    $this->trackSelfHostedInstall($input, $isUpgrade, $version, $account);
+                }

                 if ($isCLI) {
                     Console::success('Appwrite installed successfully');
@@ -753,7 +772,7 @@ private function trackSelfHostedInstall(array $input, bool $isUpgrade, string $v
         $name = $account['name'] ?? 'Admin';
         $email = $account['email'] ?? 'admin@selfhosted.local';

-        $hostIp = gethostbyname($domain);
+        $hostIp = @gethostbyname($domain);

         $payload = [
             'action' => $type,
@@ -767,7 +786,7 @@ private function trackSelfHostedInstall(array $input, bool $isUpgrade, string $v
                 'email' => $email,
                 'domain' => $domain,
                 'database' => $database,
-                'hostIp' => $hostIp !== $domain ? $hostIp : null,
+                'ip' => ($hostIp !== false && $hostIp !== $domain) ? $hostIp : null,
                 'os' => php_uname('s') . ' ' . php_uname('r'),
                 'arch' => php_uname('m'),
                 'cpus' => ((int) trim((string) \shell_exec('nproc'))) ?: null,
@@ -778,6 +797,8 @@ private function trackSelfHostedInstall(array $input, bool $isUpgrade, string $v
         try {
             $client = new Client();
             $client
+                ->setConnectTimeout(5000)
+                ->setTimeout(5000)
                 ->addHeader('Content-Type', 'application/json')
                 ->fetch(self::GROWTH_API_URL . '/analytics', Client::METHOD_POST, $payload);
         } catch (\Throwable) {
@@ -1261,6 +1282,22 @@ protected function applyLocalPaths(bool $isLocalInstall, bool $force = false): v
         $this->hostPath = $this->getInstallerHostPath();
     }

+    /**
+     * Check if any installer-specific CLI params were explicitly passed.
+     * When params like --database or --http-port are provided, the user
+     * intends to run in CLI mode rather than launching the web installer.
+     */
+    private function hasExplicitCliParams(): bool
+    {
+        $argv = $_SERVER['argv'] ?? [];
+        foreach ($argv as $arg) {
+            if (\str_starts_with($arg, '--') && !\str_starts_with($arg, '--interactive')) {
+                return true;
+            }
+        }
+        return false;
+    }
+
     /**
      * Detect the database adapter from a pre-1.9.0 compose file by
      * checking which DB service exists or reading _APP_DB_HOST.
PATCH

# Apply CSS patch for upgrade min-height
if ! grep -q "installer-page\[data-upgrade='true'\]" app/views/install/installer/css/styles.css 2>/dev/null; then
    cat >> app/views/install/installer/css/styles.css << 'CSSPATCH'

.installer-page[data-upgrade='true'] .installer-step {
    min-height: 0;
}
CSSPATCH
fi

# Apply template patch for step-4 (hide secret key on upgrade) - using Python for reliable multi-line edit
python3 << 'PYEOF'
import re

with open('app/views/install/installer/templates/steps/step-4.phtml', 'r') as f:
    content = f.read()

# Check if already patched
if 'if (!$isUpgrade)' not in content:
    # Find and wrap the secret key row with the upgrade check
    pattern = r'(<div class="review-row">\s*<span class="badge <\?php echo \$badgeClass; \?> typography-text-xs-400" data-review-badge>.*?Secret API key</div>\s*</div>)'
    replacement = r'<?php if (!$isUpgrade) { ?>\n                    \1\n                    <?php } ?>'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open('app/views/install/installer/templates/steps/step-4.phtml', 'w') as f:
        f.write(content)
    print("Step-4 template patched")
else:
    print("Step-4 template already patched")
PYEOF

# Apply template patch for step-5 (change text from 'your app' to 'Appwrite')
sed -i "s/Updating your app/Updating Appwrite/g" app/views/install/installer/templates/steps/step-5.phtml
sed -i "s/Installing your app/Installing Appwrite/g" app/views/install/installer/templates/steps/step-5.phtml

echo "Patch applied successfully"
