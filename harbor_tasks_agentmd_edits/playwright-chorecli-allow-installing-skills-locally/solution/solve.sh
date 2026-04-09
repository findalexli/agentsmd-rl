#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied (check for install-skills command)
if grep -q 'install-skills' packages/playwright/src/mcp/terminal/commands.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch from PR #39078
git apply - <<'PATCH'
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
index d4f6b7368af93b..6c7d7763db41e 100644
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
index bad843297ab6c..950f47950c79 100644
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
PATCH

echo "Patch applied successfully."
