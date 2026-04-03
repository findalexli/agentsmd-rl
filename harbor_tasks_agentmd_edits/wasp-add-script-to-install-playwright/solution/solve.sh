#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wasp

# Idempotent: skip if already applied
if grep -q 'test:install-deps' examples/kitchen-sink/package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/workflows/ci-examples-test.yaml b/.github/workflows/ci-examples-test.yaml
index 29719a72dd..7e4479effc 100644
--- a/.github/workflows/ci-examples-test.yaml
+++ b/.github/workflows/ci-examples-test.yaml
@@ -41,10 +41,6 @@ jobs:
         working-directory: examples/${{ matrix.example }}
         run: npm ci

-      - name: Install playwright dependencies for ${{ matrix.example }}
-        working-directory: examples/${{ matrix.example }}
-        run: npx playwright install --with-deps
-
       - name: Setup project environment for ${{ matrix.example }}
         working-directory: examples/${{ matrix.example }}
         run: |
diff --git a/.github/workflows/ci-starters-test.yaml b/.github/workflows/ci-starters-test.yaml
index 124563c2fb..a4ac1e61f3 100644
--- a/.github/workflows/ci-starters-test.yaml
+++ b/.github/workflows/ci-starters-test.yaml
@@ -29,10 +29,6 @@ jobs:
         working-directory: waspc/starters-e2e-tests
         run: npm ci

-      - name: Install playwright dependencies
-        working-directory: waspc/starters-e2e-tests
-        run: npx playwright install --with-deps
-
       - name: Run starters e2e tests
         working-directory: waspc/starters-e2e-tests
         run: npm run test:dev
