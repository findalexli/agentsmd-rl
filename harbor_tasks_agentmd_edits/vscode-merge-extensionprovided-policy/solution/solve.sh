#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotent: skip if already applied
if grep -q 'getDistroProductJson' src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/skills/add-policy/SKILL.md b/.github/skills/add-policy/SKILL.md
index 64119b056bad3..40f1cc3a37635 100644
--- a/.github/skills/add-policy/SKILL.md
+++ b/.github/skills/add-policy/SKILL.md
@@ -124,15 +124,62 @@ npm run compile-check-ts-native
 Regenerate the auto-generated policy catalog:
 
 ```bash
-npm run transpile-client && ./scripts/code.sh --export-policy-data
+npm run export-policy-data
 ```
 
+This script handles transpilation, sets up `GITHUB_TOKEN` (via `gh` CLI or GitHub OAuth device flow), and runs `--export-policy-data`. The export command reads extension configuration policies from the distro's `product.json` via the GitHub API and merges them into the output.
+
 This updates `build/lib/policies/policyData.jsonc`. **Never edit this file manually.** Verify your new policy appears in the output.  You will need code review from a codeowner to merge the change to main.
 
 
 ## Policy for extension-provided settings
 
-For an extension author to provide policies for their extension's settings, a change must be made in `vscode-distro` to the `product.json`.
+Extension authors cannot add `policy:` fields directly—their settings are defined in the extension's `package.json`, not in VS Code core. Instead, policies for extension settings are defined in `vscode-distro`'s `product.json` under the `extensionConfigurationPolicy` key.
+
+### How it works
+
+1. **Source of truth**: The `extensionConfigurationPolicy` map lives in `vscode-distro` under `mixin/{quality}/product.json` (stable, insider, exploration).
+2. **Runtime**: When VS Code starts with a distro-mixed `product.json`, `configurationExtensionPoint.ts` reads `extensionConfigurationPolicy` and attaches matching `policy` objects to extension-contributed configuration properties.
+3. **Export/build**: The `--export-policy-data` command fetches the distro's `product.json` at the commit pinned in `package.json` and merges extension policies into the output. Use `npm run export-policy-data` which sets up authentication automatically.
+
+### Distro format
+
+Each entry in `extensionConfigurationPolicy` must include:
+
+```json
+"extensionConfigurationPolicy": {
+    "publisher.extension.settingName": {
+        "name": "PolicyName",
+        "category": "InteractiveSession",
+        "minimumVersion": "1.99",
+        "description": "Human-readable description."
+    }
+}
+```
+
+- `name`: PascalCase policy name, unique across all policies
+- `category`: Must be a valid `PolicyCategory` enum value (e.g., `InteractiveSession`, `Extensions`)
+- `minimumVersion`: The VS Code version that first shipped this policy
+- `description`: Human-readable description string used to generate localization key/value pairs for ADMX/ADML/macOS/Linux policy artifacts
+
+### Adding a new extension policy
+
+1. Add the entry to `extensionConfigurationPolicy` in **all three** quality `product.json` files in `vscode-distro` (`mixin/stable/`, `mixin/insider/`, `mixin/exploration/`)
+2. Update the `distro` commit hash in `package.json` to point to the distro commit that includes your new entry — the export command fetches extension policies from the pinned distro commit
+3. Regenerate `policyData.jsonc` by running `npm run export-policy-data` (see Step 4 above)
+4. Update the test fixture at `src/vs/workbench/contrib/policyExport/test/node/extensionPolicyFixture.json` with the new entry
+
+### Test fixtures
+
+The file `src/vs/workbench/contrib/policyExport/test/node/extensionPolicyFixture.json` is a test fixture that must stay in sync with the extension policies in the checked-in `policyData.jsonc`. When extension policies are added or changed in the distro, this fixture must be updated to match — otherwise the integration test will fail because the test output (generated from the fixture) won't match the checked-in file (generated from the real distro).
+
+### Downstream consumers
+
+| Consumer | What it reads | Output |
+|----------|--------------|--------|
+| `policyGenerator.ts` | `policyData.jsonc` | ADMX/ADML (Windows GP), `.mobileconfig` (macOS), `policy.json` (Linux) |
+| `vscode-website` (`gulpfile.policies.js`) | `policyData.jsonc` | Enterprise policy reference table at code.visualstudio.com/docs/enterprise/policies |
+| `vscode-docs` | Generated from website build | `docs/enterprise/policies.md` |
 
 ## Examples
 
