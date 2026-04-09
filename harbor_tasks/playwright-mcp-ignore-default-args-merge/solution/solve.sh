#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'configIgnoreDefaultArgs' packages/playwright-core/src/tools/mcp/browserFactory.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/mcp/browserFactory.ts b/packages/playwright-core/src/tools/mcp/browserFactory.ts
index dfc1c153efdf8..e4f92bd241829 100644
--- a/packages/playwright-core/src/tools/mcp/browserFactory.ts
+++ b/packages/playwright-core/src/tools/mcp/browserFactory.ts
@@ -145,15 +145,19 @@ async function createPersistentBrowser(config: FullConfig, clientInfo: ClientInf
     throw new Error(`Browser is already in use for ${userDataDir}, use --isolated to run multiple instances of the same browser`);

   const browserType = playwright[config.browser.browserName];
+  const configIgnoreDefaultArgs = config.browser.launchOptions?.ignoreDefaultArgs;
   const launchOptions: playwright.LaunchOptions & playwright.BrowserContextOptions = {
     tracesDir,
     ...config.browser.launchOptions,
     ...config.browser.contextOptions,
     handleSIGINT: false,
     handleSIGTERM: false,
-    ignoreDefaultArgs: [
-      '--disable-extensions',
-    ],
+    ignoreDefaultArgs: configIgnoreDefaultArgs === true
+      ? true
+      : [
+        '--disable-extensions',
+        ...Array.isArray(configIgnoreDefaultArgs) ? configIgnoreDefaultArgs : [],
+      ],
   };
   try {
     const browserContext = await browserType.launchPersistentContext(userDataDir, launchOptions);

PATCH

echo "Patch applied successfully."
