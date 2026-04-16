#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied (check for CLAUDE.md change)
if grep -q "Never add Co-Authored-By agents in commit message" CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch - includes BOTH code changes AND CLAUDE.md update
git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index d168ae9d1b9fc..858166243e0f6 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -122,6 +122,7 @@ EOF
 )"
 ```

+Never add Co-Authored-By agents in commit message.
 Branch naming for issue fixes: `fix-<issue-number>`

 ## Development Guides
diff --git a/packages/playwright-core/src/mcp/config.d.ts b/packages/playwright-core/src/mcp/config.d.ts
index 35c5ca61fb225..99ad58fbf9523 100644
--- a/packages/playwright-core/src/mcp/config.d.ts
+++ b/packages/playwright-core/src/mcp/config.d.ts
@@ -137,11 +137,6 @@ export type Config = {
    */
   saveSession?: boolean;

-  /**
-   * Reuse the same browser context between all connected HTTP clients.
-   */
-  sharedBrowserContext?: boolean;
-
   /**
    * Secrets are used to prevent LLM from getting sensitive data while
    * automating scenarios such as authentication.
diff --git a/packages/playwright-core/src/mcp/config.ts b/packages/playwright-core/src/mcp/config.ts
index 577da213a873e..1088e834a6c14 100644
--- a/packages/playwright-core/src/mcp/config.ts
+++ b/packages/playwright-core/src/mcp/config.ts
@@ -64,7 +64,6 @@ export type CLIOptions = {
   proxyServer?: string;
   saveSession?: boolean;
   secrets?: Record<string, string>;
-  sharedBrowserContext?: boolean;
   snapshotMode?: 'incremental' | 'full' | 'none';
   storageState?: string;
   testIdAttribute?: string;
@@ -253,7 +252,6 @@ export function configFromCLIOptions(cliOptions: CLIOptions): Config & { configF
     codegen: cliOptions.codegen,
     saveSession: cliOptions.saveSession,
     secrets: cliOptions.secrets,
-    sharedBrowserContext: cliOptions.sharedBrowserContext,
     snapshot: cliOptions.snapshotMode ? { mode: cliOptions.snapshotMode } : undefined,
     outputMode: cliOptions.outputMode,
     outputDir: cliOptions.outputDir,
diff --git a/packages/playwright-core/src/mcp/configIni.ts b/packages/playwright-core/src/mcp/configIni.ts
index 966e4ab617c9b..29c4c743e7955 100644
--- a/packages/playwright-core/src/mcp/configIni.ts
+++ b/packages/playwright-core/src/mcp/configIni.ts
@@ -160,7 +160,6 @@ const longhandTypes: Record<string, LonghandType> = {
   'saveSession': 'boolean',
   'saveTrace': 'boolean',
   'saveVideo': 'size',
-  'sharedBrowserContext': 'boolean',
   'outputDir': 'string',
   'outputMode': 'string',
   'imageResponses': 'string',
diff --git a/packages/playwright-core/src/mcp/program.ts b/packages/playwright-core/src/mcp/program.ts
index c60b789c088c5..f82bf80b47755 100644
--- a/packages/playwright-core/src/mcp/program.ts
+++ b/packages/playwright-core/src/mcp/program.ts
@@ -26,6 +26,7 @@ import { testDebug } from './log';

 import type { Command } from '../utilsBundle';
 import type { ClientInfo } from './sdk/server';
+import type * as playwright from '../..';

 export function decorateMCPCommand(command: Command, version: string) {
   command
@@ -62,7 +63,6 @@ export function decorateMCPCommand(command: Command, version: string) {
       .option('--sandbox', 'enable the sandbox for all process types that are normally not sandboxed.')
       .option('--save-session', 'Whether to save the Playwright MCP session into the output directory.')
       .option('--secrets <path>', 'path to a file containing secrets in the dotenv format', dotenvFileLoader)
-      .option('--shared-browser-context', 'reuse the same browser context between all connected HTTP clients.')
       .option('--snapshot-mode <mode>', 'when taking snapshots for responses, specifies the mode to use. Can be "incremental", "full", or "none". Default is incremental.')
       .option('--storage-state <path>', 'path to the storage state file for isolated sessions.')
       .option('--test-id-attribute <attribute>', 'specify the attribute to use for test ids, defaults to "data-testid"')
@@ -107,14 +107,18 @@ export function decorateMCPCommand(command: Command, version: string) {
           return;
         }

-        const sharedBrowser = config.sharedBrowserContext ? await createBrowser(config, { cwd: process.cwd() }) : undefined;
+        const useSharedBrowser = !!config.browser.userDataDir;
+        let sharedBrowser: playwright.Browser | undefined;
         let clientCount = 0;
+
         const factory: mcpServer.ServerBackendFactory = {
           name: 'Playwright',
           nameInConfig: 'playwright',
           version,
           toolSchemas: tools.map(tool => tool.schema),
           create: async (clientInfo: ClientInfo) => {
+            if (useSharedBrowser && clientCount === 0)
+              sharedBrowser = await createBrowser(config, clientInfo);
             clientCount++;
             const browser = sharedBrowser || await createBrowser(config, clientInfo);
             const browserContext = config.browser.isolated ? await browser.newContext(config.browser.contextOptions) : browser.contexts()[0];
@@ -126,6 +130,7 @@ export function decorateMCPCommand(command: Command, version: string) {
               return;

             testDebug('close browser');
+            sharedBrowser = undefined;
             const browserContext = (backend as BrowserServerBackend).browserContext;
             await browserContext.close().catch(() => { });
             await browserContext.browser()!.close().catch(() => { });
PATCH

echo "Patch applied successfully."
