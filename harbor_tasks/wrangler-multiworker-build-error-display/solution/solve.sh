#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotent: skip if already applied
if grep -q 'isBuildFailure(event.cause)' packages/wrangler/src/api/startDevWorker/DevEnv.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/wrangler/src/api/startDevWorker/BundlerController.ts b/packages/wrangler/src/api/startDevWorker/BundlerController.ts
index 5e34762bfb..e2771d0bd8 100644
--- a/packages/wrangler/src/api/startDevWorker/BundlerController.ts
+++ b/packages/wrangler/src/api/startDevWorker/BundlerController.ts
@@ -173,7 +173,6 @@ export class BundlerController extends Controller {
 				entrypointSource: readFileSync(entrypointPath, "utf8"),
 			});
 		} catch (err) {
-			logger.error("Custom build failed:", err);
 			this.emitErrorEvent({
 				type: "error",
 				reason: "Custom build failed",
@@ -335,9 +334,6 @@ export class BundlerController extends Controller {
 		try {
 			this.#tmpDir = getWranglerTmpDir(event.config.projectRoot, "dev");
 		} catch (e) {
-			logger.error(
-				"Failed to create temporary directory to store built files."
-			);
 			this.emitErrorEvent({
 				type: "error",
 				reason: "Failed to create temporary directory to store built files.",
@@ -348,7 +344,6 @@ export class BundlerController extends Controller {
 		}

 		void this.#startCustomBuild(event.config).catch((err) => {
-			logger.error("Failed to run custom build:", err);
 			this.emitErrorEvent({
 				type: "error",
 				reason: "Failed to run custom build",
@@ -358,7 +353,6 @@ export class BundlerController extends Controller {
 			});
 		});
 		void this.#startBundle(event.config).catch((err) => {
-			logger.error("Failed to start bundler:", err);
 			this.emitErrorEvent({
 				type: "error",
 				reason: "Failed to start bundler",
@@ -368,7 +362,6 @@ export class BundlerController extends Controller {
 			});
 		});
 		void this.#ensureWatchingAssets(event.config).catch((err) => {
-			logger.error("Failed to watch assets:", err);
 			this.emitErrorEvent({
 				type: "error",
 				reason: "Failed to watch assets",
diff --git a/packages/wrangler/src/api/startDevWorker/DevEnv.ts b/packages/wrangler/src/api/startDevWorker/DevEnv.ts
index eab5cf530f..36bc0f937b 100644
--- a/packages/wrangler/src/api/startDevWorker/DevEnv.ts
+++ b/packages/wrangler/src/api/startDevWorker/DevEnv.ts
@@ -2,7 +2,11 @@ import assert from "node:assert";
 import { EventEmitter } from "node:events";
 import { ParseError, UserError } from "@cloudflare/workers-utils";
 import { MiniflareCoreError } from "miniflare";
-import { logger, runWithLogLevel } from "../../logger";
+import {
+	isBuildFailure,
+	isBuildFailureFromCause,
+} from "../../deployment-bundle/build-failures";
+import { logBuildFailure, logger, runWithLogLevel } from "../../logger";
 import { BundlerController } from "./BundlerController";
 import { ConfigController } from "./ConfigController";
 import { LocalRuntimeController } from "./LocalRuntimeController";
@@ -156,6 +160,16 @@ export class DevEnv extends EventEmitter implements ControllerBus {
 		) {
 			logger.error(event.cause);
 		}
+		// Build errors are recoverable by fixing the code and saving
+		else if (event.source === "BundlerController") {
+			if (isBuildFailure(event.cause)) {
+				logBuildFailure(event.cause.errors, event.cause.warnings);
+			} else if (isBuildFailureFromCause(event.cause)) {
+				logBuildFailure(event.cause.cause.errors, event.cause.cause.warnings);
+			} else {
+				logger.error(event.cause.message);
+			}
+		}
 		// if other knowable + recoverable errors occur, handle them here
 		else {
 			// otherwise, re-emit the unknowable errors to the top-level

PATCH

echo "Patch applied successfully."