diff --git a/build/lib/policies/exportPolicyData.ts b/build/lib/policies/exportPolicyData.ts
new file mode 100644
index 0000000000000..eaaaeb60cb69d
--- /dev/null
+++ b/build/lib/policies/exportPolicyData.ts
@@ -0,0 +1,85 @@
+/*---------------------------------------------------------------------------------------------
+ *  Copyright (c) Microsoft Corporation. All rights reserved.
+ *  Licensed under the MIT License. See License.txt in the project root for license information.
+ *--------------------------------------------------------------------------------------------*/
+
+import { execSync, execFileSync } from 'child_process';
+import { resolve } from 'path';
+
+const rootPath = resolve(import.meta.dirname, '..', '..', '..');
+
+// VS Code OAuth app client ID (same as the GitHub Authentication extension)
+const CLIENT_ID = '01ab8ac9400c4e429b23';
+
+/**
+ * Acquires a GitHub token via the OAuth device flow.
+ * Opens the browser for the user to authorize, then polls for the token.
+ */
+async function acquireTokenViaDeviceFlow(): Promise<string> {
+	const response1 = await (await fetch('https://github.com/login/device/code', {
+		method: 'POST',
+		body: JSON.stringify({ client_id: CLIENT_ID, scope: 'repo' }),
+		headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
+	})).json() as { user_code: string; device_code: string; verification_uri: string; expires_in: number; interval: number };
+
+	console.log(`\n  Copy this code: ${response1.user_code}`);
+	console.log(`  Then open: ${response1.verification_uri}`);
+	console.log(`  Waiting for authorization (up to ${response1.expires_in}s)...\n`);
+
+	let expiresIn = response1.expires_in;
+	while (expiresIn > 0) {
+		await new Promise(resolve => setTimeout(resolve, 1000 * response1.interval));
+		expiresIn -= response1.interval;
+
+		const response2 = await (await fetch('https://github.com/login/oauth/access_token', {
+			method: 'POST',
+			body: JSON.stringify({
+				client_id: CLIENT_ID,
+				device_code: response1.device_code,
+				grant_type: 'urn:ietf:params:oauth:grant-type:device_code',
+			}),
+			headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
+		})).json() as { access_token?: string };
+
+		if (response2.access_token) {
+			return response2.access_token;
+		}
+	}
+
+	throw new Error('Timed out waiting for GitHub authorization');
+}
+
+// Ensure sources are transpiled
+console.log('Transpiling client sources...');
+execSync('npm run transpile-client', { cwd: rootPath, stdio: 'inherit' });
+
+// Set up GITHUB_TOKEN if not already set
+if (!process.env['GITHUB_TOKEN'] && !process.env['DISTRO_PRODUCT_JSON']) {
+	// Try gh CLI first (fast, non-interactive)
+	let token: string | undefined;
+	try {
+		token = execFileSync('gh', ['auth', 'token'], { encoding: 'utf8' }).trim();
+		console.log('Set GITHUB_TOKEN from gh CLI.');
+	} catch {
+		// Fall back to OAuth device flow (interactive)
+		console.log('gh CLI not available, starting GitHub OAuth device flow...');
+		token = await acquireTokenViaDeviceFlow();
+		console.log('GitHub authorization successful.');
+	}
+
+	process.env['GITHUB_TOKEN'] = token;
+}
+
+// Run the export
+console.log('Exporting policy data...');
+const codeScript = process.platform === 'win32'
+	? resolve(rootPath, 'scripts', 'code.bat')
+	: resolve(rootPath, 'scripts', 'code.sh');
+
+execSync(`"${codeScript}" --export-policy-data`, {
+	cwd: rootPath,
+	stdio: 'inherit',
+	env: process.env,
+});
+
+console.log('\nPolicy data exported to build/lib/policies/policyData.jsonc');
diff --git a/build/lib/policies/policyData.jsonc b/build/lib/policies/policyData.jsonc
index f58dda70afad4..23e21914f0547 100644
--- a/build/lib/policies/policyData.jsonc
+++ b/build/lib/policies/policyData.jsonc
@@ -1,4 +1,4 @@
-/** THIS FILE IS AUTOMATICALLY GENERATED USING `code --export-policy-data`. DO NOT MODIFY IT MANUALLY. **/
+/** THIS FILE IS AUTOMATICALLY GENERATED USING `npm run export-policy-data`. DO NOT MODIFY IT MANUALLY. **/
 {
     "categories": [
         {
@@ -314,6 +314,62 @@
             },
             "type": "boolean",
             "default": false
+        },
+        {
+            "key": "github.copilot.nextEditSuggestions.enabled",
+            "name": "CopilotNextEditSuggestions",
+            "category": "InteractiveSession",
+            "minimumVersion": "1.99",
+            "localization": {
+                "description": {
+                    "key": "github.copilot.nextEditSuggestions.enabled",
+                    "value": "Whether to enable next edit suggestions (NES). NES can propose a next edit based on your recent changes."
+                }
+            },
+            "type": "boolean",
+            "default": true
+        },
+        {
+            "key": "github.copilot.chat.reviewSelection.enabled",
+            "name": "CopilotReviewSelection",
+            "category": "InteractiveSession",
+            "minimumVersion": "1.104",
+            "localization": {
+                "description": {
+                    "key": "github.copilot.chat.reviewSelection.enabled",
+                    "value": "Enables code review on current selection."
+                }
+            },
+            "type": "boolean",
+            "default": true
+        },
+        {
+            "key": "github.copilot.chat.reviewAgent.enabled",
+            "name": "CopilotReviewAgent",
+            "category": "InteractiveSession",
+            "minimumVersion": "1.104",
+            "localization": {
+                "description": {
+                    "key": "github.copilot.chat.reviewAgent.enabled",
+                    "value": "Enables the code review agent."
+                }
+            },
+            "type": "boolean",
+            "default": true
+        },
+        {
+            "key": "github.copilot.chat.claudeAgent.enabled",
+            "name": "Claude3PIntegration",
+            "category": "InteractiveSession",
+            "minimumVersion": "1.113",
+            "localization": {
+                "description": {
+                    "key": "github.copilot.chat.claudeAgent.enabled",
+                    "value": "Enable Claude Agent sessions in VS Code. Start and resume agentic coding sessions powered by Anthropic Claude Agent SDK directly in the editor. Uses your existing Copilot subscription."
+                }
+            },
+            "type": "boolean",
+            "default": true
         }
     ]
 }
