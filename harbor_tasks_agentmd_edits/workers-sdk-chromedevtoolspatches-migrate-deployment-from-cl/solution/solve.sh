#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotent: skip if already applied
if grep -q 'cloudflare-devtools.devprod.workers.dev' packages/miniflare/src/plugins/core/inspector-proxy/inspector-proxy-controller.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.changeset/migrate-devtools-to-workers-assets.md b/.changeset/migrate-devtools-to-workers-assets.md
new file mode 100644
index 0000000000..c91d4c68d7
--- /dev/null
+++ b/.changeset/migrate-devtools-to-workers-assets.md
@@ -0,0 +1,11 @@
+---
+"@cloudflare/chrome-devtools-patches": patch
+"wrangler": patch
+"miniflare": patch
+---
+
+Migrate chrome-devtools-patches deployment from Cloudflare Pages to Workers + Assets
+
+The DevTools frontend is now deployed as a Cloudflare Workers + Assets project instead of a Cloudflare Pages project. This uses `wrangler deploy` for production deployments and `wrangler versions upload` for PR preview deployments.
+
+The inspector proxy origin allowlists in both wrangler and miniflare have been updated to accept connections from the new `workers.dev` domain patterns, while retaining the legacy `pages.dev` patterns for backward compatibility.
diff --git a/.github/workflows/deploy-previews.yml b/.github/workflows/deploy-previews.yml
index 27812207a2..0100d5f8ab 100644
--- a/.github/workflows/deploy-previews.yml
+++ b/.github/workflows/deploy-previews.yml
@@ -52,9 +52,10 @@ jobs:
       - name: Deploy Wrangler DevTools preview
         if: contains(github.event.*.labels.*.name, 'preview:chrome-devtools-patches')
         run: |
-          output=$(pnpm --filter @cloudflare/chrome-devtools-patches run deploy)
+          output=$(pnpm --filter @cloudflare/chrome-devtools-patches run deploy:preview)
+          echo "Command output: $output"
           echo "Extracting deployed URL from command output"
-          url=$(echo "$output" | sed -nE "s/.*Take a peek over at (\S+).*/\1/p")
+          url=$(echo "$output" | sed -nE "s/.*Version Preview URL: ([^[:space:]]+).*/\1/p")
           echo "Extracted URL: $url"
           echo "VITE_DEVTOOLS_PREVIEW_URL=$url" >> $GITHUB_ENV
         env:
@@ -84,5 +85,5 @@ jobs:

             ```
             - https://devtools.devprod.cloudflare.dev/js_app?theme=systemPreferred&ws=127.0.0.1%3A9229%2Fws&domain=tester&debugger=true
-            + https://8afc7d3d.cloudflare-devtools.pages.dev/js_app?theme=systemPreferred&ws=127.0.0.1%3A9229%2Fws&domain=tester&debugger=true
+            + ${{ env.VITE_DEVTOOLS_PREVIEW_URL }}/js_app?theme=systemPreferred&ws=127.0.0.1%3A9229%2Fws&domain=tester&debugger=true
             ```
diff --git a/packages/chrome-devtools-patches/Makefile b/packages/chrome-devtools-patches/Makefile
index d54fbc2a3b..95d3741940 100644
--- a/packages/chrome-devtools-patches/Makefile
+++ b/packages/chrome-devtools-patches/Makefile
@@ -21,7 +21,10 @@ devtools-frontend/out/Default/gen/front_end: devtools-frontend
 	cd devtools-frontend && PATH="$(PATH_WITH_DEPOT)" $(ROOT)/depot/autoninja -C out/Default

 publish: cleanup devtools-frontend/out/Default/gen/front_end
-	npx wrangler pages deploy --project-name cloudflare-devtools devtools-frontend/out/Default/gen/front_end
+	npx wrangler deploy
+
+publish-preview: cleanup devtools-frontend/out/Default/gen/front_end
+	npx wrangler versions upload

 cleanup:
 	rm -rf devtools-frontend .gclient* .cipd node_modules depot
diff --git a/packages/chrome-devtools-patches/README.md b/packages/chrome-devtools-patches/README.md
index e20e4e8ed2..6f12095d98 100644
--- a/packages/chrome-devtools-patches/README.md
+++ b/packages/chrome-devtools-patches/README.md
@@ -1,4 +1,4 @@
-# Workers Devtools Pages Project
+# Workers Devtools

 This package contains a Workers specific version of Chrome Devtools that is used by the Wrangler dev command and other applications. It is a customized fork of Chrome DevTools specifically tailored for debugging Cloudflare Workers. This package provides Worker-specific functionality through carefully maintained patches on top of Chrome DevTools.

@@ -76,11 +76,15 @@ When making changes:

 ## Deployment

