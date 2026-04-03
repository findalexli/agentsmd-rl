#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slate

# Idempotent: skip if already applied
if grep -q 'test:integration-docker' package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/docs/general/contributing.md b/docs/general/contributing.md
index 6cf590887a..b521209ac1 100644
--- a/docs/general/contributing.md
+++ b/docs/general/contributing.md
@@ -99,6 +99,40 @@ This will fix Prettier and Eslint errors.
 
 To run integrations with [Playwright](https://playwright.dev/), first run `yarn start` to run the examples website, then run `yarn playwright` in a separate session to open the Playwright test suite. Or alternatively, run just `yarn test:integration-local`.
 
+### Running integration tests in Docker
+
+If tests fail on CI but pass locally (often due to OS differences), you can run tests in a Docker container that replicates the same environment as CI.
+
+**Prerequisites:** The project must be built first (same as running tests locally).
+
+```text
+yarn test:integration-docker
+```
+
+The script will automatically:
+
+1. Start the development server (if not already running)
+2. Run tests inside a Docker container
+3. Stop the server when tests complete
+
+You can also pass additional arguments to the test runner. For example, to run a specific test file:
+
+```text
+yarn test:integration-docker playwright/integration/slate-react/selection.test.ts
+```
+
+Or run a specific browser project:
+
+```text
+yarn test:integration-docker --project=chromium
+```
+
+You can combine arguments as well:
+
+```text
+yarn test:integration-docker playwright/integration/examples/check-lists.test.ts --project chromium
+```
+
 ## Testing Input Methods
 
 [Here's a helpful page](https://github.com/Microsoft/vscode/wiki/IME-Test) detailing how to test various input scenarios on Windows, Mac and Linux.
diff --git a/package.json b/package.json
index 220cf9e1ab..1665b432c1 100644
--- a/package.json
+++ b/package.json
@@ -33,6 +33,7 @@
     "test:inspect": "yarn test --inspect-brk",
     "test:integration": "playwright install --with-deps && run-p -r serve playwright",
     "test:integration-local": "playwright install && run-p -r serve playwright",
+    "test:integration-docker": "./playwright/docker/run-tests.sh",
     "test:mocha": "mocha --require ./config/babel/register.cjs ./packages/{slate,slate-history,slate-hyperscript}/test/**/*.{js,ts}",
     "test:jest": "jest --config jest.config.js",
     "tsc:examples": "tsc --project ./site/tsconfig.example.json",
diff --git a/playwright.config.ts b/playwright.config.ts
index 1dbd7156d0..e3fe6ea5ee 100644
--- a/playwright.config.ts
+++ b/playwright.config.ts
@@ -74,7 +74,8 @@ const config: PlaywrightTestConfig = {
     /* Maximum time each action such as `click()` can take. Defaults to 0 (no limit). */
     actionTimeout: 0,
     /* Base URL to use in actions like `await page.goto('/')`. */
-    // baseURL: 'http://localhost:3000',
+    // Can be overridden with PLAYWRIGHT_BASE_URL env var (used by Docker tests)
+    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
 
     /* Collect trace if the first attempt fails. See https://playwright.dev/docs/trace-viewer */
     trace: 'retain-on-first-failure',
diff --git a/playwright/docker/Dockerfile b/playwright/docker/Dockerfile
new file mode 100644
index 0000000000..298edaf666
--- /dev/null
+++ b/playwright/docker/Dockerfile
@@ -0,0 +1,24 @@
+# Use Node.js 22 base (Debian-based, similar to CI ubuntu-22.04)
+# Note: Can't use official Playwright image because Yarn PnP uses absolute paths
+# that break when the project is mounted at a different location in Docker
+FROM node:22-slim
+
+# Install curl (for health checks) and socat (for localhost port forwarding)
+RUN apt-get update && \
+    apt-get install -y curl socat && \
+    apt-get clean && \
+    rm -rf /var/lib/apt/lists/*
+
+RUN corepack enable
+
+WORKDIR /app
+
+# Install globally to avoid Yarn PnP path resolution issues in container
+RUN npm install -g @playwright/test@1.52.0
+
+RUN playwright install --with-deps
+
+COPY entrypoint.sh /entrypoint.sh
+RUN chmod +x /entrypoint.sh
+
+ENTRYPOINT ["/entrypoint.sh"]
diff --git a/playwright/docker/docker-compose.yml b/playwright/docker/docker-compose.yml
new file mode 100644
index 0000000000..fc55d700ab
--- /dev/null
+++ b/playwright/docker/docker-compose.yml
@@ -0,0 +1,17 @@
+services:
+  test-runner:
+    build:
+      context: .
+      dockerfile: Dockerfile
+    volumes:
+      - ../..:/app:ro
+      - ../../test-results:/app/test-results:rw
+    environment:
+      - CI=true
+      - PLAYWRIGHT_BASE_URL=http://host.docker.internal:3000
+      - NODE_PATH=/usr/local/lib/node_modules
+    extra_hosts:
+      - "host.docker.internal:host-gateway"
+      - "localhost:host-gateway"
+    stdin_open: false
+    tty: false
diff --git a/playwright/docker/entrypoint.sh b/playwright/docker/entrypoint.sh
new file mode 100644
index 0000000000..7eaf46d95e
--- /dev/null
+++ b/playwright/docker/entrypoint.sh
@@ -0,0 +1,41 @@
+#!/bin/bash
+set -e
+
+echo "=========================================="
+echo "Docker Integration Tests"
+echo "=========================================="
+
+# Default to host.docker.internal if not overridden
+if [ -z "$PLAYWRIGHT_BASE_URL" ]; then
+  PLAYWRIGHT_BASE_URL="http://host.docker.internal:3000"
+fi
+
+echo "Waiting for development server on host..."
+
+timeout=60
+elapsed=0
+while ! curl -s "$PLAYWRIGHT_BASE_URL" > /dev/null; do
+  if [ $elapsed -ge $timeout ]; then
+    echo "❌ Server did not start within ${timeout}s"
+    exit 1
+  fi
+  sleep 1
+  elapsed=$((elapsed + 1))
+done
+
+echo "✓ Server is ready on host"
+
+# Forward localhost:3000 to host for tests that use hardcoded localhost URLs
+echo "Setting up port forwarding from localhost:3000 to host..."
+socat TCP-LISTEN:3000,fork,reuseaddr TCP:host.docker.internal:3000 &
+SOCAT_PID=$!
+
+sleep 1
+
+cd /app/playwright/docker
+playwright test --config=playwright.config.docker.ts "$@"
+TEST_EXIT_CODE=$?
+
+kill $SOCAT_PID 2>/dev/null || true
+
+exit $TEST_EXIT_CODE
diff --git a/playwright/docker/playwright.config.docker.ts b/playwright/docker/playwright.config.docker.ts
new file mode 100644
index 0000000000..3e4a216f6f
--- /dev/null
+++ b/playwright/docker/playwright.config.docker.ts
@@ -0,0 +1,10 @@
+import type { PlaywrightTestConfig } from '@playwright/test'
+import baseConfig from '../../playwright.config'
+
+const config: PlaywrightTestConfig = {
+  ...baseConfig,
+  testDir: '..',
+  outputDir: '../../test-results/docker',
+}
+
+export default config
diff --git a/playwright/docker/run-tests.sh b/playwright/docker/run-tests.sh
new file mode 100755
index 0000000000..c998cb552f
--- /dev/null
+++ b/playwright/docker/run-tests.sh
@@ -0,0 +1,53 @@
+#!/bin/bash
+
+# Orchestrates running integration tests: starts dev server if needed, runs Docker tests, cleans up
+
+set -e
+
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
+
+cd "$PROJECT_ROOT"
+
+echo "=========================================="
+echo "Docker Integration Tests"
+echo "=========================================="
+
+if curl -s http://localhost:3000 > /dev/null 2>&1; then
+  echo "✓ Development server already running on port 3000"
+  SERVER_STARTED_HERE=false
+else
+  echo "Starting development server..."
+  yarn serve > /dev/null 2>&1 &
+  SERVER_PID=$!
+  SERVER_STARTED_HERE=true
+
+  trap "echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null || true" EXIT
+
+  echo "Waiting for server to be ready..."
+  timeout=60
+  elapsed=0
+  while ! curl -s http://localhost:3000 > /dev/null 2>&1; do
+    if [ $elapsed -ge $timeout ]; then
+      echo "❌ Server did not start within ${timeout}s"
+      exit 1
+    fi
+    sleep 1
+    elapsed=$((elapsed + 1))
+  done
+  echo "✓ Server is ready"
+fi
+
+echo "Running tests in Docker..."
+cd "$SCRIPT_DIR"
+
+docker compose run --rm test-runner "$@"
+TEST_EXIT_CODE=$?
+
+# Only stop server if we started it
+if [ "$SERVER_STARTED_HERE" = true ]; then
+  echo "Stopping development server..."
+  kill $SERVER_PID 2>/dev/null || true
+fi
+
+exit $TEST_EXIT_CODE

PATCH

echo "Patch applied successfully."