diff --git a/package.json b/package.json
index c530f4c90a12b..ac972ae2a2fcf 100644
--- a/package.json
+++ b/package.json
@@ -1,7 +1,7 @@
 {
   "name": "code-oss-dev",
   "version": "1.115.0",
-  "distro": "fdfcc35f4a498ffc0fae5966393153e96672dc89",
+  "distro": "084798d47e4cc4c713def402d4a1110fb619116d",
   "author": {
     "name": "Microsoft Corporation"
   },
@@ -55,6 +55,7 @@
     "valid-layers-check": "node build/checker/layersChecker.ts && tsgo --project build/checker/tsconfig.browser.json && tsgo --project build/checker/tsconfig.worker.json && tsgo --project build/checker/tsconfig.node.json && tsgo --project build/checker/tsconfig.electron-browser.json && tsgo --project build/checker/tsconfig.electron-main.json && tsgo --project build/checker/tsconfig.electron-utility.json",
     "define-class-fields-check": "node build/lib/propertyInitOrderChecker.ts && tsgo --project src/tsconfig.defineClassFields.json",
     "update-distro": "node build/npm/update-distro.ts",
+    "export-policy-data": "node build/lib/policies/exportPolicyData.ts",
     "web": "echo 'npm run web' is replaced by './scripts/code-server' or './scripts/code-web'",
     "compile-cli": "npm run gulp compile-cli",
     "compile-web": "npm run gulp compile-web",
diff --git a/src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts b/src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts
index 51a0f8b42e10f..e78e85ab2b410 100644
--- a/src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts
+++ b/src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts
@@ -8,6 +8,7 @@ import { Disposable } from '../../../../base/common/lifecycle.js';
 import { IWorkbenchConfigurationService } from '../../../services/configuration/common/configuration.js';
 import { IExtensionService } from '../../../services/extensions/common/extensions.js';
 import { INativeEnvironmentService } from '../../../../platform/environment/common/environment.js';
+import { process } from '../../../../base/parts/sandbox/electron-browser/globals.js';
 import { ILogService } from '../../../../platform/log/common/log.js';
 import { INativeHostService } from '../../../../platform/native/common/native.js';
 import { Registry } from '../../../../platform/registry/common/platform.js';
@@ -20,6 +21,13 @@ import { PolicyCategory, PolicyCategoryData } from '../../../../base/common/poli
 import { ExportedPolicyDataDto } from '../common/policyDto.js';
 import { join } from '../../../../base/common/path.js';
 
+interface ExtensionConfigurationPolicyEntry {
+	readonly name: string;
+	readonly category: string;
+	readonly minimumVersion: `${number}.${number}`;
+	readonly description: string;
+}
+
 export class PolicyExportContribution extends Disposable implements IWorkbenchContribution {
 	static readonly ID = 'workbench.contrib.policyExport';
 	static readonly DEFAULT_POLICY_EXPORT_PATH = 'build/lib/policies/policyData.jsonc';
@@ -96,7 +104,38 @@ export class PolicyExportContribution extends Disposable implements IWorkbenchCo
 				}
 				this.log(`Discovered ${policyData.policies.length} policies to export.`);
 
-				const disclaimerComment = `/** THIS FILE IS AUTOMATICALLY GENERATED USING \`code --export-policy-data\`. DO NOT MODIFY IT MANUALLY. **/`;
+				// Merge extension configuration policies from the distro's product.json.
+				// Checks DISTRO_PRODUCT_JSON env var (for testing),
+				// then falls back to fetching from GitHub API with GITHUB_TOKEN.
+				const distroProduct = await this.getDistroProductJson();
+				const extensionPolicies = distroProduct['extensionConfigurationPolicy'] as Record<string, ExtensionConfigurationPolicyEntry> | undefined;
+				if (extensionPolicies) {
+					const existingKeys = new Set(policyData.policies.map(p => p.key));
+					let added = 0;
+					for (const [key, entry] of Object.entries(extensionPolicies)) {
+						if (existingKeys.has(key)) {
+							continue;
+						}
+						if (!entry.description || !entry.category) {
+							throw new Error(`Extension policy '${key}' is missing required 'description' or 'category' field.`);
+						}
+						policyData.policies.push({
+							key,
+							name: entry.name,
+							category: entry.category,
+							minimumVersion: entry.minimumVersion,
+							localization: {
+								description: { key, value: entry.description },
+							},
+							type: 'boolean',
+							default: true,
+						});
+						added++;
+					}
+					this.log(`Merged ${added} extension configuration policies.`);
+				}
+
+				const disclaimerComment = `/** THIS FILE IS AUTOMATICALLY GENERATED USING \`npm run export-policy-data\`. DO NOT MODIFY IT MANUALLY. **/`;
 				const policyDataFileContent = `${disclaimerComment}\n${JSON.stringify(policyData, null, 4)}\n`;
 				await this.fileService.writeFile(URI.file(policyDataPath), VSBuffer.fromString(policyDataFileContent));
 				this.log(`Successfully exported ${policyData.policies.length} policies to ${policyDataPath}.`);
@@ -108,6 +147,66 @@ export class PolicyExportContribution extends Disposable implements IWorkbenchCo
 			await this.nativeHostService.exit(1);
 		}
 	}
