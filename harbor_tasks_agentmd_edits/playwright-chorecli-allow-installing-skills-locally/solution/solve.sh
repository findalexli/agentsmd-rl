#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'install-skills' packages/playwright/src/mcp/terminal/commands.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.claude/skills/playwright-mcp-dev/SKILL.md b/.claude/skills/playwright-mcp-dev/SKILL.md
index c6fb82a5684bd..9b706310d6aa5 100644
--- a/.claude/skills/playwright-mcp-dev/SKILL.md
+++ b/.claude/skills/playwright-mcp-dev/SKILL.md
@@ -39,3 +39,8 @@ description: Explains how to add and debug playwright MCP tools and CLI commands

 # Lint
 - run `npm run flint` to lint everything before commit
+
+# SKILL File
+
+The skill file is located at `packages/playwright/src/skill/SKILL.md`. It contains documentation for all available CLI commands and MCP tools. Update it whenever you add new commands or tools.
+At any point in time you can run "npm run playwright-cli -- --help" to see the latest available commands and use them to update the skill file.
diff --git a/packages/playwright/src/mcp/browser/tools/route.ts b/packages/playwright/src/mcp/browser/tools/route.ts
index d4f6b736af93b..6c7d7763db41e 100644
--- a/packages/playwright/src/mcp/browser/tools/route.ts
+++ b/packages/playwright/src/mcp/browser/tools/route.ts
@@ -21,7 +21,7 @@ import type * as playwright from 'playwright-core';
 import type { RouteEntry } from '../context';

 const route = defineTool({
-  capability: 'core',
+  capability: 'network',

   schema: {
     name: 'browser_route',
@@ -86,7 +86,7 @@ const route = defineTool({
 });

 const routeList = defineTool({
-  capability: 'core',
+  capability: 'network',

   schema: {
     name: 'browser_route_list',
@@ -126,7 +126,7 @@ const routeList = defineTool({
 });

 const unroute = defineTool({
-  capability: 'core',
+  capability: 'network',

   schema: {
     name: 'browser_unroute',
diff --git a/packages/playwright/src/mcp/config.d.ts b/packages/playwright/src/mcp/config.d.ts
index 59d1265f8edfc..002766ddbbbcf 100644
--- a/packages/playwright/src/mcp/config.d.ts
+++ b/packages/playwright/src/mcp/config.d.ts
@@ -22,6 +22,7 @@ export type ToolCapability =
   'core-tabs' |
   'core-input' |
   'core-install' |
+  'network' |
   'pdf' |
   'storage' |
   'testing' |
diff --git a/packages/playwright/src/mcp/terminal/commands.ts b/packages/playwright/src/mcp/terminal/commands.ts
index 58beec5493650..5da23e79596b0 100644
--- a/packages/playwright/src/mcp/terminal/commands.ts
+++ b/packages/playwright/src/mcp/terminal/commands.ts
@@ -799,7 +799,7 @@ const config = declareCommand({
 });

 const install = declareCommand({
-  name: 'install',
+  name: 'install-browser',
   description: 'Install browser',
   category: 'install',
   options: z.object({
@@ -809,6 +809,15 @@ const install = declareCommand({
   toolParams: () => ({}),
 });

+const installSkills = declareCommand({
+  name: 'install-skills',
+  description: 'Install Claude / GitGub Copilot skills to the local workspace',
+  category: 'install',
+  args: z.object({}),
+  toolName: '',
+  toolParams: () => ({}),
+});
+
 const commandsArray: AnyCommandSchema[] = [
   // core category
   open,
@@ -886,6 +895,7 @@ const commandsArray: AnyCommandSchema[] = [

   // install category
   install,
+  installSkills,

   // devtools category
   networkRequests,
diff --git a/packages/playwright/src/mcp/terminal/helpGenerator.ts b/packages/playwright/src/mcp/terminal/helpGenerator.ts
index bad843297ab6c..e70dc89350c79 100644
--- a/packages/playwright/src/mcp/terminal/helpGenerator.ts
+++ b/packages/playwright/src/mcp/terminal/helpGenerator.ts
@@ -103,7 +103,7 @@ export function generateHelp() {
   lines.push(formatWithGap('  --extension', 'connect to a running browser instance using Playwright MCP Bridge extension'));
   lines.push(formatWithGap('  --headed', 'create a headed session'));
   lines.push(formatWithGap('  --help [command]', 'print help'));
-  lines.push(formatWithGap('  --isolated', 'keep the browser profile in memory, do not save it to disk'));
+  lines.push(formatWithGap('  --in-memory', 'keep the browser profile in memory, do not save it to disk'));
   lines.push(formatWithGap('  --session', 'run command in the scope of a specific session'));
   lines.push(formatWithGap('  --version', 'print version'));

diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index 9457734be7810..082188390dc42 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -507,9 +507,27 @@ export async function program(options: { version: string }) {
     return;
   }

+  if (commandName === 'install-skills') {
+    await installSkills();
+    return;
+  }
+
   await sessionManager.run(args);
 }

+async function installSkills() {
+  const skillSourceDir = path.join(__dirname, '../../skill');
+  const skillDestDir = path.join(process.cwd(), '.claude', 'skills', 'playwright');
+
+  if (!fs.existsSync(skillSourceDir)) {
+    console.error('Skills source directory not found:', skillSourceDir);
+    process.exit(1);
+  }
+
+  await fs.promises.cp(skillSourceDir, skillDestDir, { recursive: true });
+  console.log(`Skills installed to ${path.relative(process.cwd(), skillDestDir)}`);
+}
+
 const outputDir = path.join(process.cwd(), '.playwright-cli');

 function daemonSocketPath(sessionName: string): string {
diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index 6d94d12372626..de63c48ddae1a 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -125,6 +125,16 @@ playwright-cli sessionstorage-delete step
 playwright-cli sessionstorage-clear
 ```

+### Network
+
+```bash
+playwright-cli route "**/*.jpg" --status=404
+playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
+playwright-cli route-list
+playwright-cli unroute "**/*.jpg"
+playwright-cli unroute
+```
+
 ### DevTools

 ```bash
@@ -138,8 +148,23 @@ playwright-cli video-start
 playwright-cli video-stop video.webm
 ```

+### Install
+
+```bash
+playwright-cli install-browser
+playwright-cli install-skills
+```
+
 ### Configuration
 ```bash
+# Use specific browser when creating session
+playwright-cli open --browser=chrome
+playwright-cli open --browser=firefox
+playwright-cli open --browser=webkit
+playwright-cli open --browser=msedge
+# Connect to browser via extension
+playwright-cli open --extension
+
 # Configure the session
 playwright-cli config --config my-config.json
 playwright-cli config --headed --in-memory --browser=firefox
@@ -156,6 +181,7 @@ playwright-cli --session=mysession open example.com
 playwright-cli --session=mysession click e6
 playwright-cli session-list
 playwright-cli session-stop mysession
+playwright-cli session-restart mysession
 playwright-cli session-stop-all
 playwright-cli session-delete
 playwright-cli session-delete mysession
@@ -201,22 +227,6 @@ playwright-cli fill e7 "test"
 playwright-cli tracing-stop
 ```

-## Example: Authentication state reuse
-
-```bash
-# Login and save auth state
-playwright-cli open https://app.example.com/login
-playwright-cli snapshot
-playwright-cli fill e1 "user@example.com"
-playwright-cli fill e2 "password123"
-playwright-cli click e3
-playwright-cli state-save auth.json
-
-# Later, restore state and skip login
-playwright-cli state-load auth.json
-playwright-cli open https://app.example.com/dashboard
-```
-
 ## Specific tasks

 * **Request mocking** [references/request-mocking.md](references/request-mocking.md)
diff --git a/tests/mcp/cli-misc.spec.ts b/tests/mcp/cli-misc.spec.ts
index d0d9988bc2e5d..36fbd0d354ded 100644
--- a/tests/mcp/cli-misc.spec.ts
+++ b/tests/mcp/cli-misc.spec.ts
@@ -14,6 +14,8 @@
  * limitations under the License.
  */

+import fs from 'fs';
+import path from 'path';
 import { test, expect } from './cli-fixtures';

 test('daemon shuts down on browser launch failure', async ({ cli, server }) => {
@@ -41,6 +43,18 @@ test('old client', async ({ cli }) => {
 test('install', async ({ cli, server, mcpBrowser }) => {
   test.skip(mcpBrowser !== 'chromium', 'Test only chromium');
   await cli('open', server.HELLO_WORLD);
-  const { output } = await cli('install');
+  const { output } = await cli('install-browser');
   expect(output).toContain(`Browser ${mcpBrowser} installed.`);
 });
+
+test('install-skills', async ({ cli }, testInfo) => {
+  const { output } = await cli('install-skills');
+  expect(output).toContain(`Skills installed to .claude${path.sep}skills${path.sep}playwright`);
+
+  const skillFile = testInfo.outputPath('.claude', 'skills', 'playwright', 'SKILL.md');
+  expect(fs.existsSync(skillFile)).toBe(true);
+
+  const referencesDir = testInfo.outputPath('.claude', 'skills', 'playwright', 'references');
+  const references = await fs.promises.readdir(referencesDir);
+  expect(references.length).toBeGreaterThan(0);
+});
diff --git a/tests/mcp/fixtures.ts b/tests/mcp/fixtures.ts
index ee2043a691424..76d47746e28e3 100644
--- a/tests/mcp/fixtures.ts
+++ b/tests/mcp/fixtures.ts
@@ -40,6 +40,7 @@ export { parseResponse };
 export type TestOptions = {
   mcpArgs: string[] | undefined;
   mcpBrowser: string | undefined;
+  mcpCaps: string[] | undefined;
   mcpServerType: 'mcp' | 'test-mcp';
 };

@@ -82,13 +83,14 @@ export const serverTest = baseTest

 export const test = serverTest.extend<TestFixtures & TestOptions, WorkerFixtures>({
   mcpArgs: [undefined, { option: true }],
+  mcpCaps: [undefined, { option: true }],

   client: async ({ startClient }, use) => {
     const { client } = await startClient();
     await use(client);
   },

-  startClient: async ({ mcpHeadless, mcpBrowser, mcpArgs, mcpServerType }, use, testInfo) => {
+  startClient: async ({ mcpHeadless, mcpBrowser, mcpArgs, mcpServerType, mcpCaps }, use, testInfo) => {
     const configDir = path.dirname(test.info().config.configFile!);
     const clients: Client[] = [];

@@ -97,6 +99,8 @@ export const test = serverTest.extend<TestFixtures & TestOptions, WorkerFixtures

       if (mcpHeadless)
         args.push('--headless');
+      if (mcpCaps?.length)
+        args.push(`--caps=${mcpCaps.join(',')}`);

       if (mcpServerType === 'test-mcp') {
         if (!options?.args?.some(arg => arg.startsWith('--config')))

PATCH

echo "Patch applied successfully."
