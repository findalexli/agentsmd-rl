#!/bin/bash
set -e

cd /workspace/appwrite

# 1. Fix styles.css - add upgrade CSS rule
echo '.installer-page[data-upgrade='\''true'\''] .installer-step { min-height: 0; }' >> app/views/install/installer/css/styles.css

# 2. Fix step-4.phtml - hide API key on upgrade
# Find the line with data-review-badge and wrap it with the upgrade check
python3 << 'PYEOF'
with open('app/views/install/installer/templates/steps/step-4.phtml', 'r') as f:
    content = f.read()

# Add <?php if (!$isUpgrade) { ?> before the review-row div containing data-review-badge
old = '''                    <div class="review-row">
                        <span class="badge <?php echo $badgeClass; ?> typography-text-xs-400" data-review-badge>'''
new = '''                    <?php if (!$isUpgrade) { ?>
                    <div class="review-row">
                        <span class="badge <?php echo $badgeClass; ?> typography-text-xs-400" data-review-badge>'''
content = content.replace(old, new)

# Add closing <?php } ?> after the review-row div
old = '''                        <div class="review-label typography-text-xs-400 text-neutral-tertiary">Secret API key</div>
                    </div>'''
new = '''                        <div class="review-label typography-text-xs-400 text-neutral-tertiary">Secret API key</div>
                    </div>
                    <?php } ?>'''
content = content.replace(old, new)

with open('app/views/install/installer/templates/steps/step-4.phtml', 'w') as f:
    f.write(content)
PYEOF

# 3. Fix step-5.phtml - update copy
sed -i "s/Updating your app/Updating Appwrite/g" app/views/install/installer/templates/steps/step-5.phtml

# 4. Fix Server.php - add Swoole Runtime import and enableCoroutine
python3 << 'PYEOF'
with open('src/Appwrite/Platform/Installer/Server.php', 'r') as f:
    content = f.read()

# Add Runtime import after SwooleServer import
content = content.replace(
    'use Swoole\Http\Server as SwooleServer;',
    'use Swoole\Http\Server as SwooleServer;\nuse Swoole\Runtime;'
)

# Add enableCoroutine call in startSwooleServer
content = content.replace(
    '    private function startSwooleServer(string $host, int $port, ?string $readyFile = null): void\n    {\n        $this->state->clearStaleLock();',
    '    private function startSwooleServer(string $host, int $port, ?string $readyFile = null): void\n    {\n        Runtime::enableCoroutine(SWOOLE_HOOK_ALL);\n\n        $this->state->clearStaleLock();'
)

with open('src/Appwrite/Platform/Installer/Server.php', 'w') as f:
    f.write(content)
PYEOF

# 5. Fix Http/Installer/Install.php - add onComplete callback
python3 << 'PYEOF'
with open('src/Appwrite/Platform/Installer/Http/Installer/Install.php', 'r') as f:
    content = f.read()

# Add $responseSent and $onComplete before performInstallation call
old = '''            $installer->performInstallation(
                $httpPort ?: $config->getDefaultHttpPort(),
                $httpsPort ?: $config->getDefaultHttpsPort(),
                $installId,
                $this->state,
                $input,
                $progress,
                $retryStep,
                $config->isUpgrade(),
                $account
            );

            if ($wantsStream) {
                $this->writeSseEvent($swooleResponse, 'done', ['installId' => $installId, 'success' => true]);
                usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
                $swooleResponse->write(": keepalive\n\n");
                usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
                $swooleResponse->end();
            } else {
                $response->json([
                    'success' => true,
                    'installId' => $installId,
                    'message' => 'Installation completed successfully',
                ]);
            }
            $state->updateGlobalLock($installId, Server::STATUS_COMPLETED);'''