diff --git a/examples/ask-the-documents/package.json b/examples/ask-the-documents/package.json
index 2a535e0249..a72d46ed78 100644
--- a/examples/ask-the-documents/package.json
+++ b/examples/ask-the-documents/package.json
@@ -8,7 +8,8 @@
   "scripts": {
     "env:pull": "npx dotenv-vault@latest pull development .env.server",
     "env:push": "npx dotenv-vault@latest push development .env.server",
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "@heroui/react": "2.7.5",
diff --git a/examples/kitchen-sink/README.md b/examples/kitchen-sink/README.md
index 361a0aeab3..f4bf8e1438 100644
--- a/examples/kitchen-sink/README.md
+++ b/examples/kitchen-sink/README.md
@@ -84,15 +84,7 @@ wasp-cli start db
 ### End-to-End Tests

 We use `playwright` for e2e tests.
-To run the tests:
-
-1. Install `playwright`'s browser dependencies:
-
-```sh
-npx playwright install --with-deps
-```
-
-2. Run the tests:
+Run the e2e tests with:

 ```sh
 npm run test
diff --git a/examples/kitchen-sink/package.json b/examples/kitchen-sink/package.json
index 55642748b5..910b80732a 100644
--- a/examples/kitchen-sink/package.json
+++ b/examples/kitchen-sink/package.json
@@ -8,7 +8,8 @@
   "scripts": {
     "env:pull": "npx dotenv-vault@latest pull development .env.server",
     "env:push": "npx dotenv-vault@latest push development .env.server",
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "@tanstack/react-query": "~4.41.0",
diff --git a/examples/tutorials/TodoApp/package.json b/examples/tutorials/TodoApp/package.json
index cc1cf0f4ca..a1ec5dde7d 100644
--- a/examples/tutorials/TodoApp/package.json
+++ b/examples/tutorials/TodoApp/package.json
@@ -6,7 +6,8 @@
     ".wasp/out/*"
   ],
   "scripts": {
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "react": "^18.2.0",
diff --git a/examples/tutorials/TodoAppTs/package.json b/examples/tutorials/TodoAppTs/package.json
index 7b319f2bd8..d802638fe3 100644
--- a/examples/tutorials/TodoAppTs/package.json
+++ b/examples/tutorials/TodoAppTs/package.json
@@ -6,7 +6,8 @@
     ".wasp/out/*"
   ],
   "scripts": {
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "react": "^18.2.0",
diff --git a/examples/waspello/package.json b/examples/waspello/package.json
index 7c22e187fa..eba046813b 100644
--- a/examples/waspello/package.json
+++ b/examples/waspello/package.json
@@ -6,7 +6,8 @@
     ".wasp/out/*"
   ],
   "scripts": {
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "@hello-pangea/dnd": "^17.0.0",
diff --git a/examples/waspleau/package.json b/examples/waspleau/package.json
index 72c8858f52..c2d5d5e27b 100644
--- a/examples/waspleau/package.json
+++ b/examples/waspleau/package.json
@@ -6,7 +6,8 @@
     ".wasp/out/*"
   ],
   "scripts": {
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "axios": "^1.4.0",
diff --git a/examples/websockets-realtime-voting/package.json b/examples/websockets-realtime-voting/package.json
index e1ef8da4b0..10a79d363c 100644
--- a/examples/websockets-realtime-voting/package.json
+++ b/examples/websockets-realtime-voting/package.json
@@ -6,7 +6,8 @@
     ".wasp/out/*"
   ],
   "scripts": {
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "express": "~5.1.0",
diff --git a/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/README.md b/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/README.md
index 361a0aeab3..f4bf8e1438 100644
--- a/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/README.md
+++ b/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/README.md
@@ -84,15 +84,7 @@ wasp-cli start db
 ### End-to-End Tests

 We use `playwright` for e2e tests.
-To run the tests:
-
-1. Install `playwright`'s browser dependencies:
-
-```sh
-npx playwright install --with-deps
-```
-
-2. Run the tests:
+Run the e2e tests with:

 ```sh
 npm run test
diff --git a/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/package.json b/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/package.json
index 1af2c1dbff..aefae92e03 100644
--- a/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/package.json
+++ b/waspc/e2e-tests/snapshots/kitchen-sink-golden/wasp-app/package.json
@@ -29,7 +29,8 @@
   "scripts": {
     "env:pull": "npx dotenv-vault@latest pull development .env.server",
     "env:push": "npx dotenv-vault@latest push development .env.server",
-    "test": "DEBUG=pw:webserver playwright test --config e2e-tests/"
+    "test": "npm run test:install-deps && DEBUG=pw:webserver playwright test --config e2e-tests/",
+    "test:install-deps": "playwright install --with-deps"
   },
   "type": "module",
   "workspaces": [
diff --git a/waspc/run b/waspc/run
index db97590479..9f2ebd6973 100755
--- a/waspc/run
+++ b/waspc/run
@@ -38,9 +38,9 @@ WASP_CLI_TESTS_CMD="cabal test wasp-cli-tests"

 WASPLS_TESTS_CMD="cabal test waspls-tests"

-KITCHEN_SINK_E2E_TESTS_CMD="cd $REPOSITORY_ROOT/examples/kitchen-sink && npm i && npx playwright install --with-deps && npm run test"
+KITCHEN_SINK_E2E_TESTS_CMD="cd $REPOSITORY_ROOT/examples/kitchen-sink && npm i && npm run test"

-STARTERS_E2E_TESTS_CMD="cd $PROJECT_ROOT/starters-e2e-tests && npm i && npx playwright install --with-deps && npm run test:dev"
+STARTERS_E2E_TESTS_CMD="cd $PROJECT_ROOT/starters-e2e-tests && npm i && npm run test:dev"

 function run_examples_e2e_tests() {
   local paths=(
@@ -54,7 +54,7 @@ function run_examples_e2e_tests() {
   )

   for path in "${paths[@]}"; do
-    eval "(cd $REPOSITORY_ROOT/$path && npm i && npx playwright install --with-deps && npm run test)"
+    eval "(cd $REPOSITORY_ROOT/$path && npm i && npm run test)"
     local status=$?
     if [ $status -ne 0 ]; then
       echo -e "${RED}E2E tests failed in $path${RESET}"
diff --git a/waspc/starters-e2e-tests/package.json b/waspc/starters-e2e-tests/package.json
index 6a0eaef81a..9816b80c28 100644
--- a/waspc/starters-e2e-tests/package.json
+++ b/waspc/starters-e2e-tests/package.json
@@ -6,8 +6,9 @@
   "scripts": {
     "build": "tsc",
     "start": "node ./dist/src/main.js",
-    "test": "npm run build && DEBUG=pw:webserver npm run start -- --wasp-cli-command wasp",
-    "test:dev": "npm run build && DEBUG=pw:webserver npm run start -- --wasp-cli-command wasp-cli"
+    "test": "npm run build && npm run test:install-deps && DEBUG=pw:webserver npm run start -- --wasp-cli-command wasp",
+    "test:dev": "npm run build && npm run test:install-deps && DEBUG=pw:webserver npm run start -- --wasp-cli-command wasp-cli",
+    "test:install-deps": "playwright install --with-deps"
   },
   "dependencies": {
     "@commander-js/extra-typings": "^14.0.0",

PATCH

echo "Patch applied successfully."
