#!/bin/bash
set -e

cd /workspace/playwright

# Check if already applied (idempotency check)
if grep -q "async (page) =>" packages/playwright/src/mcp/browser/tools/runCode.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the patch
cat << 'GITPATCH' | git apply -
diff --git a/examples/todomvc/.claude/agents/playwright-test-planner.md b/examples/todomvc/.claude/agents/playwright-test-planner.md
index 78af43b534500..b33d6ba96e82a 100644
--- a/examples/todomvc/.claude/agents/playwright-test-planner.md
+++ b/examples/todomvc/.claude/agents/playwright-test-planner.md
@@ -1,7 +1,7 @@
 ---
 name: playwright-test-planner
 description: Use this agent when you need to create comprehensive test plan for a web application or website
-tools: Glob, Grep, Read, LS, mcp__playwright-test__browser_click, mcp__playwright-test__browser_close, mcp__playwright-test__browser_console_messages, mcp__playwright-test__browser_drag, mcp__playwright-test__browser_evaluate, mcp__playwright-test__browser_file_upload, mcp__playwright-test__browser_handle_dialog, mcp__playwright-test__browser_hover, mcp__playwright-test__browser_navigate, mcp__playwright-test__browser_navigate_back, mcp__playwright-test__browser_network_requests, mcp__playwright-test__browser_press_key, mcp__playwright-test__browser_select_option, mcp__playwright-test__browser_snapshot, mcp__playwright-test__browser_take_screenshot, mcp__playwright-test__browser_type, mcp__playwright-test__browser_wait_for, mcp__playwright-test__planner_setup_page, mcp__playwright-test__planner_save_plan
+tools: Glob, Grep, Read, LS, mcp__playwright-test__browser_click, mcp__playwright-test__browser_close, mcp__playwright-test__browser_console_messages, mcp__playwright-test__browser_drag, mcp__playwright-test__browser_evaluate, mcp__playwright-test__browser_file_upload, mcp__playwright-test__browser_handle_dialog, mcp__playwright-test__browser_hover, mcp__playwright-test__browser_navigate, mcp__playwright-test__browser_navigate_back, mcp__playwright-test__browser_network_requests, mcp__playwright-test__browser_press_key, mcp__playwright-test__browser_run_code, mcp__playwright-test__browser_select_option, mcp__playwright-test__browser_snapshot, mcp__playwright-test__browser_take_screenshot, mcp__playwright-test__browser_type, mcp__playwright-test__browser_wait_for, mcp__playwright-test__planner_setup_page, mcp__playwright-test__planner_save_plan
 model: sonnet
 color: green
 ---

diff --git a/examples/todomvc/.github/agents/playwright-test-planner.agent.md b/examples/todomvc/.github/agents/playwright-test-planner.agent.md
index 6ac9a5f1f3241..c10240e2be737 100644
--- a/examples/todomvc/.github/agents/playwright-test-planner.agent.md
+++ b/examples/todomvc/.github/agents/playwright-test-planner.agent.md
@@ -16,6 +16,7 @@ tools:
   - playwright-test/browser_navigate_back
   - playwright-test/browser_network_requests
   - playwright-test/browser_press_key
+  - playwright-test/browser_run_code
   - playwright-test/browser_select_option
   - playwright-test/browser_snapshot
   - playwright-test/browser_take_screenshot

diff --git a/packages/playwright/src/agents/playwright-test-planner.agent.md b/packages/playwright/src/agents/playwright-test-planner.agent.md
index ce0780ba569ef..4ff02c115aa6d 100644
--- a/packages/playwright/src/agents/playwright-test-planner.agent.md
+++ b/packages/playwright/src/agents/playwright-test-planner.agent.md
@@ -17,6 +17,7 @@ tools:
   - playwright-test/browser_navigate_back
   - playwright-test/browser_network_requests
   - playwright-test/browser_press_key
+  - playwright-test/browser_run_code
   - playwright-test/browser_select_option
   - playwright-test/browser_snapshot
   - playwright-test/browser_take_screenshot

