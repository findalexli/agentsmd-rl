#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotent: skip if already applied
if grep -q 'import type { ExpectStatic } from "vitest"' packages/create-cloudflare/e2e/helpers/framework-helpers.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/create-cloudflare/e2e/helpers/framework-helpers.ts b/packages/create-cloudflare/e2e/helpers/framework-helpers.ts
index e550fee307..5063d72bdb 100644
--- a/packages/create-cloudflare/e2e/helpers/framework-helpers.ts
+++ b/packages/create-cloudflare/e2e/helpers/framework-helpers.ts
@@ -15,8 +15,6 @@ import { detectPackageManager } from "helpers/packageManagers";
 import { retry } from "helpers/retry";
 import * as jsonc from "jsonc-parser";
 import { fetch } from "undici";
-// eslint-disable-next-line no-restricted-imports
-import { expect } from "vitest";
 import { version } from "../../package.json";
 import { getFrameworkMap } from "../../src/templates";
 import {
@@ -31,6 +29,7 @@ import { kill, spawnWithLogging } from "./spawn";
 import type { TemplateConfig } from "../../src/templates";
 import type { RunnerConfig } from "./run-c3";
 import type { Writable } from "node:stream";
+import type { ExpectStatic } from "vitest";

 export type FrameworkTestConfig = RunnerConfig & {
 	testCommitMessage: boolean;
@@ -44,6 +43,7 @@ export type FrameworkTestConfig = RunnerConfig & {
 const packageManager = detectPackageManager();

 export async function runC3ForFrameworkTest(
+	expect: ExpectStatic,
 	framework: string,
 	projectPath: string,
 	logStream: Writable,
@@ -139,6 +139,7 @@ export async function addTestVarsToWranglerToml(projectPath: string) {
 }

 export async function verifyDeployment(
+	expect: ExpectStatic,
 	{ testCommitMessage }: FrameworkTestConfig,
 	frameworkId: string,
 	projectName: string,
@@ -150,7 +151,7 @@ export async function verifyDeployment(
 	}

 	if (testCommitMessage && process.env.CLOUDFLARE_API_TOKEN) {
-		await testDeploymentCommitMessage(projectName, frameworkId);
+		await testDeploymentCommitMessage(expect, projectName, frameworkId);
 	}

 	await retry({ times: 5 }, async () => {
@@ -166,6 +167,7 @@ export async function verifyDeployment(
 }

 export async function verifyDevScript(
+	expect: ExpectStatic,
 	{ verifyDev }: FrameworkTestConfig,
 	{ devScript }: TemplateConfig,
 	projectPath: string,
@@ -243,6 +245,7 @@ export async function verifyDevScript(
 }

 export async function verifyPreviewScript(
+	expect: ExpectStatic,
 	{ verifyPreview }: FrameworkTestConfig,
 	{ previewScript }: TemplateConfig,
 	projectPath: string,
@@ -308,6 +311,7 @@ export async function verifyPreviewScript(
 }

 export async function verifyTypes(
+	expect: ExpectStatic,
 	{ nodeCompat, verifyTypes: verify }: FrameworkTestConfig,
 	{
 		workersTypes,
@@ -362,6 +366,7 @@ export async function verifyTypes(
 }

 export async function verifyCloudflareVitePluginConfigured(
+	expect: ExpectStatic,
 	{ verifyCloudflareVitePluginConfigured: verify }: FrameworkTestConfig,
 	projectPath: string
 ) {
@@ -444,6 +449,7 @@ export function getFrameworkConfig(frameworkKey: string) {
  * Test that C3 added a git commit with the correct message.
  */
 export async function testGitCommitMessage(
+	expect: ExpectStatic,
 	projectName: string,
 	framework: string,
 	projectPath: string
@@ -465,6 +471,7 @@ export async function testGitCommitMessage(
  * Test that we pushed the commit message to the deployment correctly.
  */
 export async function testDeploymentCommitMessage(
+	expect: ExpectStatic,
 	projectName: string,
 	framework: string
 ) {
diff --git a/packages/create-cloudflare/e2e/helpers/to-exist.ts b/packages/create-cloudflare/e2e/helpers/to-exist.ts
index 3665092c42..4eca8bd196 100644
--- a/packages/create-cloudflare/e2e/helpers/to-exist.ts
+++ b/packages/create-cloudflare/e2e/helpers/to-exist.ts
@@ -1,5 +1,5 @@
 import { existsSync } from "node:fs";
-// eslint-disable-next-line no-restricted-imports
+// eslint-disable-next-line no-restricted-imports -- We need to import `expect` from "vitest" so that we can extend it
 import { expect } from "vitest";

 declare module "vitest" {
diff --git a/packages/create-cloudflare/e2e/helpers/workers-helpers.ts b/packages/create-cloudflare/e2e/helpers/workers-helpers.ts
index 0c40f76052..c100cf5fbc 100644
--- a/packages/create-cloudflare/e2e/helpers/workers-helpers.ts
+++ b/packages/create-cloudflare/e2e/helpers/workers-helpers.ts
@@ -3,17 +3,17 @@ import getPort from "get-port";
 import { detectPackageManager } from "helpers/packageManagers";
 import { retry } from "helpers/retry";
 import { fetch } from "undici";
-// eslint-disable-next-line no-restricted-imports
-import { expect } from "vitest";
 import { isExperimental, runDeployTests } from "./constants";
 import { runC3 } from "./run-c3";
 import { kill, spawnWithLogging, waitForExit } from "./spawn";
 import type { WorkerTestConfig } from "../tests/workers/test-config";
 import type { Writable } from "node:stream";
+import type { ExpectStatic } from "vitest";

 const { name: pm } = detectPackageManager();

 export async function runC3ForWorkerTest(
+	expect: ExpectStatic,
 	{ argv, promptHandlers, template }: WorkerTestConfig,
 	projectPath: string,
 	logStream: Writable
@@ -70,6 +70,7 @@ export async function verifyDeployment(
 }

 export async function verifyLocalDev(
+	expect: ExpectStatic,
 	{ verifyDeploy }: WorkerTestConfig,
 	projectPath: string,
 	logStream: Writable
diff --git a/packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts b/packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts
index 220f236c36..53ec4863fd 100644
--- a/packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts
+++ b/packages/create-cloudflare/e2e/tests/frameworks/frameworks.test.ts
@@ -68,6 +68,7 @@ describe

 					try {
 						const deploymentUrl = await runC3ForFrameworkTest(
+							expect,
 							frameworkConfig.id,
 							project.path,
 							logStream,
@@ -96,6 +97,7 @@ describe

 						if (testConfig.testCommitMessage) {
 							await testGitCommitMessage(
+								expect,
 								project.name,
 								frameworkConfig.id,
 								project.path
@@ -104,6 +106,7 @@ describe

 						// Make a request to the deployed project and verify it was successful
 						await verifyDeployment(
+							expect,
 							testConfig,
 							frameworkConfig.id,
 							project.name,
@@ -139,6 +142,7 @@ describe
 						}

 						await verifyDevScript(
+							expect,
 							testConfig,
 							frameworkConfig,
 							project.path,
@@ -146,15 +150,22 @@ describe
 						);

 						await verifyPreviewScript(
+							expect,
 							testConfig,
 							frameworkConfig,
 							project.path,
 							logStream
 						);

-						await verifyTypes(testConfig, frameworkConfig, project.path);
+						await verifyTypes(
+							expect,
+							testConfig,
+							frameworkConfig,
+							project.path
+						);

 						await verifyCloudflareVitePluginConfigured(
+							expect,
 							testConfig,
 							project.path
 						);
diff --git a/packages/create-cloudflare/e2e/tests/workers/workers.test.ts b/packages/create-cloudflare/e2e/tests/workers/workers.test.ts
index 5a1be7e019..b86e1e7080 100644
--- a/packages/create-cloudflare/e2e/tests/workers/workers.test.ts
+++ b/packages/create-cloudflare/e2e/tests/workers/workers.test.ts
@@ -45,6 +45,7 @@ describe
 				async ({ expect, project, logStream }) => {
 					try {
 						const deployedUrl = await runC3ForWorkerTest(
+							expect,
 							testConfig,
 							project.path,
 							logStream
@@ -83,7 +84,12 @@ describe
 							if (deployedUrl) {
 								await verifyDeployment(deployedUrl, verifyDeploy);
 							} else {
-								await verifyLocalDev(testConfig, project.path, logStream);
+								await verifyLocalDev(
+									expect,
+									testConfig,
+									project.path,
+									logStream
+								);
 							}
 						}

diff --git a/packages/create-cloudflare/src/helpers/__tests__/mocks.ts b/packages/create-cloudflare/src/helpers/__tests__/mocks.ts
index fb360c9357..0e98b5d190 100644
--- a/packages/create-cloudflare/src/helpers/__tests__/mocks.ts
+++ b/packages/create-cloudflare/src/helpers/__tests__/mocks.ts
@@ -1,13 +1,12 @@
 import { readdirSync } from "node:fs";
 import { spinner } from "@cloudflare/cli/interactive";
-// eslint-disable-next-line no-restricted-imports
-import { expect, vi } from "vitest";
+import { vi } from "vitest";
 import whichPMRuns from "which-pm-runs";
 import type { Dirent } from "node:fs";

 export const mockPackageManager = (name: string, version = "1.0.0") => {
 	if (!vi.isMockFunction(whichPMRuns)) {
-		expect.fail(
+		throw new Error(
 			"When using `mockPackageManager` you must first call: vi.mock('which-pm-runs');"
 		);
 	}
@@ -18,7 +17,7 @@ export const mockWorkersTypesDirectory = (
 	mockImpl: () => string[] = () => [...mockWorkersTypesDirListing]
 ) => {
 	if (!vi.isMockFunction(readdirSync)) {
-		expect.fail(
+		throw new Error(
 			"When using `mockWorkersTypesDirectory` you must first call: vi.mock('fs');"
 		);
 	}
@@ -33,7 +32,7 @@ export const mockWorkersTypesDirectory = (

 export const mockSpinner = () => {
 	if (!vi.isMockFunction(spinner)) {
-		expect.fail(
+		throw new Error(
 			"When using `mockPackageManager` you must first call: vi.mock('@cloudflare/cli/interactive');"
 		);
 	}

PATCH

echo "Patch applied successfully."
