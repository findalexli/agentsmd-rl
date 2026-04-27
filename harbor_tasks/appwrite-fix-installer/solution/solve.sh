#!/usr/bin/env bash
set -euo pipefail

cd /workspace/appwrite

# Idempotency: if patch already applied (distinctive new heading and the
# new onComplete callable parameter), bail.
if grep -q 'Self-hosted Backend-as-a-Service platform' AGENTS.md 2>/dev/null \
   && grep -q 'callable \$onComplete = null' src/Appwrite/Platform/Tasks/Install.php 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index bb24d9f4fe3..4d11ff0ee30 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -1,107 +1,120 @@
-# AGENTS.md
+# Appwrite
 
-Appwrite is an end-to-end backend server for web, mobile, native, and backend apps. This guide provides context and instructions for AI coding agents working on the Appwrite codebase.
+Self-hosted Backend-as-a-Service platform. Hybrid monolithic-microservice architecture built with PHP 8.3+ on Swoole, delivered as Docker containers.
 
-## Project Overview
+## Commands
 
-Appwrite is a self-hosted Backend-as-a-Service (BaaS) platform that provides developers with a set of APIs and tools to build secure, scalable applications. The project uses a hybrid monolithic-microservice architecture built with PHP, running on Swoole for high performance.
+| Command | Purpose |
+|---------|---------|
+| `docker compose up -d --force-recreate --build` | Build and start all services |
+| `docker compose exec appwrite test tests/e2e/Services/[Service]` | Run E2E tests for a service |
+| `docker compose exec appwrite test tests/e2e/Services/[Service] --filter=[Method]` | Run a single test method |
+| `docker compose exec appwrite test tests/unit/` | Run unit tests |
+| `composer format` | Auto-format code (Pint, PSR-12) |
+| `composer format <file>` | Format a specific file |
+| `composer lint <file>` | Check formatting of a file |
+| `composer analyze` | Static analysis (PHPStan level 3) |
+| `composer check` | Same as `analyze` |
 
-**Key Technologies:**
-- **Backend:** PHP 8.3+, Swoole
-- **Libraries:** Utopia PHP
-- **Database:** MariaDB, Redis
-- **Cache:** Redis
-- **Queue:** Redis
-- **Containers:** Docker
+## Stack
 
-## Development Commands
+- PHP 8.3+, Swoole 6.x (async runtime, replaces PHP-FPM)
+- Utopia PHP framework (HTTP routing, CLI, DI, queue)
+- MongoDB (default), MariaDB, MySQL, PostgreSQL (adapters via utopia-php/database)
+- Redis (cache, queue, pub/sub)
+- Docker + Traefik (reverse proxy)
+- PHPUnit 12, Pint (PSR-12), PHPStan level 3
 
