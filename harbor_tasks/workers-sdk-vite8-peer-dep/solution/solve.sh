#!/bin/bash
set -euo pipefail
cd /workspace/workers-sdk

# Idempotency check
if grep -q '|| \^8\.0\.0' packages/vite-plugin-cloudflare/package.json; then
    echo "Patch already applied."
    exit 0
fi

git apply <<'PATCH'
diff --git a/.changeset/green-buses-melt.md b/.changeset/green-buses-melt.md
new file mode 100644
index 0000000000..137c3e21e3
--- /dev/null
+++ b/.changeset/green-buses-melt.md
@@ -0,0 +1,7 @@
+---
+"@cloudflare/vite-plugin": minor
+---
+
+Add Vite 8 to the supported peer dependency range
+
+The package now lists Vite 8 in its peer dependency range, so installs with Vite 8 no longer show a peer dependency warning.
diff --git a/.github/workflows/vite-plugin-playgrounds.yml b/.github/workflows/vite-plugin-playgrounds.yml
index 64885fb5af..756448ca48 100644
--- a/.github/workflows/vite-plugin-playgrounds.yml
+++ b/.github/workflows/vite-plugin-playgrounds.yml
@@ -28,7 +28,7 @@ jobs:
           - os: ubuntu-latest
             vite: "vite-6"
           - os: ubuntu-latest
-            vite: vite-8-beta
+            vite: vite-8
     runs-on: ${{ matrix.os }}
     steps:
       - name: Checkout Repo
@@ -60,10 +60,10 @@ jobs:
         if: steps.changes.outputs.everything_but_markdown == 'true' && matrix.vite == 'vite-6'
         run: |
           pnpm update -r --no-save vite@6.4.1
-      - name: Upgrade to Vite 8 beta
-        if: steps.changes.outputs.everything_but_markdown == 'true' && matrix.vite == 'vite-8-beta'
+      - name: Upgrade to Vite 8
+        if: steps.changes.outputs.everything_but_markdown == 'true' && matrix.vite == 'vite-8'
         run: |
-          pnpm update -r --no-save vite@beta
+          pnpm update -r --no-save vite@^8.0.0
       - name: Run dev playground tests
         if: steps.changes.outputs.everything_but_markdown == 'true'
         # We use `--only` to prevent TurboRepo from rebuilding dependencies
diff --git a/packages/vite-plugin-cloudflare/AGENTS.md b/packages/vite-plugin-cloudflare/AGENTS.md
index 68eeac0091..608aa76e83 100644
--- a/packages/vite-plugin-cloudflare/AGENTS.md
+++ b/packages/vite-plugin-cloudflare/AGENTS.md
@@ -29,4 +29,4 @@ Vite plugin for Cloudflare Workers development. Exports `cloudflare()` plugin fa

 - Unit tests: `.spec.ts` in `__tests__/`
 - E2E tests: `.test.ts` in `e2e/`, own vitest config
-- Playground tests: Playwright-based, tested across Vite 6/7/8-beta in CI
+- Playground tests: Playwright-based, tested across Vite 6/7/8 in CI
diff --git a/packages/vite-plugin-cloudflare/package.json b/packages/vite-plugin-cloudflare/package.json
index 8c8cf607c7..fa057dd6d0 100644
--- a/packages/vite-plugin-cloudflare/package.json
+++ b/packages/vite-plugin-cloudflare/package.json
@@ -74,7 +74,7 @@
 		"vitest": "catalog:vitest-3"
 	},
 	"peerDependencies": {
-		"vite": "^6.1.0 || ^7.0.0",
+		"vite": "^6.1.0 || ^7.0.0 || ^8.0.0",
 		"wrangler": "workspace:^"
 	},
 	"publishConfig": {
PATCH