new = '''            $responseSent = false;
            $onComplete = function () use ($wantsStream, $swooleResponse, $response, $installId, $state, &$responseSent) {
                if ($responseSent) {
                    return;
                }
                $responseSent = true;
                $state->updateGlobalLock($installId, Server::STATUS_COMPLETED);
                if ($wantsStream) {
                    $this->writeSseEvent($swooleResponse, 'done', ['installId' => $installId, 'success' => true]);
                    usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
                    $swooleResponse->write(": keepalive\\n\\n");
                    usleep(self::SSE_KEEPALIVE_DELAY_MICROSECONDS);
                    $swooleResponse->end();
                } else {
                    $response->json([
                        'success' => true,
                        'installId' => $installId,
                        'message' => 'Installation completed successfully',
                    ]);
                }
            };

            $installer->performInstallation(
                $httpPort ?: $config->getDefaultHttpPort(),
                $httpsPort ?: $config->getDefaultHttpsPort(),
                $installId,
                $this->state,
                $input,
                $progress,
                $retryStep,
                $config->isUpgrade(),
                $account,
                $onComplete,
            );

            $onComplete();'''

content = content.replace(old, new)

with open('src/Appwrite/Platform/Installer/Http/Installer/Install.php', 'w') as f:
    f.write(content)
PYEOF

# 6. Fix Install.php - add Swoole\Coroutine import
sed -i 's/use Appwrite\\Utopia\\View;/use Appwrite\\Utopia\\View;\nuse Swoole\\Coroutine;/' src/Appwrite/Platform/Tasks/Install.php

# 7. Fix Install.php - add hasExplicitCliParams() method and update web installer logic
python3 << 'PYEOF'
with open('src/Appwrite/Platform/Tasks/Install.php', 'r') as f:
    content = f.read()

# Add hasExplicitCliParams method before the detectDatabaseAdapter method
old = '''    /**
     * Detect the database adapter'''
new = '''    /**
     * Check if any installer-specific CLI params were explicitly passed.
     * When params like --database or --http-port are provided, the user
     * intends to run in CLI mode rather than launching the web installer.
     */
    private function hasExplicitCliParams(): bool
    {
        $argv = $_SERVER['argv'] ?? [];
        foreach ($argv as $arg) {
            if (\\str_starts_with($arg, '--') && !\\str_starts_with($arg, '--interactive')) {
                return true;
            }
        }
        return false;
    }

    /**
     * Detect the database adapter'''
content = content.replace(old, new)

# Update the web server start logic to use hasExplicitCliParams
old = '''        if ($interactive === 'Y' && Console::isInteractive()) {'''
new = '''        // Skip the web installer when explicit CLI params are provided
        if ($interactive === 'Y' && Console::isInteractive() && !$this->hasExplicitCliParams()) {'''
content = content.replace(old, new)

# Update startWebServer call to use $isUpgrade || $existingInstallation
old = '''            $this->startWebServer($defaultHttpPort, $defaultHttpsPort, $organization, $image, $noStart, $vars, $isUpgrade, $detectedDb);'''
new = '''            $this->startWebServer($defaultHttpPort, $defaultHttpsPort, $organization, $image, $noStart, $vars, $isUpgrade || $existingInstallation, $detectedDb);'''
content = content.replace(old, new)

# Update performInstallation signature to add onComplete callback
old = '''        bool $isUpgrade = false,
        array $account = []
    ): void {'''
new = '''        bool $isUpgrade = false,
        array $account = [],
        ?callable $onComplete = null,
    ): void {'''
content = content.replace(old, new)

# Update the tracking code to use onComplete callback and run in coroutine
old = '''                // Track installs
                $this->trackSelfHostedInstall($input, $isUpgrade, $version, $account);'''
new = '''                // Signal completion before tracking so the SSE stream
                // finishes and the frontend can redirect immediately.
                if ($onComplete) {
                    try {
                        $onComplete();
                    } catch (\\Throwable) {
                    }
                }

                // Run tracking in a coroutine when inside a Swoole
                // request so it doesn't block the worker.
                if (Coroutine::getCid() !== -1) {
                    go(function () use ($input, $isUpgrade, $version, $account) {
                        $this->trackSelfHostedInstall($input, $isUpgrade, $version, $account);
                    });
                } else {
                    $this->trackSelfHostedInstall($input, $isUpgrade, $version, $account);
                }'''
content = content.replace(old, new)

# Fix gethostbyname to use @ and fix the condition
old = '''        $hostIp = gethostbyname($domain);'''
new = '''        $hostIp = @gethostbyname($domain);'''
content = content.replace(old, new)

old = '''                'hostIp' => $hostIp !== $domain ? $hostIp : null,'''
new = '''                'ip' => ($hostIp !== false && $hostIp !== $domain) ? $hostIp : null,'''
content = content.replace(old, new)