-```bash
-# Run Appwrite
-docker compose up -d --force-recreate --build
+## Project layout
 
-# Run specific test
-docker compose exec appwrite test /usr/src/code/tests/e2e/Services/[ServiceName] --filter=[FunctionName]
+- **src/Appwrite/Platform/Modules/** -- feature modules (Account, Avatars, Compute, Console, Databases, Functions, Health, Project, Projects, Proxy, Sites, Storage, Teams, Tokens, VCS, Webhooks)
+- **src/Appwrite/Platform/Workers/** -- background job workers
+- **src/Appwrite/Platform/Tasks/** -- CLI tasks
+- **app/init.php** -- bootstrap (registers services, resources, listeners)
+- **app/init/** -- configs, constants, locales, models, registers, resources, span, database filters/formats
+- **bin/** -- CLI entry points: `worker-*` (14 workers), `schedule-*`, `queue-*`, plus `doctor`, `install`, `migrate`, `realtime`, `upgrade`, `ssl`, `vars`, `maintenance`, `interval`, `specs`, `sdks`, etc.
+- **tests/e2e/** -- end-to-end tests per service
+- **tests/unit/** -- unit tests
+- **public/** -- static assets and generated SDKs
 
-# Format code
-composer format
-```
-
-## Code Style Guidelines
-
-- Follow [PSR-12](https://www.php-fig.org/psr/psr-12/) coding standard
-- Use PSR-4 autoloading
-- Strict type declarations where applicable
-- Comprehensive PHPDoc comments
+## Module structure
 
-### Naming Conventions
+Each module under `src/Appwrite/Platform/Modules/{Name}/` contains:
 
-#### `resourceType` Naming Rule
-
-When a collection has a combination of `resourceType`, `resourceId`, and/or `resourceInternalId`, the value of `resourceType` MUST always be **plural** - for example: `functions`, `sites`, `deployments`.
-
-Examples:
-```php
-'resourceType' => 'functions'
-'resourceType' => 'sites'
-'resourceType' => 'deployments'
+```
+Module.php           -- registers all services for the module
+Services/Http.php    -- registers HTTP endpoints
+Services/Workers.php -- registers background workers
+Services/Tasks.php   -- registers CLI tasks
+Http/{Service}/      -- endpoint actions (Create.php, Get.php, Update.php, Delete.php, XList.php)
+Workers/             -- worker implementations
+Tasks/               -- CLI task implementations
 ```
 
-## Performance Patterns
+HTTP endpoint nesting reflects the URL path. Sub-resources get subdirectories. For example, within the Functions module:
+`Http/Deployments/Template/Create.php` -> `POST /v1/functions/:functionId/deployments/template`
 
-### Document Update Optimization
+File names in Http directories must only be `Get.php`, `Create.php`, `Update.php`, `Delete.php`, or `XList.php`. For non-CRUD operations, model the endpoint as a property update. For example, updating a team membership status lives at `Teams/Http/Memberships/Status/Update.php` (`PATCH /v1/teams/:teamId/memberships/:membershipId/status`).
 
-When updating documents, always pass only the changed attributes as a sparse `Document` rather than the full document. This is more efficient because `updateDocument()` internally performs `array_merge($old, $new)`.
+Register new modules in `src/Appwrite/Platform/Appwrite.php`. Detailed module guide: `src/Appwrite/Platform/AGENTS.md`.
 
-**Correct Pattern:**
-```php
-// Good: Pass only changed attributes directly
-$user = $dbForProject->updateDocument('users', $user->getId(), new Document([
-    'name' => $name,
-    'email' => $email,
-]));
-```
+## Action pattern (HTTP endpoints)
 
-**Incorrect Pattern:**
 ```php
-$user->setAttribute('name', $name);
-$user->setAttribute('email', $email);
-
-// Bad: Passing full document is inefficient
-$user = $dbForProject->updateDocument('users', $user->getId(), $user);
+class Create extends Action
+{
+    public static function getName(): string { return 'createTeam'; }
+
+    public function __construct()
+    {
+        $this
+            ->setHttpMethod(Action::HTTP_REQUEST_METHOD_POST)
+            ->setHttpPath('/v1/teams')
+            ->desc('Create team')
+            ->groups(['api', 'teams'])
+            ->label('event', 'teams.[teamId].create')
+            ->label('scope', 'teams.write')
+            ->param('teamId', '', new CustomId(), 'Team ID.')
+            ->param('name', null, new Text(128), 'Team name.')
+            ->inject('response')
+            ->inject('dbForProject')
+            ->inject('queueForEvents')
+            ->callback($this->action(...));
+    }
+
+    public function action(
+        string $teamId,
+        string $name,
+        Response $response,
+        Database $dbForProject,
+        Event $queueForEvents,
+    ): void {
+        // implementation
+    }
+}
 ```
 
-**Exceptions:**
-- Migration files (need full document updates by design)
-- Cases already using `array_merge()` with `getArrayCopy()`
-- Updates where almost all attributes of the document change at once (sparse update provides little benefit compared to passing the full document)
-- Complex nested relationship logic where full document state is required
-
-## Security Considerations
-
-### Critical Security Practices
-
-- **Never hardcode credentials** - Use environment variables
-- **Rate limiting** - Respect abuse prevention mechanisms
-
-## Dependencies
-
-Avoid introducing new dependencies other than utopia-php.
-
-## Adding new endpoints
-
-When adding new endpoints, make sure to use modules and follow its patterns. Find instruction in [Modules AGENTS.md](src/Appwrite/Platform/AGENTS.md) file.
-
-## Pull Request Guidelines
-### Before Submitting
-
--  Run `composer format`
-- Update documentation if adding features
-- Add/update tests for your changes
-- Check that Docker build succeeds
-`docs/specs/authentication.drawio.svg`
-
-## Known Issues and Gotchas
-
-- **Hot Reload:** Code changes require container restart in some cases
-- **Logging:** There is no central place for logs, so when debugging, ensure to check all possibly relevant containers
+Common injections: `$response`, `$request`, `$dbForProject`, `$dbForPlatform`, `$user`, `$project`, `$queueForEvents`, `$queueForMails`, `$queueForDeletes`.
+
+## Conventions
+
+- PSR-12 formatting enforced by Pint. PSR-4 autoloading.
+- `resourceType` values are always **plural**: `'functions'`, `'sites'`, `'deployments'`.
+- When updating documents, pass only changed attributes as a sparse Document:
+  ```php
+  // correct
+  $dbForProject->updateDocument('users', $user->getId(), new Document([
+      'name' => $name,
+  ]));
+  // incorrect -- passing full document is inefficient
+  $user->setAttribute('name', $name);
+  $dbForProject->updateDocument('users', $user->getId(), $user);
+  ```
+  Exceptions: migrations, `array_merge()` with `getArrayCopy()`, updates where nearly all attributes change, complex nested relationship logic requiring full document state.
+- Avoid introducing dependencies outside the `utopia-php` ecosystem.
+- Never hardcode credentials -- use environment variables.
+- Code changes may require container restart. No central log location -- check relevant containers.
+
+## Cross-repo context
+
+Appwrite is the base server for `appwrite/cloud`. Changes to the Action pattern, module structure, DI system, or response models affect cloud. The `feat-dedicated-db` feature spans cloud, edge, and console.
diff --git a/app/views/install/installer/css/styles.css b/app/views/install/installer/css/styles.css
index 7f253eed463..eedce90834c 100644
--- a/app/views/install/installer/css/styles.css
+++ b/app/views/install/installer/css/styles.css
@@ -478,6 +478,10 @@ body {
     overflow: hidden;
 }
 
+.installer-page[data-upgrade='true'] .installer-step {
+    min-height: 0;
+}
+
 .action-shell {
     display: flex;
     flex-direction: column;
diff --git a/app/views/install/installer/templates/steps/step-4.phtml b/app/views/install/installer/templates/steps/step-4.phtml
index 07dc8652578..8468de30f45 100644
--- a/app/views/install/installer/templates/steps/step-4.phtml
+++ b/app/views/install/installer/templates/steps/step-4.phtml
@@ -62,12 +62,14 @@ $badgeClass = $defaultSecretKey !== '' ? 'badge-success' : 'badge-warning';
                         <span class="badge badge-neutral typography-text-xs-400" data-review-assistant-badge>Disabled</span>
                         <div class="review-label typography-text-xs-400 text-neutral-tertiary">Appwrite Assistant</div>
                     </div>
+                    <?php if (!$isUpgrade) { ?>
                     <div class="review-row">
                         <span class="badge <?php echo $badgeClass; ?> typography-text-xs-400" data-review-badge>
                             <?php echo htmlspecialchars((string) $badgeLabel, ENT_QUOTES, 'UTF-8'); ?>
                         </span>
                         <div class="review-label typography-text-xs-400 text-neutral-tertiary">Secret API key</div>
                     </div>
+                    <?php } ?>
                 </div>
             </div>
         </div>
diff --git a/app/views/install/installer/templates/steps/step-5.phtml b/app/views/install/installer/templates/steps/step-5.phtml
index cd5de5f4abb..c18c3ea748c 100644
--- a/app/views/install/installer/templates/steps/step-5.phtml
+++ b/app/views/install/installer/templates/steps/step-5.phtml
@@ -6,7 +6,7 @@ $isUpgrade = $isUpgrade ?? false;
         <div class="install-panel">
             <div class="install-header">
                 <div class="typography-text-m-400 text-neutral-primary">
-                    <?php echo $isUpgrade ? 'Updating your app…' : 'Installing your app…'; ?>
+                    <?php echo $isUpgrade ? 'Updating Appwrite…' : 'Installing Appwrite…'; ?>
                 </div>
             </div>
             <div class="install-list" data-install-list></div>
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

echo "Patch applied successfully"
