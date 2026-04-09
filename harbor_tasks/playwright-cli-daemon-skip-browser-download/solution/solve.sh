#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "getAsBooleanFromENV('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD')" packages/playwright-core/src/tools/cli-daemon/program.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/cli-daemon/program.ts b/packages/playwright-core/src/tools/cli-daemon/program.ts
index 5d6bdc30a801f..73cc515e2f96d 100644
--- a/packages/playwright-core/src/tools/cli-daemon/program.ts
+++ b/packages/playwright-core/src/tools/cli-daemon/program.ts
@@ -27,6 +27,7 @@ import * as configUtils from '../mcp/config';
 import { createClientInfo } from '../cli-client/registry';
 import { program } from '../../utilsBundle';
 import { registry as browserRegistry } from '../../server/registry/index';
+import { getAsBooleanFromENV } from '../../server/utils/env';

 program.argument('[session-name]', 'name of the session to create or connect to', 'default')
     .option('--headed', 'run in headed mode (non-headless)')
@@ -103,17 +104,16 @@ async function initWorkspace(initSkills: string | undefined) {
 }

 async function ensureConfiguredBrowserInstalled() {
+  if (getAsBooleanFromENV('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'))
+    return;
   if (fs.existsSync(defaultConfigFile()) || fs.existsSync(globalConfigFile())) {
     // Config exists, ensure configured browser is installed
     const clientInfo = createClientInfo();
     const config = await configUtils.resolveCLIConfigForCLI(clientInfo.daemonProfilesDir, 'default', {});
     const browserName = config.browser.browserName;
     const channel = config.browser.launchOptions.channel;
-    if (!channel || channel.startsWith('chromium')) {
-      const executable = browserRegistry.findExecutable(channel ?? browserName);
-      if (executable && !fs.existsSync(executable.executablePath()!))
-        await browserRegistry.install([executable]);
-    }
+    if (!channel || channel.startsWith('chromium'))
+      await resolveAndInstall(channel ?? browserName);
   } else {
     const channel = await findOrInstallDefaultBrowser();
     if (channel !== 'chrome')
@@ -127,15 +127,19 @@ async function findOrInstallDefaultBrowser() {
     const executable = browserRegistry.findExecutable(channel);
     if (!executable?.executablePath())
       continue;
+    await resolveAndInstall('ffmpeg');
     console.log(`✅ Found ${channel}, will use it as the default browser.`);
     return channel;
   }
-  const chromiumExecutable = browserRegistry.findExecutable('chromium');
-  if (!fs.existsSync(chromiumExecutable?.executablePath()!))
-    await browserRegistry.install([chromiumExecutable]);
+  await resolveAndInstall('chromium');
   return 'chromium';
 }

+async function resolveAndInstall(nameOrChannel: string) {
+  const executables = browserRegistry.resolveBrowsers([nameOrChannel], { shell: 'no' });
+  await browserRegistry.install(executables);
+}
+
 async function createDefaultConfig(channel: string) {
   const config = {
     browser: {

PATCH

echo "Patch applied successfully."
