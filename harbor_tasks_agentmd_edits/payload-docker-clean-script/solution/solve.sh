#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotent: skip if already applied
if [ -f scripts/docker-clean.js ]; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index b43843ea5a9..d622ed32c41 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -82,7 +82,7 @@ Payload is a monorepo structured around Next.js, containing the core CMS platfor
 - Auto-login is enabled by default with credentials: `dev@payloadcms.com` / `test`
 - To disable: pass `--no-auto-login` flag or set `PAYLOAD_PUBLIC_DISABLE_AUTO_LOGIN=false`
 - Default database is MongoDB (in-memory). Switch to Postgres with `PAYLOAD_DATABASE=postgres`
-- Docker services: `pnpm docker:start` / `pnpm docker:stop` / `pnpm docker:test`
+- Docker services: `pnpm docker:start` / `pnpm docker:clean` / `pnpm docker:test`

 ### Playwright MCP

diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 90e6e24a99b..6f9cc45a35e 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -145,8 +145,8 @@ Then use Docker to start your databases and storage emulators.
 On MacOS, the easiest way to install Docker is to use brew. Simply run `brew install --cask docker`, open the docker desktop app, apply the recommended settings and you're good to go.

 ```bash
-pnpm docker:start  # Start all services (PostgreSQL, MongoDB, storage emulators) with fresh data
-pnpm docker:stop   # Stop all services
+pnpm docker:start  # Clean + start all services (PostgreSQL, MongoDB, storage emulators) with fresh data
+pnpm docker:clean  # Stop and remove all services
 pnpm docker:test   # Test database connections
 ```

diff --git a/package.json b/package.json
index 54d91a14558..5e5a854d275 100644
--- a/package.json
+++ b/package.json
@@ -82,8 +82,8 @@
     "dev:prod": "cross-env NODE_OPTIONS=--no-deprecation tsx ./test/dev.ts --prod",
     "dev:vercel-postgres": "cross-env PAYLOAD_DATABASE=vercel-postgres pnpm runts ./test/dev.ts",
     "devsafe": "node ./scripts/delete-recursively.js '**/.next' && pnpm dev",
-    "docker:start": "docker compose -f test/docker-compose.yml --profile all down -v --remove-orphans 2>/dev/null; docker compose -f test/docker-compose.yml --profile all up -d --wait",
-    "docker:stop": "docker compose -f test/docker-compose.yml --profile all down --remove-orphans",
+    "docker:clean": "node ./scripts/docker-clean.js",
+    "docker:start": "pnpm docker:clean && docker compose -f test/docker-compose.yml --profile all up -d --wait",
     "docker:test": "pnpm runts test/__helpers/shared/db/mongodb/run-test-connection.ts && pnpm runts test/__helpers/shared/db/mongodb-atlas/run-test-connection.ts",
     "force:build": "pnpm run build:core:force",
     "lint": "turbo run lint --log-order=grouped --continue --filter \"!blank\" --filter \"!website\" --filter \"!ecommerce\"",
diff --git a/scripts/docker-clean.js b/scripts/docker-clean.js
new file mode 100644
index 00000000000..4dc543223bd
--- /dev/null
+++ b/scripts/docker-clean.js
@@ -0,0 +1,16 @@
+import { execSync } from 'child_process'
+
+try {
+  execSync(
+    'docker rm -f postgres-payload-test mongodb-payload-test mongot-payload-test mongodb-atlas-payload-test localstack_demo',
+    { stdio: 'ignore' },
+  )
+} catch {
+  // Some or all containers don't exist
+}
+
+try {
+  execSync('docker compose -f test/docker-compose.yml --profile all down -v --remove-orphans', {
+    stdio: 'inherit',
+  })
+} catch {}
diff --git a/test/docker-compose.yml b/test/docker-compose.yml
index 7062f822d1d..c451a1e5586 100644
--- a/test/docker-compose.yml
+++ b/test/docker-compose.yml
@@ -3,8 +3,8 @@ name: payload-monorepo
 # Unified Docker Compose for all Payload test services
 #
 # Usage:
-#   pnpm docker:start  - Start ALL services with fresh data
-#   pnpm docker:stop   - Stop all services
+#   pnpm docker:start  - Clean + start ALL services with fresh data
+#   pnpm docker:clean  - Force-remove containers, volumes, and orphans
 #
 # Profiles (used by CI to start individual services):
 #   --profile all       - Everything

PATCH

echo "Patch applied successfully."
