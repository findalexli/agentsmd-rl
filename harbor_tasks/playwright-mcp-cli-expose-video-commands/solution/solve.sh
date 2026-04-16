#!/bin/bash
set -e

cd /workspace/playwright

# Apply the gold patch for exposing video commands in MCP CLI
cat > /tmp/patch.diff << 'PATCH_EOF'
diff --git a/packages/playwright/src/mcp/browser/browserContextFactory.ts b/packages/playwright/src/mcp/browser/browserContextFactory.ts
index 04951363627e6..819a680e2d302 100644
--- a/packages/playwright/src/mcp/browser/browserContextFactory.ts
+++ b/packages/playwright/src/mcp/browser/browserContextFactory.ts
@@ -352,7 +352,7 @@ export class SharedContextFactory implements BrowserContextFactory {
 }

 async function computeTracesDir(config: FullConfig, clientInfo: ClientInfo): Promise<string | undefined> {
-  if (!config.saveTrace && !config.capabilities?.includes('tracing'))
+  if (!config.saveTrace && !config.capabilities?.includes('devtools'))
     return;
   return await outputFile(config, clientInfo, `traces`, { origin: 'code', title: 'Collecting trace' });
 }
diff --git a/packages/playwright/src/mcp/browser/tools.ts b/packages/playwright/src/mcp/browser/tools.ts
index 6432206fdc4ed..a70cd5af356d6 100644
--- a/packages/playwright/src/mcp/browser/tools.ts
+++ b/packages/playwright/src/mcp/browser/tools.ts
@@ -32,8 +32,9 @@ import screenshot from './tools/screenshot';
 import storage from './tools/storage';
 import tabs from './tools/tabs';
 import tracing from './tools/tracing';
-import wait from './tools/wait';
 import verify from './tools/verify';
+import video from './tools/video';
+import wait from './tools/wait';

 import type { Tool } from './tools/tool';
 import type { FullConfig } from './config';
