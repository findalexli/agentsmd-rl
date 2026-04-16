#!/bin/bash
# Gold solution - applies the fix from PR #39183
set -e

cd /workspace/superset

# Idempotency check - skip if already applied
if grep -q "DISABLE_TS_CHECKER" superset-frontend/webpack.config.js 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/docker-compose-light.yml b/docker-compose-light.yml
index 1d0a4a90be7b..458708bd26ab 100644
--- a/docker-compose-light.yml
+++ b/docker-compose-light.yml
@@ -115,6 +115,10 @@ services:
       DATABASE_HOST: db-light
       DATABASE_DB: superset_light
       POSTGRES_DB: superset_light
+      EXAMPLES_HOST: db-light
+      EXAMPLES_DB: superset_light
+      EXAMPLES_USER: superset
+      EXAMPLES_PASSWORD: superset
       SUPERSET_CONFIG_PATH: /app/docker/pythonpath_dev/superset_config_docker_light.py
       GITHUB_HEAD_REF: ${GITHUB_HEAD_REF:-}
       GITHUB_SHA: ${GITHUB_SHA:-}
@@ -137,6 +141,10 @@ services:
       DATABASE_HOST: db-light
       DATABASE_DB: superset_light
       POSTGRES_DB: superset_light
+      EXAMPLES_HOST: db-light
+      EXAMPLES_DB: superset_light
+      EXAMPLES_USER: superset
+      EXAMPLES_PASSWORD: superset
       SUPERSET_CONFIG_PATH: /app/docker/pythonpath_dev/superset_config_docker_light.py
     healthcheck:
       disable: true
@@ -157,6 +165,7 @@ services:
       BUILD_SUPERSET_FRONTEND_IN_DOCKER: true
       NPM_RUN_PRUNE: false
       SCARF_ANALYTICS: "${SCARF_ANALYTICS:-}"
+      DISABLE_TS_CHECKER: "${DISABLE_TS_CHECKER:-true}"
       # configuring the dev-server to use the host.docker.internal to connect to the backend
       superset: "http://superset-light:8088"
       # Webpack dev server must bind to 0.0.0.0 to be accessible from outside the container
diff --git a/docker/docker-bootstrap.sh b/docker/docker-bootstrap.sh
index 58d71d25c250..d20f28007f1b 100755
--- a/docker/docker-bootstrap.sh
+++ b/docker/docker-bootstrap.sh
@@ -80,7 +80,7 @@ case "${1}" in
     ;;
   app)
     echo "Starting web app (using development server)..."
-    flask run -p $PORT --reload --debugger --without-threads --host=0.0.0.0 --exclude-patterns "*/node_modules/*:*/.venv/*:*/build/*:*/__pycache__/*"
+    flask run -p $PORT --reload --debugger --host=0.0.0.0 --exclude-patterns "*/node_modules/*:*/.venv/*:*/build/*:*/__pycache__/*:*/superset-frontend/*"
     ;;
   app-gunicorn)
     echo "Starting web app..."
diff --git a/superset-frontend/webpack.config.js b/superset-frontend/webpack.config.js
index 0963b3454beb..f3926c3f968d 100644
--- a/superset-frontend/webpack.config.js
+++ b/superset-frontend/webpack.config.js
@@ -219,11 +219,15 @@ if (!isDevMode) {

 // TypeScript type checking and .d.ts generation
 // SWC handles transpilation; this plugin handles type checking separately.
-// build: true enables project references so .d.ts files are auto-generated.
+// build: true enables project references so .d.ts files are auto-generated
+// across the monorepo when editing plugins/packages.
 // mode: 'write-references' writes .d.ts output (no manual `npm run plugins:build` needed).
-// Story files are excluded because they import @storybook-shared which resolves
-// outside plugin rootDir ("src"), causing errors in --build mode.
-if (isDevMode) {
+// Set DISABLE_TS_CHECKER=true to skip this plugin entirely (~2-3 GB savings).
+// Type errors are still caught by pre-commit and CI.
+const disableTsChecker = ['true', '1'].includes(
+  (process.env.DISABLE_TS_CHECKER || '').toLowerCase(),
+);
+if (isDevMode && !disableTsChecker) {
   plugins.push(
     new ForkTsCheckerWebpackPlugin({
       async: true,
@@ -535,7 +539,7 @@ const config = {
           {
             loader: 'css-loader',
             options: {
-              sourceMap: true,
+              sourceMap: !isDevMode,
             },
           },
         ],
@@ -619,10 +623,23 @@ const config = {
   watchOptions: isDevMode
     ? {
         // Watch all plugin and package source directories
-        ignored: ['**/node_modules', '**/.git', '**/lib', '**/esm', '**/dist'],
-        // Poll less frequently to reduce file handles
+        ignored: [
+          '**/node_modules',
+          '**/.git',
+          '**/lib',
+          '**/esm',
+          '**/dist',
+          '**/.temp_cache',
+          '**/coverage',
+          '**/*.test.*',
+          '**/*.stories.*',
+          '**/cypress-base',
+          '**/*.geojson',
+        ],
+        // Poll-based watching is needed in Docker/VM where native fs events
+        // don't propagate from host to container.
         poll: 2000,
-        // Aggregate changes for 500ms before rebuilding
+        // Aggregate changes before rebuilding
         aggregateTimeout: 500,
       }
     : undefined,
PATCH

echo "Patch applied successfully."
