#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'playwright-cli goto' packages/playwright/src/skill/SKILL.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright/src/mcp/terminal/program.ts b/packages/playwright/src/mcp/terminal/program.ts
index f4b0c01094cf3..146d3761fc2ce 100644
--- a/packages/playwright/src/mcp/terminal/program.ts
+++ b/packages/playwright/src/mcp/terminal/program.ts
@@ -573,19 +573,19 @@ async function install(args: MinimistArgs) {
   // Create .playwright folder to mark workspace root
   const playwrightDir = path.join(cwd, '.playwright');
   await fs.promises.mkdir(playwrightDir, { recursive: true });
-  console.log(`Workspace initialized at ${cwd}`);
+  console.log(`✅ Workspace initialized at \`${cwd}\`.`);

   if (args.skills) {
     const skillSourceDir = path.join(__dirname, '../../skill');
     const skillDestDir = path.join(cwd, '.claude', 'skills', 'playwright-cli');

     if (!fs.existsSync(skillSourceDir)) {
-      console.error('Skills source directory not found:', skillSourceDir);
+      console.error('❌ Skills source directory not found:', skillSourceDir);
       process.exit(1);
     }

     await fs.promises.cp(skillSourceDir, skillDestDir, { recursive: true });
-    console.log(`Skills installed to ${path.relative(cwd, skillDestDir)}`);
+    console.log(`✅ Skills installed to \`${path.relative(cwd, skillDestDir)}\`.`);
   }

   if (!args.config)
@@ -622,7 +622,7 @@ async function createDefaultConfig(channel: string) {
     },
   };
   await fs.promises.writeFile(defaultConfigFile(), JSON.stringify(config, null, 2));
-  console.log(`Created default config for ${channel} at ${path.relative(process.cwd(), defaultConfigFile())}.`);
+  console.log(`✅ Created default config for ${channel} at ${path.relative(process.cwd(), defaultConfigFile())}.`);
 }

 async function findOrInstallDefaultBrowser() {
@@ -632,7 +632,7 @@ async function findOrInstallDefaultBrowser() {
     const executable = registry.findExecutable(channel);
     if (!executable?.executablePath())
       continue;
-    console.log(`Found ${channel}, will use it as the default browser.`);
+    console.log(`✅ Found ${channel}, will use it as the default browser.`);
     return channel;
   }
   const chromiumExecutable = registry.findExecutable('chromium');
diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index 847a1764894df..29182e7630425 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -9,25 +9,29 @@ allowed-tools: Bash(playwright-cli:*)
 ## Quick start

 ```bash
-playwright-cli open https://playwright.dev
+# open new browser
+playwright-cli open
+# navigate to a page
+playwright-cli goto https://playwright.dev
+# interact with the page using refs from the snapshot
 playwright-cli click e15
 playwright-cli type "page.click"
 playwright-cli press Enter
+# take a screenshot
+playwright-cli screenshot
+# close the browser
+playwright-cli close
 ```

-## Core workflow
-
-1. Navigate: `playwright-cli open https://example.com`
-2. Interact using refs from the snapshot
-3. Re-snapshot after significant changes
-
 ## Commands

 ### Core

 ```bash
+playwright-cli open
+# open and navigate right away
 playwright-cli open https://example.com/
-playwright-cli close
+playwright-cli goto https://playwright.dev
 playwright-cli type "search query"
 playwright-cli click e3
 playwright-cli dblclick e7
@@ -46,6 +50,7 @@ playwright-cli dialog-accept
 playwright-cli dialog-accept "confirmation text"
 playwright-cli dialog-dismiss
 playwright-cli resize 1920 1080
+playwright-cli close
 ```

 ### Navigation
@@ -153,8 +158,8 @@ playwright-cli video-stop video.webm
 ### Install

 ```bash
+playwright-cli install --skills
 playwright-cli install-browser
-playwright-cli install-skills
 ```

 ### Configuration
@@ -184,10 +189,13 @@ playwright-cli delete-data
 ### Browser Sessions

 ```bash
-playwright-cli -s=mysession open example.com
+# create new browser session named "mysession" with persistent profile
+playwright-cli -s=mysession open example.com --persistent
+# same with manually specified profile directory (use when requested explicitly)
+playwright-cli -s=mysession open example.com --profile=/path/to/profile
 playwright-cli -s=mysession click e6
 playwright-cli -s=mysession close  # stop a named browser
-playwright-cli -s=mysession delete-data  # delete user data for named browser
+playwright-cli -s=mysession delete-data  # delete user data for persistent session

 playwright-cli list
 # Close all browsers
@@ -206,6 +214,7 @@ playwright-cli fill e1 "user@example.com"
 playwright-cli fill e2 "password123"
 playwright-cli click e3
 playwright-cli snapshot
+playwright-cli close
 ```

 ## Example: Multi-tab workflow
@@ -216,6 +225,7 @@ playwright-cli tab-new https://example.com/other
 playwright-cli tab-list
 playwright-cli tab-select 0
 playwright-cli snapshot
+playwright-cli close
 ```

 ## Example: Debugging with DevTools
@@ -226,6 +236,7 @@ playwright-cli click e4
 playwright-cli fill e7 "test"
 playwright-cli console
 playwright-cli network
+playwright-cli close
 ```

 ```bash
@@ -234,6 +245,7 @@ playwright-cli tracing-start
 playwright-cli click e4
 playwright-cli fill e7 "test"
 playwright-cli tracing-stop
+playwright-cli close
 ```

 ## Specific tasks
diff --git a/tests/mcp/cli-misc.spec.ts b/tests/mcp/cli-misc.spec.ts
index 3e6cb7b8a64ee..1b20c49e4a0bc 100644
--- a/tests/mcp/cli-misc.spec.ts
+++ b/tests/mcp/cli-misc.spec.ts
@@ -43,7 +43,7 @@ test('install workspace', async ({ cli }, testInfo) => {

 test('install workspace w/skills', async ({ cli }, testInfo) => {
   const { output } = await cli('install', '--skills');
-  expect(output).toContain(`Skills installed to .claude${path.sep}skills${path.sep}playwright-cli`);
+  expect(output).toContain(`Skills installed to \`.claude${path.sep}skills${path.sep}playwright-cli\`.`);

   const skillFile = testInfo.outputPath('.claude', 'skills', 'playwright-cli', 'SKILL.md');
   expect(fs.existsSync(skillFile)).toBe(true);

PATCH

echo "Patch applied successfully."