@@ -57,8 +58,9 @@ export const browserTools: Tool<any>[] = [
   ...storage,
   ...tabs,
   ...tracing,
-  ...wait,
   ...verify,
+  ...video,
+  ...wait,
 ];

 export function filteredTools(config: FullConfig) {
diff --git a/packages/playwright/src/mcp/browser/tools/tracing.ts b/packages/playwright/src/mcp/browser/tools/tracing.ts
index 041f950c90125..6dc4accb35881 100644
--- a/packages/playwright/src/mcp/browser/tools/tracing.ts
+++ b/packages/playwright/src/mcp/browser/tools/tracing.ts
@@ -20,7 +20,7 @@ import { defineTool } from './tool';
 import type { Tracing } from '../../../../../playwright-core/src/client/tracing';

 const tracingStart = defineTool({
-  capability: 'tracing',
+  capability: 'devtools',

   schema: {
     name: 'browser_start_tracing',
@@ -50,7 +50,7 @@ const tracingStart = defineTool({
 });

 const tracingStop = defineTool({
-  capability: 'tracing',
+  capability: 'devtools',

   schema: {
     name: 'browser_stop_tracing',
diff --git a/packages/playwright/src/mcp/browser/tools/video.ts b/packages/playwright/src/mcp/browser/tools/video.ts
new file mode 100644
index 0000000000000..defa36cdef4b1
--- /dev/null
+++ b/packages/playwright/src/mcp/browser/tools/video.ts
@@ -0,0 +1,71 @@
+/**
+ * Copyright (c) Microsoft Corporation.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License");
+ * you may not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software
+ * distributed under the License is distributed on an "AS IS" BASIS,
+ * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+ * See the License for the specific language governing permissions and
+ * limitations under the License.
+ */
+
+import { z } from 'playwright-core/lib/mcpBundle';
+import { defineTabTool } from './tool';
+import { dateAsFileName } from './utils';
+
+const startVideo = defineTabTool({
+  capability: 'devtools',
+
+  schema: {
+    name: 'browser_start_video',
+    title: 'Start video',
+    description: 'Start video recording',
+    inputSchema: z.object({
+      size: z.object({
+        width: z.number().describe('Video width'),
+        height: z.number().describe('Video height'),
+      }).optional().describe('Video size'),
+    }),
+    type: 'readOnly',
+  },
+
+  handle: async (tab, params, response) => {
+    await tab.page.video().start({ size: params.size });
+    response.addTextResult('Video recording started.');
+  },
+});
+
+const stopVideo = defineTabTool({
+  capability: 'devtools',
+
+  schema: {
+    name: 'browser_stop_video',
+    title: 'Stop video',
+    description: 'Stop video recording',
+    inputSchema: z.object({
+      filename: z.string().optional().describe('Filename to save the video'),
+    }),
+    type: 'readOnly',
+  },
+
+  handle: async (tab, params, response) => {
+    const tmpPath = await tab.page.video().path();
+    let videoPath: string | undefined;
+    if (params.filename) {
+      const suggestedFilename = params.filename ?? dateAsFileName('video', 'webm');
+      videoPath = await tab.context.outputFile(suggestedFilename, { origin: 'llm', title: 'Saving video' });
+    }
+    await tab.page.video().stop({ path: videoPath });
+    response.addTextResult(`Video recording stopped: ${videoPath ?? tmpPath}`);
+  },
+});
+
+export default [
+  startVideo,
+  stopVideo,
+];
diff --git a/packages/playwright/src/mcp/config.d.ts b/packages/playwright/src/mcp/config.d.ts
index 62f3073ccff2d..ca6c49517ae94 100644
--- a/packages/playwright/src/mcp/config.d.ts
+++ b/packages/playwright/src/mcp/config.d.ts
@@ -25,8 +25,8 @@ export type ToolCapability =
   'pdf' |
   'storage' |
   'testing' |
-  'tracing' |
-  'vision';
+  'vision' |
+  'devtools';

 export type Config = {
   /**
@@ -119,6 +119,7 @@ export type Config = {
    *   - 'core': Core browser automation features.
    *   - 'pdf': PDF generation and manipulation.
    *   - 'vision': Coordinate-based interactions.
+   *   - 'devtools': Developer tools features.
    */
   capabilities?: ToolCapability[];

diff --git a/packages/playwright/src/mcp/program.ts b/packages/playwright/src/mcp/program.ts
index 0cea3d07fc216..c832d64ae7528 100644
--- a/packages/playwright/src/mcp/program.ts
+++ b/packages/playwright/src/mcp/program.ts
@@ -39,7 +39,7 @@ export function decorateCommand(command: Command, version: string) {
       .option('--blocked-origins <origins>', 'semicolon-separated list of origins to block the browser from requesting. Blocklist is evaluated before allowlist. If used without the allowlist, requests not matching the blocklist are still allowed.\nImportant: *does not* serve as a security boundary and *does not* affect redirects.', semicolonSeparatedList)
       .option('--block-service-workers', 'block service workers')
       .option('--browser <browser>', 'browser or chrome channel to use, possible values: chrome, firefox, webkit, msedge.')
-      .option('--caps <caps>', 'comma-separated list of additional capabilities to enable, possible values: vision, pdf.', commaSeparatedList)
+      .option('--caps <caps>', 'comma-separated list of additional capabilities to enable, possible values: vision, pdf, devtools.', commaSeparatedList)
       .option('--cdp-endpoint <endpoint>', 'CDP endpoint to connect to.')
       .option('--cdp-header <headers...>', 'CDP headers to send with the connect request, multiple can be specified.', headerParser)
       .option('--codegen <lang>', 'specify the language to use for code generation, possible values: "typescript", "none". Default is "typescript".', enumParser.bind(null, '--codegen', ['none', 'typescript']))
@@ -92,6 +92,9 @@ export function decorateCommand(command: Command, version: string) {
           options.caps = 'vision';
         }

+        if (options.caps?.includes('tracing'))
+          options.caps.push('devtools');
+
         const config = await resolveCLIConfig(options);

         // Chromium browsers require ffmpeg to be installed to save video.
diff --git a/packages/playwright/src/mcp/terminal/SKILL.md b/packages/playwright/src/mcp/terminal/SKILL.md
index 72db230f5bd71..0600464be3984 100644
--- a/packages/playwright/src/mcp/terminal/SKILL.md
+++ b/packages/playwright/src/mcp/terminal/SKILL.md
@@ -103,6 +103,8 @@ playwright-cli network
 playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
 playwright-cli tracing-start
 playwright-cli tracing-stop
+playwright-cli video-start
+playwright-cli video-stop video.webm
 ```

 ### Configuration
diff --git a/packages/playwright/src/mcp/terminal/command.ts b/packages/playwright/src/mcp/terminal/command.ts
index 5bba0ba6150e6..2800c97aaf1ac 100644
--- a/packages/playwright/src/mcp/terminal/command.ts
+++ b/packages/playwright/src/mcp/terminal/command.ts
@@ -14,6 +14,7 @@
  * limitations under the License.
  */

+import path from 'path';

 import type zodType from 'zod';

@@ -36,6 +37,9 @@ export function declareCommand<Args extends zodType.ZodTypeAny, Options extends
 }

 export function parseCommand(command: AnyCommandSchema, args: Record<string, string> & { _: string[] }): { toolName: string, toolParams: any } {
+  if (args.filename)
+    args.filename = path.resolve(args.outputDir, args.filename);
+
   const shape = command.args ? (command.args as zodType.ZodObject<any>).shape : {};
   const argv = args['_'];
   const options = command.options?.parse({ ...args, _: undefined }) ?? {};
diff --git a/packages/playwright/src/mcp/terminal/commands.ts b/packages/playwright/src/mcp/terminal/commands.ts
index e9ccb88bb12c2..fe74a66fb13d5 100644
--- a/packages/playwright/src/mcp/terminal/commands.ts
+++ b/packages/playwright/src/mcp/terminal/commands.ts
@@ -14,7 +14,6 @@
  * limitations under the License.
  */

-
 import { z } from 'playwright-core/lib/mcpBundle';
 import { declareCommand } from './command';

@@ -340,6 +339,17 @@ const resize = declareCommand({
   toolParams: ({ w: width, h: height }) => ({ width, height }),
 });

+const runCode = declareCommand({
+  name: 'run-code',
+  description: 'Run Playwright code snippet',
+  category: 'devtools',
+  args: z.object({
+    code: z.string().describe('A JavaScript function containing Playwright code to execute. It will be invoked with a single argument, page, which you can use for any page interaction.'),
+  }),
+  toolName: 'browser_run_code',
+  toolParams: ({ code }) => ({ code }),
+});
+
 // Tabs

 const tabList = declareCommand({
@@ -442,17 +452,6 @@ const networkRequests = declareCommand({
   toolParams: ({ static: includeStatic, clear }) => clear ? ({}) : ({ includeStatic }),
 });

-const runCode = declareCommand({
-  name: 'run-code',
-  description: 'Run Playwright code snippet',
-  category: 'devtools',
-  args: z.object({
-    code: z.string().describe('A JavaScript function containing Playwright code to execute. It will be invoked with a single argument, page, which you can use for any page interaction.'),
-  }),
-  toolName: 'browser_run_code',
-  toolParams: ({ code }) => ({ code }),
-});
-
 const tracingStart = declareCommand({
   name: 'tracing-start',
   description: 'Start trace recording',
@@ -471,6 +470,26 @@ const tracingStop = declareCommand({
   toolParams: () => ({}),
 });

+const videoStart = declareCommand({
+  name: 'video-start',
+  description: 'Start video recording',
+  category: 'devtools',
+  args: z.object({}),
+  toolName: 'browser_start_video',
+  toolParams: () => ({}),
+});
+
+const videoStop = declareCommand({
+  name: 'video-stop',
+  description: 'Stop video recording',
+  category: 'devtools',
+  options: z.object({
+    filename: z.string().optional().describe('Filename to save the video.'),
+  }),
+  toolName: 'browser_stop_video',
+  toolParams: ({ filename }) => ({ filename }),
+});
+
 // Sessions

 const sessionList = declareCommand({
@@ -543,6 +562,7 @@ const commandsArray: AnyCommandSchema[] = [
   dialogAccept,
   dialogDismiss,
   resize,
+  runCode,

   // navigation category
   goBack,
@@ -575,9 +595,10 @@ const commandsArray: AnyCommandSchema[] = [

   // devtools category
   networkRequests,
-  runCode,
   tracingStart,
   tracingStop,
+  videoStart,
+  videoStop,

   // session category
   sessionList,
diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index 7908b6411925c..5ecf624e6434e 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -112,7 +112,6 @@ class Session {
       console.log(`No user data found for session '${this.name}'.`);
       return;
     }
-    console.log(matchingDirs);
     for (const dir of matchingDirs) {
       const userDataDir = path.resolve(daemonProfilesDir, dir);
       for (let i = 0; i < 5; i++) {
@@ -202,6 +201,7 @@ class Session {
     const child = spawn(process.execPath, [
       cliPath,
       'run-mcp-server',
+      `--output-dir=${outputDir}`,
       `--daemon=${this._socketPath}`,
       `--daemon-data-dir=${userDataDir}`,
       ...configArg,
@@ -291,7 +291,7 @@ class Session {
       this.sessions.set(sessionName, session);
     }

-    const result = await session.run(args);
+    const result = await session.run({ ...args, outputDir });
     await printResponse(result);
     session.close();
   }
diff --git a/tests/mcp/cli.spec.ts b/tests/mcp/cli.spec.ts
index d7aef87187965..9a82dff38b388 100644
--- a/tests/mcp/cli.spec.ts
+++ b/tests/mcp/cli.spec.ts
@@ -15,6 +15,7 @@
  */

 import fs from 'fs';
+import path from 'path';
 import { test, expect, eventsPage } from './cli-fixtures';

 test.describe('help', () => {
@@ -203,6 +204,12 @@ test.describe('navigation', () => {
 - Page URL: ${server.HELLO_WORLD}
 - Page Title: Title`);
   });
+
+  test('run-code', async ({ cli, server }) => {
+    await cli('open', server.HELLO_WORLD);
+    const { output } = await cli('run-code', '() => page.title()');
+    expect(output).toContain('"Title"');
+  });
 });

 test.describe('keyboard', () => {
@@ -284,6 +291,14 @@ test.describe('save as', () => {
     expect(attachments[0].data).toEqual(expect.any(Buffer));
   });

+  test('screenshot --filename', async ({ cli, server, mcpBrowser }) => {
+    await cli('open', server.HELLO_WORLD);
+    const { output, attachments } = await cli('screenshot', '--filename=screenshot.png');
+    expect(output).toContain('.playwright-cli' + path.sep + 'screenshot.png');
+    expect(attachments[0].name).toEqual('Screenshot of viewport');
+    expect(attachments[0].data).toEqual(expect.any(Buffer));
+  });
+
   test('pdf', async ({ cli, server, mcpBrowser }) => {
     test.skip(mcpBrowser !== 'chromium' && mcpBrowser !== 'chrome', 'PDF is only supported in Chromium and Chrome');
     await cli('open', server.HELLO_WORLD);
@@ -291,6 +306,15 @@ test.describe('save as', () => {
     expect(attachments[0].name).toEqual('Page as pdf');
     expect(attachments[0].data).toEqual(expect.any(Buffer));
   });
+
+  test('pdf --filename', async ({ cli, server, mcpBrowser }) => {
+    test.skip(mcpBrowser !== 'chromium' && mcpBrowser !== 'chrome', 'PDF is only supported in Chromium and Chrome');
+    await cli('open', server.HELLO_WORLD);
+    const { output, attachments } = await cli('pdf', '--filename=pdf.pdf');
+    expect(output).toContain('.playwright-cli' + path.sep + 'pdf.pdf');
+    expect(attachments[0].name).toEqual('Page as pdf');
+    expect(attachments[0].data).toEqual(expect.any(Buffer));
+  });
 });

 test.describe('devtools', () => {
@@ -346,12 +370,6 @@ test.describe('devtools', () => {
     expect(attachments[0].data.toString()).not.toContain(`[GET] ${`${server.PREFIX}/hello-world`} => [200] OK`);
   });

-  test('run-code', async ({ cli, server }) => {
-    await cli('open', server.HELLO_WORLD);
-    const { output } = await cli('run-code', '() => page.title()');
-    expect(output).toContain('"Title"');
-  });
-
   test('tracing-start-stop', async ({ cli, server }) => {
     await cli('open', server.HELLO_WORLD);
     const { output } = await cli('tracing-start');
@@ -360,6 +378,16 @@ test.describe('devtools', () => {
     const { output: tracingStopOutput } = await cli('tracing-stop');
     expect(tracingStopOutput).toContain('Tracing stopped.');
   });
+
+  test('video-start-stop', async ({ cli, server }) => {
+    await cli('open', server.HELLO_WORLD);
+    const { output: videoStartOutput } = await cli('video-start');
+    expect(videoStartOutput).toContain('Video recording started.');
+    await cli('open', server.HELLO_WORLD);
+    const { output: videoStopOutput } = await cli('video-stop', '--filename=video.webm');
+    expect(videoStopOutput).toContain('Video recording stopped:');
+    expect(videoStopOutput).toContain('.playwright-cli' + path.sep + 'video.webm');
+  });
 });

 test.describe('config', () => {
PATCH_EOF

# Apply the patch
git apply /tmp/patch.diff

echo "Gold patch applied successfully"
