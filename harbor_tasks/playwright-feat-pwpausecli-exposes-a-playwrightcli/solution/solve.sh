#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'runDaemonForContext' packages/playwright/src/mcp/test/browserBackend.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full patch (code + config changes)
git apply --whitespace=fix - <<'PATCH'
diff --git a/.gitignore b/.gitignore
index 834eff0437594..f3dc324a766c4 100644
--- a/.gitignore
+++ b/.gitignore
@@ -30,6 +30,7 @@ test-results
 /packages/playwright/README.md
 /packages/playwright-test/README.md
 /packages/playwright-core/api.json
+/packages/playwright-cli
 .env
 /tests/installation/output/
 /tests/installation/.registry.json
diff --git a/packages/playwright-core/src/server/utils/network.ts b/packages/playwright-core/src/server/utils/network.ts
index 1aea7f6d7b986..5ac90e9f2b6ac 100644
--- a/packages/playwright-core/src/server/utils/network.ts
+++ b/packages/playwright-core/src/server/utils/network.ts
@@ -240,7 +240,7 @@ async function httpStatusCode(url: URL, ignoreHTTPSErrors: boolean, onLog?: (dat
   });
 }

-function decorateServer(server: net.Server) {
+export function decorateServer(server: net.Server) {
   const sockets = new Set<net.Socket>();
   server.on('connection', socket => {
     sockets.add(socket);
diff --git a/packages/playwright/src/cli/client/program.ts b/packages/playwright/src/cli/client/program.ts
index 5bde14a155dd2..2059f55a073b3 100644
--- a/packages/playwright/src/cli/client/program.ts
+++ b/packages/playwright/src/cli/client/program.ts
@@ -309,7 +309,7 @@ function defaultConfigFile(): string {
   return path.resolve('.playwright', 'cli.config.json');
 }

-function sessionConfigFromArgs(clientInfo: ClientInfo, sessionName: string, args: MinimistArgs): SessionConfig {
+export function sessionConfigFromArgs(clientInfo: ClientInfo, sessionName: string, args: MinimistArgs): SessionConfig {
   let config = args.config ? path.resolve(args.config) : undefined;
   try {
     if (!config && fs.existsSync(defaultConfigFile()))
diff --git a/packages/playwright/src/cli/daemon/daemon.ts b/packages/playwright/src/cli/daemon/daemon.ts
index bd19ada21c205..b981d1bad2a98 100644
--- a/packages/playwright/src/cli/daemon/daemon.ts
+++ b/packages/playwright/src/cli/daemon/daemon.ts
@@ -21,7 +21,7 @@ import path from 'path';
 import url from 'url';

 import { debug } from 'playwright-core/lib/utilsBundle';
-import { gracefullyProcessExitDoNotHang } from 'playwright-core/lib/utils';
+import { decorateServer, gracefullyProcessExitDoNotHang } from 'playwright-core/lib/utils';

 import { BrowserServerBackend } from '../../mcp/browser/browserServerBackend';
 import { SocketConnection } from '../client/socketConnection';
@@ -49,7 +49,8 @@ export async function startMcpDaemonServer(
   mcpConfig: FullConfig,
   sessionConfig: SessionConfig,
   contextFactory: BrowserContextFactory,
-): Promise<string> {
+  noShutdown?: boolean,
+): Promise<() => Promise<void>> {
   const { socketPath } = sessionConfig;
   // Clean up existing socket file on Unix
   if (os.platform() !== 'win32' && await socketExists(socketPath)) {
@@ -74,16 +75,18 @@ export async function startMcpDaemonServer(
   };

   const { browserContext, close } = await contextFactory.createContext(clientInfo, new AbortController().signal, {});
-  browserContext.on('close', () => {
-    daemonDebug('browser closed, shutting down daemon');
-    shutdown(0);
-  });
+  if (!noShutdown) {
+    browserContext.on('close', () => {
+      daemonDebug('browser closed, shutting down daemon');
+      shutdown(0);
+    });
+  }

   const existingContextFactory = {
     createContext: () => Promise.resolve({ browserContext, close }),
   };
   const backend = new BrowserServerBackend(mcpConfig, existingContextFactory, { allTools: true });
-  await backend.initialize?.(clientInfo);
+  await backend.initialize(clientInfo);

   await fs.mkdir(path.dirname(socketPath), { recursive: true });

@@ -121,10 +124,11 @@ export async function startMcpDaemonServer(
       } catch (e) {
         daemonDebug('command failed', e);
         const error = process.env.PWDEBUGIMPL ? (e as Error).stack || (e as Error).message : (e as Error).message;
-        await connection.send({ id, error });
+        connection.send({ id, error }).catch(() => {});
       }
     };
   });
+  decorateServer(server);

   return new Promise((resolve, reject) => {
     server.on('error', (error: NodeJS.ErrnoException) => {
@@ -134,7 +138,10 @@ export async function startMcpDaemonServer(

     server.listen(socketPath, () => {
       daemonDebug(`daemon server listening on ${socketPath}`);
-      resolve(socketPath);
+      resolve(async () => {
+        backend.serverClosed();
+        await new Promise(cb => server.close(cb));
+      });
     });
   });
 }
diff --git a/packages/playwright/src/cli/daemon/program.ts b/packages/playwright/src/cli/daemon/program.ts
index 091130f548a42..1d411cbff3e5b 100644
--- a/packages/playwright/src/cli/daemon/program.ts
+++ b/packages/playwright/src/cli/daemon/program.ts
@@ -44,12 +44,12 @@ export function decorateCLICommand(command: Command, version: string) {

         const cf = mcpConfig.extension ? extensionContextFactory : browserContextFactory;
         try {
-          const socketPath = await startMcpDaemonServer(mcpConfig, sessionConfig, cf);
+          await startMcpDaemonServer(mcpConfig, sessionConfig, cf);
           console.log(`### Config`);
           console.log('```json');
           console.log(JSON.stringify(mcpConfig, null, 2));
           console.log('```');
-          console.log(`### Success\nDaemon listening on ${socketPath}`);
+          console.log(`### Success\nDaemon listening on ${sessionConfig.socketPath}`);
           console.log('<EOF>');
         } catch (error) {
           const message = process.env.PWDEBUGIMPL ? (error as Error).stack || (error as Error).message : (error as Error).message;
diff --git a/packages/playwright/src/index.ts b/packages/playwright/src/index.ts
index b615f95345968..6b9bc44596d58 100644
--- a/packages/playwright/src/index.ts
+++ b/packages/playwright/src/index.ts
@@ -22,7 +22,7 @@ import { setBoxedStackPrefixes, createGuid, currentZone, debugMode, jsonStringif

 import { currentTestInfo } from './common/globals';
 import { rootTestType } from './common/testType';
-import { createCustomMessageHandler } from './mcp/test/browserBackend';
+import { createCustomMessageHandler, runDaemonForContext } from './mcp/test/browserBackend';

 import type { Fixtures, PlaywrightTestArgs, PlaywrightTestOptions, PlaywrightWorkerArgs, PlaywrightWorkerOptions, ScreenshotMode, TestInfo, TestType, VideoMode } from '../types/test';
 import type { ContextReuseMode } from './common/config';
@@ -426,19 +426,22 @@ const playwrightFixtures: Fixtures<TestFixtures, WorkerFixtures> = ({
     await use(reuse);
   }, { scope: 'worker',  title: 'context', box: true }],

-  context: async ({ browser, _reuseContext, _contextFactory }, use, testInfo) => {
+  context: async ({ browser, _reuseContext, _contextFactory }, use, testInfoPublic) => {
     const browserImpl = browser as BrowserImpl;
+    const testInfo = testInfoPublic as TestInfoImpl;
     attachConnectedHeaderIfNeeded(testInfo, browserImpl);
     if (!_reuseContext) {
       const { context, close } = await _contextFactory();
-      (testInfo as TestInfoImpl)._onCustomMessageCallback = createCustomMessageHandler(testInfo, context);
+      testInfo._onCustomMessageCallback = createCustomMessageHandler(testInfo, context);
+      testInfo._onDidFinishTestFunctionCallbacks.add(() => runDaemonForContext(testInfo, context));
       await use(context);
       await close();
       return;
     }

     const context = await browserImpl._wrapApiCall(() => browserImpl._newContextForReuse(), { internal: true });
-    (testInfo as TestInfoImpl)._onCustomMessageCallback = createCustomMessageHandler(testInfo, context);
+    testInfo._onCustomMessageCallback = createCustomMessageHandler(testInfo, context);
+    testInfo._onDidFinishTestFunctionCallbacks.add(() => runDaemonForContext(testInfo, context));
     await use(context);
     const closeReason = testInfo.status === 'timedOut' ? 'Test timeout of ' + testInfo.timeout + 'ms exceeded.' : 'Test ended.';
     await browserImpl._wrapApiCall(() => browserImpl._disconnectFromReusedContext(closeReason), { internal: true });
@@ -702,7 +705,7 @@ class ArtifactsRecorder {

   async willStartTest(testInfo: TestInfoImpl) {
     this._testInfo = testInfo;
-    testInfo._onDidFinishTestFunctionCallback = () => this.didFinishTestFunction();
+    testInfo._onDidFinishTestFunctionCallbacks.add(() => this.didFinishTestFunction());

     this._screenshotRecorder.fixOrdinal();

diff --git a/packages/playwright/src/mcp/test/DEPS.list b/packages/playwright/src/mcp/test/DEPS.list
index 4d49a78fb2bcd..6dd1e602df478 100644
--- a/packages/playwright/src/mcp/test/DEPS.list
+++ b/packages/playwright/src/mcp/test/DEPS.list
@@ -17,3 +17,6 @@

 [backend.ts]
 ../browser/tools.ts
+
+[browserBackend.ts]
+../../cli/**
diff --git a/packages/playwright/src/mcp/test/browserBackend.ts b/packages/playwright/src/mcp/test/browserBackend.ts
index 7bed39f6bbfa2..ff4e12bd8e149 100644
--- a/packages/playwright/src/mcp/test/browserBackend.ts
+++ b/packages/playwright/src/mcp/test/browserBackend.ts
@@ -14,16 +14,23 @@
  * limitations under the License.
  */

+import path from 'path';
+import fs from 'fs';
+import { createGuid } from 'playwright-core/lib/utils';
+
 import * as mcp from '../sdk/exports';
 import { defaultConfig } from '../browser/config';
 import { BrowserServerBackend } from '../browser/browserServerBackend';
 import { Tab } from '../browser/tab';
 import { stripAnsiEscapes } from '../../util';
 import { identityBrowserContextFactory } from '../browser/browserContextFactory';
+import { startMcpDaemonServer } from '../../cli/daemon/daemon';
+import { sessionConfigFromArgs } from '../../cli/client/program';
+import { createClientInfo } from '../../cli/client/registry';

 import type * as playwright from '../../../index';
 import type { Page } from '../../../../playwright-core/src/client/page';
-import type { TestInfo } from '../../../test';
+import type { TestInfoImpl } from '../../worker/testInfo';

 export type BrowserMCPRequest = {
   initialize?: { clientInfo: mcp.ClientInfo },
@@ -39,7 +46,7 @@ export type BrowserMCPResponse = {
   close?: {},
 };

-export function createCustomMessageHandler(testInfo: TestInfo, context: playwright.BrowserContext) {
+export function createCustomMessageHandler(testInfo: TestInfoImpl, context: playwright.BrowserContext) {
   let backend: BrowserServerBackend | undefined;
   return async (data: BrowserMCPRequest): Promise<BrowserMCPResponse> => {
     if (data.initialize) {
@@ -73,7 +80,7 @@ export function createCustomMessageHandler(testInfo: TestInfo, context: playwrig
   };
 }

-async function generatePausedMessage(testInfo: TestInfo, context: playwright.BrowserContext) {
+async function generatePausedMessage(testInfo: TestInfoImpl, context: playwright.BrowserContext) {
   const lines: string[] = [];

   if (testInfo.errors.length) {
@@ -115,3 +122,41 @@ async function generatePausedMessage(testInfo: TestInfo, context: playwright.Bro

   return lines.join('\n');
 }
+
+export async function runDaemonForContext(testInfo: TestInfoImpl, context: playwright.BrowserContext): Promise<void> {
+  if (process.env.PWPAUSE !== 'cli')
+    return;
+
+  const outputDir = path.join(testInfo.artifactsDir(), '.playwright-mcp');
+  const sessionName = `test-worker-${createGuid().slice(0, 6)}`;
+  const clientInfo = createClientInfo();
+  const sessionConfig = sessionConfigFromArgs(clientInfo, sessionName, { _: [] });
+  const sessionConfigFile = path.resolve(clientInfo.daemonProfilesDir, `${sessionName}.session`);
+  await fs.promises.mkdir(path.dirname(sessionConfigFile), { recursive: true });
+  await fs.promises.writeFile(sessionConfigFile, JSON.stringify(sessionConfig, null, 2));
+  await startMcpDaemonServer({
+    ...defaultConfig,
+    outputMode: 'file',
+    snapshot: { mode: 'full', output: 'file' },
+    outputDir,
+  }, sessionConfig, identityBrowserContextFactory(context), true /* noShutdown */);
+
+  const lines = [''];
+  if (testInfo.errors.length) {
+    lines.push(`### Paused on test error`);
+    for (const error of testInfo.errors)
+      lines.push(stripAnsiEscapes(error.message || ''));
+  } else {
+    lines.push(`### Paused at the end of the test`);
+  }
+  lines.push(
+      `### Debugging Instructions`,
+      `- Use "playwright-cli --session=${sessionName}" to explore the page and fix the problem.`,
+      `- Stop this test run when finished. Restart if needed.`,
+      ``,
+  );
+
+  /* eslint-disable-next-line no-console */
+  console.log(lines.join('\n'));
+  await new Promise(() => {});
+}
diff --git a/packages/playwright/src/program.ts b/packages/playwright/src/program.ts
index 5059c633d5d19..6d9184c4f5405 100644
--- a/packages/playwright/src/program.ts
+++ b/packages/playwright/src/program.ts
@@ -315,7 +315,6 @@ function overridesFromOptions(options: { [key: string]: any }): ConfigCLIOverrid
     updateSourceMethod: options.updateSourceMethod,
     runAgents: options.runAgents,
     workers: options.workers,
-    pause: process.env.PWPAUSE ? true : undefined,
   };

   if (options.browser) {
@@ -331,7 +330,7 @@ function overridesFromOptions(options: { [key: string]: any }): ConfigCLIOverrid
     });
   }

-  if (options.headed || options.debug || overrides.pause)
+  if (options.headed || options.debug)
     overrides.use = { headless: false };
   if (!options.ui && options.debug) {
     overrides.debug = true;
@@ -341,6 +340,13 @@ function overridesFromOptions(options: { [key: string]: any }): ConfigCLIOverrid
     overrides.use = overrides.use || {};
     overrides.use.trace = options.trace;
   }
+  if (process.env.PWPAUSE === 'cli') {
+    overrides.timeout = 0;
+    overrides.use = overrides.use || {};
+    overrides.use.actionTimeout = 5000;
+  } else if (process.env.PWPAUSE) {
+    overrides.pause = true;
+  }
   if (overrides.tsconfig && !fs.existsSync(overrides.tsconfig))
     throw new Error(`--tsconfig "${options.tsconfig}" does not exist`);

diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index 99f5884333c22..c692f5f0c0681 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: playwright-cli
-description: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, test web applications, or extract information from web pages.
-allowed-tools: Bash(playwright-cli:*)
+description: Automate browser interactions, test web pages and work with Playwright tests.
+allowed-tools: Bash(playwright-cli:*) Bash(npx:*) Bash(npm:*)
 ---

 # Browser Automation with playwright-cli
@@ -274,6 +274,7 @@ playwright-cli close

 ## Specific tasks

+* **Running and Debugging Playwright tests** [references/playwright-tests.md](references/playwright-tests.md)
 * **Request mocking** [references/request-mocking.md](references/request-mocking.md)
 * **Running Playwright code** [references/running-code.md](references/running-code.md)
 * **Browser session management** [references/session-management.md](references/session-management.md)
diff --git a/packages/playwright/src/skill/references/playwright-tests.md b/packages/playwright/src/skill/references/playwright-tests.md
new file mode 100644
index 0000000000000..81d131b72205c
--- /dev/null
+++ b/packages/playwright/src/skill/references/playwright-tests.md
@@ -0,0 +1,34 @@
+# Running Playwright Tests
+
+To run Playwright tests, use the `npx playwright test` command, or a package manager script. To avoid opening the interactive html report, use `PLAYWRIGHT_HTML_OPEN=never` environment variable.
+
+```bash
+# Run all tests
+PLAYWRIGHT_HTML_OPEN=never npx playwright test
+
+# Run all tests through a custom npm script
+PLAYWRIGHT_HTML_OPEN=never npm run special-test-command
+```
+
+# Debugging Playwright Tests
+
+To debug a failing test, run it with Playwright as usual, but set `PWPAUSE=cli` environment variable. This command will pause the test at the point of failure, and print the debugging instructions.
+
+**IMPORTANT**: run the command in the background and check the output until "Debugging Instructions" is printed.
+
+Once instructions are printed, use `playwright-cli` to explore the page. Debugging instructions include a session name that should be used in `playwright-cli` to connect to the page under test. Do not create a new `playwright-cli` session, make sure to connect to the test session instead.
+
+```bash
+# Run the test
+PLAYWRIGHT_HTML_OPEN=never PWPAUSE=cli npx playwright test
+# ...
+
+# Explore the page and interact if needed
+playwright-cli --session=test-worker-abcdef snapshot
+playwright-cli --session=test-worker-abcdef click e14
+```
+
+Keep the test running in the background while you explore and look for a fix. After fixing the test, stop the background test run.
+
+Every action you perform with `playwright-cli` generates corresponding Playwright TypeScript code.
+This code appears in the output and can be copied directly into the test. Most of the time, a specific locator or an expectation should be updated, but it could also be a bug in the app. Use your judgement.
diff --git a/packages/playwright/src/worker/testInfo.ts b/packages/playwright/src/worker/testInfo.ts
index db8a4d6e2ec5e..30e044bded66b 100644
--- a/packages/playwright/src/worker/testInfo.ts
+++ b/packages/playwright/src/worker/testInfo.ts
@@ -100,7 +100,7 @@ export class TestInfoImpl implements TestInfo {
   readonly _configInternal: FullConfigInternal;
   private readonly _steps: TestStepInternal[] = [];
   private readonly _stepMap = new Map<string, TestStepInternal>();
-  _onDidFinishTestFunctionCallback?: () => Promise<void>;
+  _onDidFinishTestFunctionCallbacks = new Set<() => Promise<void>>();
   _onCustomMessageCallback?: (data: any) => Promise<any>;
   _hasNonRetriableError = false;
   _hasUnhandledError = false;
@@ -478,7 +478,8 @@ export class TestInfoImpl implements TestInfo {
         this._interruptedPromise,
       ]);
     }
-    await this._onDidFinishTestFunctionCallback?.();
+    for (const cb of this._onDidFinishTestFunctionCallbacks)
+      await cb();
   }

   // ------------ TestInfo methods ------------

PATCH

echo "Patch applied successfully."