# Add setConnectTimeout and setTimeout to the client
old = '''            $client = new Client();
            $client
                ->addHeader('Content-Type', 'application/json')'''
new = '''            $client = new Client();
            $client
                ->setConnectTimeout(5000)
                ->setTimeout(5000)
                ->addHeader('Content-Type', 'application/json')'''
content = content.replace(old, new)

with open('src/Appwrite/Platform/Tasks/Install.php', 'w') as f:
    f.write(content)
PYEOF

# 8. Fix AGENTS.md - replace with new content
cat > AGENTS.md << 'ENDOFFILE'
# Appwrite

Self-hosted Backend-as-a-Service platform. Hybrid monolithic-microservice architecture built with PHP 8.3+ on Swoole, delivered as Docker containers.

## Commands

| Command | Purpose |
|---------|---------|
| `docker compose up -d --force-recreate --build` | Build and start all services |
| `docker compose exec appwrite test tests/e2e/Services/[Service]` | Run E2E tests for a service |
| `docker compose exec appwrite test tests/e2e/Services/[Service] --filter=[Method]` | Run a single test method |
| `docker compose exec appwrite test tests/unit/` | Run unit tests |
| `composer format` | Auto-format code (Pint, PSR-12) |
| `composer format <file>` | Format a specific file |
| `composer lint <file>` | Check formatting of a file |
| `composer analyze` | Static analysis (PHPStan level 3) |
| `composer check` | Same as `analyze` |

## Stack

- PHP 8.3+, Swoole 6.x (async runtime, replaces PHP-FPM)
- Utopia PHP framework (HTTP routing, CLI, DI, queue)
- MongoDB (default), MariaDB, MySQL, PostgreSQL (adapters via utopia-php/database)
- Redis (cache, queue, pub/sub)
- Docker + Traefik (reverse proxy)
- PHPUnit 12, Pint (PSR-12), PHPStan level 3

## Project layout

- **src/Appwrite/Platform/Modules/** -- feature modules
- **src/Appwrite/Platform/Workers/** -- background job workers
- **src/Appwrite/Platform/Tasks/** -- CLI tasks
- **app/init.php** -- bootstrap
- **app/init/** -- configs, constants, locales, models, registers, resources, span, database filters/formats
- **bin/** -- CLI entry points
- **tests/e2e/** -- end-to-end tests per service
- **tests/unit/** -- unit tests
- **public/** -- static assets and generated SDKs

## Module structure

Each module under `src/Appwrite/Platform/Modules/{Name}/` contains:

```
Module.php           -- registers all services for the module
Services/Http.php    -- registers HTTP endpoints
Services/Workers.php -- registers background workers
Services/Tasks.php   -- registers CLI tasks
Http/{Service}/      -- endpoint actions (Create.php, Get.php, Update.php, Delete.php, XList.php)
Workers/             -- worker implementations
Tasks/               -- CLI task implementations
```

HTTP endpoint nesting reflects the URL path. Sub-resources get subdirectories.

Register new modules in `src/Appwrite/Platform/Appwrite.php`.

## Action pattern (HTTP endpoints)

...

## Conventions

- PSR-12 formatting enforced by Pint. PSR-4 autoloading.
- `resourceType` values are always **plural**: `'functions'`, `'sites'`, `'deployments'`.
- When updating documents, pass only changed attributes as a sparse Document.
- Avoid introducing dependencies outside the `utopia-php` ecosystem.
- Never hardcode credentials -- use environment variables.
- Code changes may require container restart. No central log location.

## Cross-repo context

Appwrite is the base server for `appwrite/cloud`.
ENDOFFILE

# Verify the patch was applied
grep -q "Runtime::enableCoroutine(SWOOLE_HOOK_ALL)" src/Appwrite/Platform/Installer/Server.php || echo "ERROR: Runtime::enableCoroutine not found"
grep -q "hasExplicitCliParams" src/Appwrite/Platform/Tasks/Install.php || echo "ERROR: hasExplicitCliParams not found"
grep -q "Updating Appwrite" app/views/install/installer/templates/steps/step-5.phtml || echo "ERROR: step-5 copy not updated"
echo "All fixes applied"