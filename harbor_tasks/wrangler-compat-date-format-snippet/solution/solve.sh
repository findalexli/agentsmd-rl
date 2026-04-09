#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotent: skip if already applied
if grep -q 'formatConfigSnippet' packages/wrangler/src/api/startDevWorker/ConfigController.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/wrangler/src/api/startDevWorker/ConfigController.ts b/packages/wrangler/src/api/startDevWorker/ConfigController.ts
index ea8081dfc8..e2f08a9ef7 100644
--- a/packages/wrangler/src/api/startDevWorker/ConfigController.ts
+++ b/packages/wrangler/src/api/startDevWorker/ConfigController.ts
@@ -3,6 +3,7 @@ import path from "node:path";
 import { resolveDockerHost } from "@cloudflare/containers-shared";
 import {
 	configFileName,
+	formatConfigSnippet,
 	getTodaysCompatDate,
 	getDisableConfigWatching,
 	getDockerPath,
@@ -482,7 +483,7 @@ function getDevCompatibilityDate(
 	if (config?.configPath && compatibilityDate === undefined) {
 		logger.warn(
 			`No compatibility_date was specified. Using today's date: ${todaysDate}.\n` +
-				`❯❯ Add one to your ${configFileName(config.configPath)} file: compatibility_date = "${todaysDate}", or\n` +
+				`❯❯ Add one to your ${configFileName(config.configPath)} file: ${formatConfigSnippet({ compatibility_date: todaysDate }, config.configPath, false).trim()}, or\n` +
 				`❯❯ Pass it in your terminal: wrangler dev [<SCRIPT>] --compatibility-date=${todaysDate}\n\n` +
 				"See https://developers.cloudflare.com/workers/platform/compatibility-dates/ for more information."
 		);

PATCH

echo "Patch applied successfully."