+This package is deployed as a Cloudflare Workers + Assets project. The static DevTools frontend is served directly from Workers Assets, configured via `wrangler.jsonc`.
+
 Deployments are managed by GitHub Actions:

-- deploy-pages-previews.yml:
+- deploy-previews.yml:
   - Runs on any PR that has the `preview:chrome-devtools-patches` label.
-  - Deploys a preview, which can then be accessed via [https://<SHA>.cloudflare-devtools.pages.dev/].
+  - Uploads a preview version (without activating it in production) via `wrangler versions upload`.
+  - The preview URL is posted as a comment on the PR.
 - changesets.yml:
   - Runs when a "Version Packages" PR, containing a changeset that touches this package, is merged to `main`.
-  - Deploys this package to production, which can then be accessed via [https://cloudflare-devtools.pages.dev/].
+  - Deploys this package to production via `wrangler deploy`.
+  - Production is accessible via the custom domain [https://devtools.devprod.cloudflare.dev/].
diff --git a/packages/chrome-devtools-patches/package.json b/packages/chrome-devtools-patches/package.json
index 098e8432c8..192bf18cd8 100644
--- a/packages/chrome-devtools-patches/package.json
+++ b/packages/chrome-devtools-patches/package.json
@@ -11,6 +11,7 @@
 	"author": "workers-devprod@cloudflare.com",
 	"scripts": {
 		"deploy": "CLOUDFLARE_ACCOUNT_ID=e35fd947284363a46fd7061634477114 make publish",
+		"deploy:preview": "CLOUDFLARE_ACCOUNT_ID=e35fd947284363a46fd7061634477114 make publish-preview",
 		"testenv": "make testenv"
 	},
 	"devDependencies": {
diff --git a/packages/chrome-devtools-patches/wrangler.jsonc b/packages/chrome-devtools-patches/wrangler.jsonc
new file mode 100644
index 0000000000..68f024d3dc
--- /dev/null
+++ b/packages/chrome-devtools-patches/wrangler.jsonc
@@ -0,0 +1,10 @@
+{
+	"$schema": "./node_modules/wrangler/config-schema.json",
+	"name": "cloudflare-devtools",
+	"compatibility_date": "2025-07-01",
+	"assets": {
+		"directory": "devtools-frontend/out/Default/gen/front_end",
+	},
+	"preview_urls": true,
+	"workers_dev": true,
+}
diff --git a/packages/miniflare/src/plugins/core/inspector-proxy/inspector-proxy-controller.ts b/packages/miniflare/src/plugins/core/inspector-proxy/inspector-proxy-controller.ts
index 0483ed7481..04b8605f1a 100644
--- a/packages/miniflare/src/plugins/core/inspector-proxy/inspector-proxy-controller.ts
+++ b/packages/miniflare/src/plugins/core/inspector-proxy/inspector-proxy-controller.ts
@@ -336,6 +336,10 @@ function getWebsocketURL(host: string, port: number): URL {
 const ALLOWED_HOST_HOSTNAMES = ["127.0.0.1", "[::1]", "localhost"];
 const ALLOWED_ORIGIN_HOSTNAMES = [
 	"devtools.devprod.cloudflare.dev",
+	// Workers + Assets (current deployment)
+	"cloudflare-devtools.devprod.workers.dev",
+	/^[a-z0-9]+-cloudflare-devtools\.devprod\.workers\.dev$/,
+	// Cloudflare Pages (legacy deployment)
 	"cloudflare-devtools.pages.dev",
 	/^[a-z0-9]+\.cloudflare-devtools\.pages\.dev$/,
 	"127.0.0.1",
diff --git a/packages/wrangler/templates/startDevWorker/InspectorProxyWorker.ts b/packages/wrangler/templates/startDevWorker/InspectorProxyWorker.ts
index f2c95498e9..e426d1d96a 100644
--- a/packages/wrangler/templates/startDevWorker/InspectorProxyWorker.ts
+++ b/packages/wrangler/templates/startDevWorker/InspectorProxyWorker.ts
@@ -24,6 +24,10 @@ import type {
 const ALLOWED_HOST_HOSTNAMES = ["127.0.0.1", "[::1]", "localhost"];
 const ALLOWED_ORIGIN_HOSTNAMES = [
 	"devtools.devprod.cloudflare.dev",
+	// Workers + Assets (current deployment)
+	"cloudflare-devtools.devprod.workers.dev",
+	/^[a-z0-9]+-cloudflare-devtools\.devprod\.workers\.dev$/,
+	// Cloudflare Pages (legacy deployment)
 	"cloudflare-devtools.pages.dev",
 	/^[a-z0-9]+\.cloudflare-devtools\.pages\.dev$/,
 	"127.0.0.1",

PATCH

echo "Patch applied successfully."