diff --git a/packages/playwright/src/mcp/browser/tools/runCode.ts b/packages/playwright/src/mcp/browser/tools/runCode.ts
index eafe672c304e5..537ffdb06444c 100644
--- a/packages/playwright/src/mcp/browser/tools/runCode.ts
+++ b/packages/playwright/src/mcp/browser/tools/runCode.ts
@@ -22,7 +22,7 @@ import { z } from 'playwright-core/lib/mcpBundle';
 import { defineTabTool } from './tool';

 const codeSchema = z.object({
-  code: z.string().describe(`Playwright code snippet to run. The snippet should access the \`page\` object to interact with the page. Can make multiple statements. \`return\` is allowed. For example: \`await page.getByRole('button', { name: 'Submit' }).click(); return await page.title();\``),
+  code: z.string().describe(`A JavaScript function containing Playwright code to execute. It will be invoked with a single argument, page, which you can use for any page interaction. For example: \`async (page) => { await page.getByRole('button', { name: 'Submit' }).click(); return await page.title(); }\``),
 });

 const runCode = defineTabTool({
@@ -37,7 +37,7 @@ const runCode = defineTabTool({

   handle: async (tab, params, response) => {
     response.setIncludeSnapshot();
-    response.addCode(params.code);
+    response.addCode(`await (${params.code})(page);`);
     const __end__ = new ManualPromise<void>();
     const context = {
       page: tab.page,
@@ -47,9 +47,7 @@ const runCode = defineTabTool({
     await tab.waitForCompletion(async () => {
       const snippet = `(async () => {
         try {
-          const result = await (async () => {
-            ${params.code};
-          })();
+          const result = await (${params.code})(page);
           __end__.resolve(JSON.stringify(result));
         } catch (e) {
           __end__.reject(e);

diff --git a/tests/mcp/run-code.spec.ts b/tests/mcp/run-code.spec.ts
index 8c3f13d75e6f8..e5f2c9d9fbd15 100644
--- a/tests/mcp/run-code.spec.ts
+++ b/tests/mcp/run-code.spec.ts
@@ -12,13 +12,13 @@ test('browser_run_code', async ({ client, server }) => {
     arguments: { url: server.PREFIX },
   });

+  const code = 'async (page) => await page.getByRole("button", { name: "Submit" }).click()';
   expect(await client.callTool({
     name: 'browser_run_code',
     arguments: {
-      code: 'await page.getByRole("button", { name: "Submit" }).click()',
+      code,
     },
   })).toHaveResponse({
-    code: `await page.getByRole(\"button\", { name: \"Submit\" }).click()`,
+    code: `await (${code})(page);`,
     consoleMessages: expect.stringContaining('- [LOG] Submit'),
   });
 });
@@ -34,10 +34,10 @@ test('browser_run_code block', async ({ client, server }) => {
   expect(await client.callTool({
     name: 'browser_run_code',
     arguments: {
-      code: 'await page.getByRole("button", { name: "Submit" }).click(); await page.getByRole("button", { name: "Submit" }).click();',
+      code: 'async (page) => { await page.getByRole("button", { name: "Submit" }).click(); await page.getByRole("button", { name: "Submit" }).click(); }',
     },
   })).toHaveResponse({
-    code: expect.stringContaining(`await page.getByRole(\"button\", { name: \"Submit\" }).click()`),
+    code: expect.stringContaining(`await page.getByRole("button", { name: "Submit" }).click()`),
     consoleMessages: expect.stringMatching(/\[LOG\] Submit.*\n.*\[LOG\] Submit/),
   });
 });
@@ -53,7 +53,7 @@ test('browser_run_code no-require', async ({ client, server }) => {
   expect(await client.callTool({
     name: 'browser_run_code',
     arguments: {
-      code: `require('fs');`,
+      code: `(page) => { require('fs'); }`,
     },
   })).toHaveResponse({
     result: expect.stringContaining(`ReferenceError: require is not defined`),
@@ -68,12 +68,12 @@ test('browser_run_code return value', async ({ client, server }) => {
     arguments: { url: server.PREFIX },
   });

-  const code = 'await page.getByRole("button", { name: "Submit" }).click(); return { message: "Hello, world!" }; await page.getByRole("banner").click();';
+  const code = 'async (page) => { await page.getByRole("button", { name: "Submit" }).click(); return { message: "Hello, world!" }; await page.getByRole("banner").click(); }';
   expect(await client.callTool({
     name: 'browser_run_code',
     arguments: {
       code,
     },
   })).toHaveResponse({
-    code,
+    code: `await (${code})(page);`,
     consoleMessages: expect.stringContaining('- [LOG] Submit'),
     result: '{"message":"Hello, world!"}',
   });
GITPATCH

echo "Patch applied successfully!"