+
+	/**
+	 * Reads the distro product.json for the 'stable' quality.
+	 * Checks DISTRO_PRODUCT_JSON env var (for testing),
+	 * then falls back to fetching from the GitHub API using GITHUB_TOKEN.
+	 */
+	private async getDistroProductJson(): Promise<Record<string, unknown>> {
+		const root = this.nativeEnvironmentService.appRoot;
+
+		// 1. DISTRO_PRODUCT_JSON env var (for testing)
+		const envPath = process.env['DISTRO_PRODUCT_JSON'];
+		if (envPath) {
+			this.log(`Reading distro product.json from DISTRO_PRODUCT_JSON=${envPath}`);
+			const content = (await this.fileService.readFile(URI.file(envPath))).value.toString();
+			return JSON.parse(content);
+		}
+
+		// 2. GitHub API with GITHUB_TOKEN
+		const packageJsonPath = join(root, 'package.json');
+		const packageJsonContent = (await this.fileService.readFile(URI.file(packageJsonPath))).value.toString();
+		const packageJson = JSON.parse(packageJsonContent);
+		const distroCommit: string | undefined = packageJson.distro;
+
+		if (!distroCommit) {
+			throw new Error(
+				'No distro commit found in package.json. ' +
+				'Use `npm run export-policy-data` which sets up the required environment.'
+			);
+		}
+
+		const token = process.env['GITHUB_TOKEN'];
+		if (!token) {
+			throw new Error(
+				'GITHUB_TOKEN is required to fetch distro product.json. ' +
+				'Use `npm run export-policy-data` which sets up the required environment.'
+			);
+		}
+
+		this.log(`Fetching distro product.json for commit ${distroCommit} from GitHub...`);
+		const url = `https://api.github.com/repos/microsoft/vscode-distro/contents/mixin/stable/product.json?ref=${encodeURIComponent(distroCommit)}`;
+		const response = await fetch(url, {
+			headers: {
+				'Accept': 'application/vnd.github+json',
+				'Authorization': `Bearer ${token}`,
+				'X-GitHub-Api-Version': '2022-11-28',
+				'User-Agent': 'VSCode Build'
+			}
+		});
+
+		if (!response.ok) {
+			throw new Error(`Failed to fetch distro product.json: ${response.status} ${response.statusText}`);
+		}
+
+		const data = await response.json() as { content: string; encoding: string };
+		if (data.encoding !== 'base64') {
+			throw new Error(`Unexpected encoding from GitHub API: ${data.encoding}`);
+		}
+		const content = VSBuffer.wrap(Uint8Array.from(atob(data.content), c => c.charCodeAt(0))).toString();
+		return JSON.parse(content);
+	}
 }
 
 registerWorkbenchContribution2(
diff --git a/src/vs/workbench/contrib/policyExport/test/node/extensionPolicyFixture.json b/src/vs/workbench/contrib/policyExport/test/node/extensionPolicyFixture.json
new file mode 100644
index 0000000000000..d11df1b559471
--- /dev/null
+++ b/src/vs/workbench/contrib/policyExport/test/node/extensionPolicyFixture.json
@@ -0,0 +1,28 @@
+{
+	"extensionConfigurationPolicy": {
+		"github.copilot.nextEditSuggestions.enabled": {
+			"name": "CopilotNextEditSuggestions",
+			"minimumVersion": "1.99",
+			"category": "InteractiveSession",
+			"description": "Whether to enable next edit suggestions (NES). NES can propose a next edit based on your recent changes."
+		},
+		"github.copilot.chat.reviewSelection.enabled": {
+			"name": "CopilotReviewSelection",
+			"minimumVersion": "1.104",
+			"category": "InteractiveSession",
+			"description": "Enables code review on current selection."
+		},
+		"github.copilot.chat.reviewAgent.enabled": {
+			"name": "CopilotReviewAgent",
+			"minimumVersion": "1.104",
+			"category": "InteractiveSession",
+			"description": "Enables the code review agent."
+		},
+		"github.copilot.chat.claudeAgent.enabled": {
+			"name": "Claude3PIntegration",
+			"minimumVersion": "1.113",
+			"category": "InteractiveSession",
+			"description": "Enable Claude Agent sessions in VS Code. Start and resume agentic coding sessions powered by Anthropic Claude Agent SDK directly in the editor. Uses your existing Copilot subscription."
+		}
+	}
+}
diff --git a/src/vs/workbench/contrib/policyExport/test/node/policyExport.integrationTest.ts b/src/vs/workbench/contrib/policyExport/test/node/policyExport.integrationTest.ts
index c9cc8881d246b..f11fa2393435a 100644
--- a/src/vs/workbench/contrib/policyExport/test/node/policyExport.integrationTest.ts
+++ b/src/vs/workbench/contrib/policyExport/test/node/policyExport.integrationTest.ts
@@ -47,10 +47,15 @@ suite('PolicyExport Integration Tests', () => {
 				? join(rootPath, 'scripts', 'code.bat')
 				: join(rootPath, 'scripts', 'code.sh');
 
-			// Skip prelaunch to avoid redownloading electron while the parent VS Code is using it
+			// Skip prelaunch to avoid redownloading electron while the parent VS Code is using it.
+			// DISTRO_PRODUCT_JSON points to a static test fixture so --export-policy-data can
+			// merge extension policies without needing distro access or GITHUB_TOKEN.
+			// This fixture is NOT expected to stay in sync with the distro — it exists purely
+			// to test the generation code path. Policy values will drift and that is fine.
+			const fixturePath = join(rootPath, 'src/vs/workbench/contrib/policyExport/test/node/extensionPolicyFixture.json');
 			await exec(`"${scriptPath}" --export-policy-data="${tempFile}"`, {
 				cwd: rootPath,
-				env: { ...process.env, VSCODE_SKIP_PRELAUNCH: '1' }
+				env: { ...process.env, VSCODE_SKIP_PRELAUNCH: '1', DISTRO_PRODUCT_JSON: fixturePath }
 			});
 
 			// Read both files
@@ -63,7 +68,7 @@ suite('PolicyExport Integration Tests', () => {
 			assert.strictEqual(
 				exportedContent,
 				checkedInContent,
-				'Exported policy data should match the checked-in file. If this fails, run: ./scripts/code.sh --export-policy-data'
+				'Exported policy data should match the checked-in file. If this fails, run: npm run export-policy-data'
 			);
 		} finally {
 			// Clean up temp file

PATCH

echo "Patch applied successfully."
