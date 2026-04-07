#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'skillMode' packages/playwright/src/mcp/browser/config.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full gold patch
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright/src/mcp/browser/config.ts b/packages/playwright/src/mcp/browser/config.ts
index 953b98989fde4..81a1f379aa9d8 100644
--- a/packages/playwright/src/mcp/browser/config.ts
+++ b/packages/playwright/src/mcp/browser/config.ts
@@ -126,6 +126,7 @@ export type FullConfig = Config & {
     action: number;
     navigation: number;
   },
+  skillMode?: boolean;
 };
 
 export async function resolveConfig(config: Config): Promise<FullConfig> {
diff --git a/packages/playwright/src/mcp/browser/response.ts b/packages/playwright/src/mcp/browser/response.ts
index 910833bb58cac..ab6a7ea8708f7 100644
--- a/packages/playwright/src/mcp/browser/response.ts
+++ b/packages/playwright/src/mcp/browser/response.ts
@@ -158,7 +158,7 @@ export class Response {
     // Handle modal states.
     if (tabSnapshot?.modalStates.length) {
       const text = addSection('Modal state');
-      text.push(...renderModalStates(tabSnapshot.modalStates));
+      text.push(...renderModalStates(this._context.config, tabSnapshot.modalStates));
     }
 
     // Handle tab snapshot
diff --git a/packages/playwright/src/mcp/browser/tab.ts b/packages/playwright/src/mcp/browser/tab.ts
index 665240fffc399..3d94e2a5a8c5b 100644
--- a/packages/playwright/src/mcp/browser/tab.ts
+++ b/packages/playwright/src/mcp/browser/tab.ts
@@ -28,6 +28,7 @@ import { requireOrImport } from '../../transform/transform';
 import type { Context } from './context';
 import type { Page } from '../../../../playwright-core/src/client/page';
 import type { Locator } from '../../../../playwright-core/src/client/locator';
+import type { FullConfig } from './config';
 
 export const TabEvents = {
   modalState: 'modalState'
@@ -111,7 +112,7 @@ export class Tab extends EventEmitter<TabEventsInterface> {
         type: 'fileChooser',
         description: 'File chooser',
         fileChooser: chooser,
-        clearedBy: uploadFile.schema.name,
+        clearedBy: { tool: uploadFile.schema.name, skill: 'upload' }
       });
     });
     page.on('dialog', dialog => this._dialogShown(dialog));
@@ -173,7 +174,7 @@ export class Tab extends EventEmitter<TabEventsInterface> {
       type: 'dialog',
       description: `"${dialog.type()}" dialog with message "${dialog.message()}"`,
       dialog,
-      clearedBy: handleDialog.schema.name
+      clearedBy: { tool: handleDialog.schema.name, skill: 'dialog-accept or dialog-dismiss' }
     });
   }
 
@@ -403,12 +404,12 @@ function pageErrorToConsoleMessage(errorOrValue: Error | any): ConsoleMessage {
   };
 }
 
-export function renderModalStates(modalStates: ModalState[]): string[] {
+export function renderModalStates(config: FullConfig, modalStates: ModalState[]): string[] {
   const result: string[] = [];
   if (modalStates.length === 0)
     result.push('- There is no modal state present');
   for (const state of modalStates)
-    result.push(`- [${state.description}]: can be handled by the "${state.clearedBy}" tool`);
+    result.push(`- [${state.description}]: can be handled by ${config.skillMode ? state.clearedBy.skill : state.clearedBy.tool}`);
   return result;
 }
 
diff --git a/packages/playwright/src/mcp/browser/tools/evaluate.ts b/packages/playwright/src/mcp/browser/tools/evaluate.ts
index 5e629c4003644..347eaf08bfe89 100644
--- a/packages/playwright/src/mcp/browser/tools/evaluate.ts
+++ b/packages/playwright/src/mcp/browser/tools/evaluate.ts
@@ -39,6 +39,8 @@ const evaluate = defineTabTool({
 
   handle: async (tab, params, response) => {
     let locator: Awaited<ReturnType<Tab['refLocator']>> | undefined;
+    if (!params.function.includes('=>'))
+      params.function = `() => (${params.function})`;
     if (params.ref) {
       locator = await tab.refLocator({ ref: params.ref, element: params.element || 'element' });
       response.addCode(`await page.${locator.resolved}.evaluate(${escapeWithQuotes(params.function)});`);
diff --git a/packages/playwright/src/mcp/browser/tools/tool.ts b/packages/playwright/src/mcp/browser/tools/tool.ts
index d4c4e80f66585..dc147f5a967f4 100644
--- a/packages/playwright/src/mcp/browser/tools/tool.ts
+++ b/packages/playwright/src/mcp/browser/tools/tool.ts
@@ -26,14 +26,14 @@ export type FileUploadModalState = {
   type: 'fileChooser';
   description: string;
   fileChooser: playwright.FileChooser;
-  clearedBy: string;
+  clearedBy: { tool: string; skill: string };
 };
 
 export type DialogModalState = {
   type: 'dialog';
   description: string;
   dialog: playwright.Dialog;
-  clearedBy: string;
+  clearedBy: { tool: string; skill: string };
 };
 
 export type ModalState = FileUploadModalState | DialogModalState;
diff --git a/packages/playwright/src/mcp/program.ts b/packages/playwright/src/mcp/program.ts
index d9653f0a5846b..e8d8312434907 100644
--- a/packages/playwright/src/mcp/program.ts
+++ b/packages/playwright/src/mcp/program.ts
@@ -112,6 +112,7 @@ export function decorateCommand(command: Command, version: string) {
         }
 
         if (options.daemon) {
+          config.skillMode = true;
           config.outputDir = path.join(process.cwd(), '.playwright-cli');
           config.outputMode = 'file';
           config.codegen = 'none';
diff --git a/packages/playwright/src/mcp/terminal/SKILL.md b/packages/playwright/src/mcp/terminal/SKILL.md
new file mode 100644
index 0000000000000..a4f8489a64a5e
--- /dev/null
+++ b/packages/playwright/src/mcp/terminal/SKILL.md
@@ -0,0 +1,159 @@
+---
+name: playwright-cli
+description: Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, test web applications, or extract information from web pages.
+allowed-tools: Bash(playwright-cli:*)
+---
+
+# Browser Automation with playwright-cli
+
+## Quick start
+
+```bash
+playwright-cli open https://playwright.dev
+playwright-cli click e15
+playwright-cli type "page.click"
+playwright-cli press Enter
+```
+
+## Core workflow
+
+1. Navigate: `playwright-cli open https://example.com`
+2. Snapshot: `playwright-cli snapshot` (returns elements with refs like `ref=e1`, `ref=e2`)
+3. Interact using refs from the snapshot
+4. Re-snapshot after navigation or significant DOM changes
+
+## Commands
+
+### Core
+
+```bash
+playwright-cli open https://example.com/
+playwright-cli close
+playwright-cli type "search query"
+playwright-cli click e3
+playwright-cli dblclick e7
+playwright-cli fill e5 "user@example.com"
+playwright-cli drag e2 e8
+playwright-cli hover e4
+playwright-cli select e9 "option-value"
+playwright-cli upload ./document.pdf
+playwright-cli check e12
+playwright-cli uncheck e12
+playwright-cli snapshot
+playwright-cli eval "document.title"
+playwright-cli eval "el => el.textContent" e5
+playwright-cli dialog-accept
+playwright-cli dialog-accept "confirmation text"
+playwright-cli dialog-dismiss
+playwright-cli resize 1920 1080
+```
+
+### Navigation
+
+```bash
+playwright-cli go-back
+playwright-cli go-forward
+playwright-cli reload
+```
+
+### Keyboard
+
+```bash
+playwright-cli press Enter
+playwright-cli press ArrowDown
+playwright-cli keydown Shift
+playwright-cli keyup Shift
+```
+
+### Mouse
+
+```bash
+playwright-cli mousemove 150 300
+playwright-cli mousedown
+playwright-cli mousedown right
+playwright-cli mouseup
+playwright-cli mouseup right
+playwright-cli mousewheel 0 100
+```
+
+### Save as
+
+```bash
+playwright-cli screenshot
+playwright-cli screenshot e5
+playwright-cli pdf
+```
+
+### Tabs
+
+```bash
+playwright-cli tab-list
+playwright-cli tab-new
+playwright-cli tab-new https://example.com/page
+playwright-cli tab-close
+playwright-cli tab-close 2
+playwright-cli tab-select 0
+```
+
+### DevTools
+
+```bash
+playwright-cli console
+playwright-cli console warning
+playwright-cli network
+playwright-cli run-code "await page.waitForTimeout(1000)"
+playwright-cli tracing-start
+playwright-cli tracing-stop
+```
+
+### Sessions
+
+```bash
+playwright-cli --session=mysession open example.com
+playwright-cli --session=mysession click e6
+playwright-cli session-list
+playwright-cli session-stop mysession
+playwright-cli session-stop-all
+playwright-cli session-delete
+playwright-cli session-delete mysession
+```
+
+## Example: Form submission
+
+```bash
+playwright-cli open https://example.com/form
+playwright-cli snapshot
+
+playwright-cli fill e1 "user@example.com"
+playwright-cli fill e2 "password123"
+playwright-cli click e3
+playwright-cli snapshot
+```
+
+## Example: Multi-tab workflow
+
+```bash
+playwright-cli open https://example.com
+playwright-cli tab-new https://example.com/other
+playwright-cli tab-list
+playwright-cli tab-select 0
+playwright-cli snapshot
+```
+
+## Example: Debugging with DevTools
+
+```bash
+playwright-cli open https://example.com
+playwright-cli click e4
+playwright-cli fill e7 "test"
+playwright-cli console
+playwright-cli network
+```
+
+```bash
+playwright-cli open https://example.com
+playwright-cli tracing-start
+playwright-cli click e4
+playwright-cli fill e7 "test"
+playwright-cli tracing-stop
+```
diff --git a/packages/playwright/src/mcp/terminal/commands.ts b/packages/playwright/src/mcp/terminal/commands.ts
index dc183b64e2328..b81042bf3068e 100644
--- a/packages/playwright/src/mcp/terminal/commands.ts
+++ b/packages/playwright/src/mcp/terminal/commands.ts
@@ -75,7 +75,7 @@ const reload = declareCommand({
 // Keyboard
 
 const pressKey = declareCommand({
-  name: 'key-press',
+  name: 'press',
   description: 'Press a key on the keyboard, `a`, `ArrowLeft`',
   category: 'keyboard',
   args: z.object({
@@ -100,7 +100,7 @@ const type = declareCommand({
 });
 
 const keydown = declareCommand({
-  name: 'key-down',
+  name: 'keydown',
   description: 'Press a key down on the keyboard',
   category: 'keyboard',
   args: z.object({
@@ -111,7 +111,7 @@ const keydown = declareCommand({
 });
 
 const keyup = declareCommand({
-  name: 'key-up',
+  name: 'keyup',
   description: 'Press a key up on the keyboard',
   category: 'keyboard',
   args: z.object({
@@ -124,7 +124,7 @@ const keyup = declareCommand({
 // Mouse
 
 const mouseMove = declareCommand({
-  name: 'mouse-move',
+  name: 'mousemove',
   description: 'Move mouse to a given position',
   category: 'mouse',
   args: z.object({
@@ -136,7 +136,7 @@ const mouseMove = declareCommand({
 });
 
 const mouseDown = declareCommand({
-  name: 'mouse-down',
+  name: 'mousedown',
   description: 'Press mouse down',
   category: 'mouse',
   args: z.object({
@@ -147,7 +147,7 @@ const mouseDown = declareCommand({
 });
 
 const mouseUp = declareCommand({
-  name: 'mouse-up',
+  name: 'mouseup',
   description: 'Press mouse up',
   category: 'mouse',
   args: z.object({
@@ -158,7 +158,7 @@ const mouseUp = declareCommand({
 });
 
 const mouseWheel = declareCommand({
-  name: 'mouse-wheel',
+  name: 'mousewheel',
   description: 'Scroll mouse wheel',
   category: 'mouse',
   args: z.object({
diff --git a/packages/playwright/src/mcp/terminal/help.json b/packages/playwright/src/mcp/terminal/help.json
index 15f83917cce07..b049024a00334 100644
--- a/packages/playwright/src/mcp/terminal/help.json
+++ b/packages/playwright/src/mcp/terminal/help.json
@@ -1,5 +1,5 @@
 {
-  "global": "Usage: playwright-cli <command> [args] [options]\n\nCore:\n  open <url>                  open url\n  close                       close the page\n  type <text>                 type text into editable element\n  click <ref> [button]        perform click on a web page\n  dblclick <ref> [button]     perform double click on a web page\n  fill <ref> <text>           fill text into editable element\n  drag <startRef> <endRef>    perform drag and drop between two elements\n  hover <ref>                 hover over element on page\n  select <ref> <val>          select an option in a dropdown\n  upload <file>               upload one or multiple files\n  check <ref>                 check a checkbox or radio button\n  uncheck <ref>               uncheck a checkbox or radio button\n  snapshot                    capture page snapshot to obtain element ref\n  eval <func> [ref]           evaluate javascript expression on page or element\n  dialog-accept [prompt]      accept a dialog\n  dialog-dismiss              dismiss a dialog\n  resize <w> <h>              resize the browser window\n\nNavigation:\n  go-back                     go back to the previous page\n  go-forward                  go forward to the next page\n  reload                      reload the current page\n\nKeyboard:\n  key-press <key>             press a key on the keyboard, `a`, `arrowleft`\n  key-down <key>              press a key down on the keyboard\n  key-up <key>                press a key up on the keyboard\n\nMouse:\n  mouse-move <x> <y>          move mouse to a given position\n  mouse-down [button]         press mouse down\n  mouse-up [button]           press mouse up\n  mouse-wheel <dx> <dy>       scroll mouse wheel\n\nSave as:\n  screenshot [ref]            screenshot of the current page or element\n  pdf                         save page as pdf\n\nTabs:\n  tab-list                    list all tabs\n  tab-new [url]               create a new tab\n  tab-close [index]           close a browser tab\n  tab-select <index>          select a browser tab\n\nDevTools:\n  console [min-level]         list console messages\n  network                     list all network requests since loading the page\n  run-code <code>             run playwright code snippet\n  tracing-start               start trace recording\n  tracing-stop                stop trace recording\n\nSessions:\n  session-list                list all sessions\n  session-stop [name]         stop session\n  session-stop-all            stop all sessions\n  session-delete [name]       delete session data",
+  "global": "Usage: playwright-cli <command> [args] [options]\n\nCore:\n  open <url>                  open url\n  close                       close the page\n  type <text>                 type text into editable element\n  click <ref> [button]        perform click on a web page\n  dblclick <ref> [button]     perform double click on a web page\n  fill <ref> <text>           fill text into editable element\n  drag <startRef> <endRef>    perform drag and drop between two elements\n  hover <ref>                 hover over element on page\n  select <ref> <val>          select an option in a dropdown\n  upload <file>               upload one or multiple files\n  check <ref>                 check a checkbox or radio button\n  uncheck <ref>               uncheck a checkbox or radio button\n  snapshot                    capture page snapshot to obtain element ref\n  eval <func> [ref]           evaluate javascript expression on page or element\n  dialog-accept [prompt]      accept a dialog\n  dialog-dismiss              dismiss a dialog\n  resize <w> <h>              resize the browser window\n\nNavigation:\n  go-back                     go back to the previous page\n  go-forward                  go forward to the next page\n  reload                      reload the current page\n\nKeyboard:\n  press <key>                 press a key on the keyboard, `a`, `arrowleft`\n  keydown <key>               press a key down on the keyboard\n  keyup <key>                 press a key up on the keyboard\n\nMouse:\n  mousemove <x> <y>           move mouse to a given position\n  mousedown [button]          press mouse down\n  mouseup [button]            press mouse up\n  mousewheel <dx> <dy>        scroll mouse wheel\n\nSave as:\n  screenshot [ref]            screenshot of the current page or element\n  pdf                         save page as pdf\n\nTabs:\n  tab-list                    list all tabs\n  tab-new [url]               create a new tab\n  tab-close [index]           close a browser tab\n  tab-select <index>          select a browser tab\n\nDevTools:\n  console [min-level]         list console messages\n  network                     list all network requests since loading the page\n  run-code <code>             run playwright code snippet\n  tracing-start               start trace recording\n  tracing-stop                stop trace recording\n\nSessions:\n  session-list                list all sessions\n  session-stop [name]         stop session\n  session-stop-all            stop all sessions\n  session-delete [name]       delete session data",
   "commands": {
     "open": "playwright-cli open <url>\n\nOpen URL\n\nArguments:\n  <url>                       the url to navigate to\nOptions:\n  --headed                    run browser in headed mode",
     "close": "playwright-cli close \n\nClose the page\n",
@@ -22,13 +22,13 @@
     "go-back": "playwright-cli go-back \n\nGo back to the previous page\n",
     "go-forward": "playwright-cli go-forward \n\nGo forward to the next page\n",
     "reload": "playwright-cli reload \n\nReload the current page\n",
-    "key-press": "playwright-cli key-press <key>\n\nPress a key on the keyboard, `a`, `ArrowLeft`\n\nArguments:\n  <key>                       name of the key to press or a character to generate, such as `arrowleft` or `a`",
-    "key-down": "playwright-cli key-down <key>\n\nPress a key down on the keyboard\n\nArguments:\n  <key>                       name of the key to press or a character to generate, such as `arrowleft` or `a`",
-    "key-up": "playwright-cli key-up <key>\n\nPress a key up on the keyboard\n\nArguments:\n  <key>                       name of the key to press or a character to generate, such as `arrowleft` or `a`",
-    "mouse-move": "playwright-cli mouse-move <x> <y>\n\nMove mouse to a given position\n\nArguments:\n  <x>                         x coordinate\n  <y>                         y coordinate",
-    "mouse-down": "playwright-cli mouse-down [button]\n\nPress mouse down\n\nArguments:\n  [button]                    button to press, defaults to left",
-    "mouse-up": "playwright-cli mouse-up [button]\n\nPress mouse up\n\nArguments:\n  [button]                    button to press, defaults to left",
-    "mouse-wheel": "playwright-cli mouse-wheel <dx> <dy>\n\nScroll mouse wheel\n\nArguments:\n  <dx>                        y delta\n  <dy>                        x delta",
+    "press": "playwright-cli press <key>\n\nPress a key on the keyboard, `a`, `ArrowLeft`\n\nArguments:\n  <key>                       name of the key to press or a character to generate, such as `arrowleft` or `a`",
+    "keydown": "playwright-cli keydown <key>\n\nPress a key down on the keyboard\n\nArguments:\n  <key>                       name of the key to press or a character to generate, such as `arrowleft` or `a`",
+    "keyup": "playwright-cli keyup <key>\n\nPress a key up on the keyboard\n\nArguments:\n  <key>                       name of the key to press or a character to generate, such as `arrowleft` or `a`",
+    "mousemove": "playwright-cli mousemove <x> <y>\n\nMove mouse to a given position\n\nArguments:\n  <x>                         x coordinate\n  <y>                         y coordinate",
+    "mousedown": "playwright-cli mousedown [button]\n\nPress mouse down\n\nArguments:\n  [button]                    button to press, defaults to left",
+    "mouseup": "playwright-cli mouseup [button]\n\nPress mouse up\n\nArguments:\n  [button]                    button to press, defaults to left",
+    "mousewheel": "playwright-cli mousewheel <dx> <dy>\n\nScroll mouse wheel\n\nArguments:\n  <dx>                        y delta\n  <dy>                        x delta",
     "screenshot": "playwright-cli screenshot [ref]\n\nscreenshot of the current page or element\n\nArguments:\n  [ref]                       exact target element reference from the page snapshot.\nOptions:\n  --filename                  file name to save the screenshot to. defaults to `page-{timestamp}.{png|jpeg}` if not specified.\n  --full-page                 when true, takes a screenshot of the full scrollable page, instead of the currently visible viewport.",
     "pdf": "playwright-cli pdf \n\nSave page as PDF\n\nOptions:\n  --filename                  file name to save the pdf to. defaults to `page-{timestamp}.pdf` if not specified.",
     "tab-list": "playwright-cli tab-list \n\nList all tabs\n",
diff --git a/tests/mcp/cli.spec.ts b/tests/mcp/cli.spec.ts
index 4dd2a6df949be..8fd4e4469a3de 100644
--- a/tests/mcp/cli.spec.ts
+++ b/tests/mcp/cli.spec.ts
@@ -132,6 +132,12 @@ test.describe('core', () => {
     expect(output).toContain('"Title"');
   });
 
+  test('eval no arrow', async ({ cli, daemon, server }) => {
+    await cli('open', server.HELLO_WORLD);
+    const { output } = await cli('eval', 'document.title');
+    expect(output).toContain('"Title"');
+  });
+
   test('eval <ref>', async ({ cli, daemon, server }) => {
     server.setContent('/', `<button>Submit</button>`, 'text/html');
     await cli('open', server.PREFIX);
@@ -144,6 +150,7 @@ test.describe('core', () => {
     await cli('open', server.PREFIX);
     const { output } = await cli('click', 'e2');
     expect(output).toContain('MyAlert');
+    expect(output).toContain('["alert" dialog with message "MyAlert"]: can be handled by dialog-accept or dialog-dismiss');
     await cli('dialog-accept');
     const { snapshot } = await cli('snapshot');
     expect(snapshot).not.toContain('MyAlert');
@@ -198,50 +205,50 @@ test.describe('navigation', () => {
 });
 
 test.describe('keyboard', () => {
-  test('key-press', async ({ cli, daemon, server }) => {
+  test('press', async ({ cli, daemon, server }) => {
     server.setContent('/', `<input type=text>`, 'text/html');
     await cli('open', server.PREFIX);
     await cli('click', 'e2');
-    await cli('key-press', 'h');
+    await cli('press', 'h');
     const { snapshot } = await cli('snapshot');
     expect(snapshot).toBe(`- textbox [active] [ref=e2]: h`);
   });
 
-  test('key-down key-up', async ({ cli, daemon, server }) => {
+  test('keydown keyup', async ({ cli, daemon, server }) => {
     server.setContent('/', `<input type=text>`, 'text/html');
     await cli('open', server.PREFIX);
     await cli('click', 'e2');
-    await cli('key-down', 'h');
-    await cli('key-up', 'h');
+    await cli('keydown', 'h');
+    await cli('keyup', 'h');
     const { snapshot } = await cli('snapshot');
     expect(snapshot).toBe(`- textbox [active] [ref=e2]: h`);
   });
 });
 
 test.describe('mouse', () => {
-  test('mouse-move', async ({ cli, daemon, server }) => {
+  test('mousemove', async ({ cli, daemon, server }) => {
     server.setContent('/', eventsPage, 'text/html');
     await cli('open', server.PREFIX);
-    await cli('mouse-move', '45', '35');
+    await cli('mousemove', '45', '35');
     const { snapshot } = await cli('snapshot');
     expect(snapshot).toContain('mouse move 45 35');
   });
 
-  test('mouse-down mouse-up', async ({ cli, daemon, server }) => {
+  test('mousedown mouseup', async ({ cli, daemon, server }) => {
     server.setContent('/', eventsPage, 'text/html');
     await cli('open', server.PREFIX);
-    await cli('mouse-move', '45', '35');
-    await cli('mouse-down');
-    await cli('mouse-up');
+    await cli('mousemove', '45', '35');
+    await cli('mousedown');
+    await cli('mouseup');
     const { snapshot } = await cli('snapshot');
     expect(snapshot).toContain('mouse down');
     expect(snapshot).toContain('mouse up');
   });
 
-  test('mouse-wheel', async ({ cli, daemon, server }) => {
+  test('mousewheel', async ({ cli, daemon, server }) => {
     server.setContent('/', eventsPage, 'text/html');
     await cli('open', server.PREFIX);
-    await cli('mouse-wheel', '10', '5');
+    await cli('mousewheel', '10', '5');
     const { snapshot } = await cli('snapshot');
     expect(snapshot).toContain('wheel 5 10');
   });
diff --git a/tests/mcp/dialogs.spec.ts b/tests/mcp/dialogs.spec.ts
index c0515f566c285..4c876e9e0c1a6 100644
--- a/tests/mcp/dialogs.spec.ts
+++ b/tests/mcp/dialogs.spec.ts
@@ -33,7 +33,7 @@ test('alert dialog', async ({ client, server }) => {
     },
   })).toHaveResponse({
     code: `await page.getByRole('button', { name: 'Button' }).click();`,
-    modalState: `- ["alert" dialog with message "Alert"]: can be handled by the "browser_handle_dialog" tool`,
+    modalState: `- ["alert" dialog with message "Alert"]: can be handled by browser_handle_dialog`,
   });
 
   expect(await client.callTool({
@@ -44,7 +44,7 @@ test('alert dialog', async ({ client, server }) => {
     },
   })).toHaveResponse({
     code: undefined,
-    modalState: `- ["alert" dialog with message "Alert"]: can be handled by the "browser_handle_dialog" tool`,
+    modalState: `- ["alert" dialog with message "Alert"]: can be handled by browser_handle_dialog`,
   });
 
   expect(await client.callTool({
@@ -81,7 +81,7 @@ test('two alert dialogs', async ({ client, server }) => {
     },
   })).toHaveResponse({
     code: `await page.getByRole('button', { name: 'Button' }).click();`,
-    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert 1"]: can be handled by the "browser_handle_dialog" tool`),
+    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert 1"]: can be handled by browser_handle_dialog`),
   });
 
   const result = await client.callTool({
@@ -92,7 +92,7 @@ test('two alert dialogs', async ({ client, server }) => {
   });
 
   expect(result).toHaveResponse({
-    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert 2"]: can be handled by the "browser_handle_dialog" tool`),
+    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert 2"]: can be handled by browser_handle_dialog`),
   });
 
   const result2 = await client.callTool({
@@ -103,7 +103,7 @@ test('two alert dialogs', async ({ client, server }) => {
   });
 
   expect(result2).not.toHaveResponse({
-    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert 2"]: can be handled by the "browser_handle_dialog" tool`),
+    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert 2"]: can be handled by browser_handle_dialog`),
   });
 });
 
@@ -129,7 +129,7 @@ test('confirm dialog (true)', async ({ client, server }) => {
       ref: 'e2',
     },
   })).toHaveResponse({
-    modalState: expect.stringContaining(`- ["confirm" dialog with message "Confirm"]: can be handled by the "browser_handle_dialog" tool`),
+    modalState: expect.stringContaining(`- ["confirm" dialog with message "Confirm"]: can be handled by browser_handle_dialog`),
   });
 
   expect(await client.callTool({
@@ -164,7 +164,7 @@ test('confirm dialog (false)', async ({ client, server }) => {
       ref: 'e2',
     },
   })).toHaveResponse({
-    modalState: expect.stringContaining(`- ["confirm" dialog with message "Confirm"]: can be handled by the "browser_handle_dialog" tool`),
+    modalState: expect.stringContaining(`- ["confirm" dialog with message "Confirm"]: can be handled by browser_handle_dialog`),
   });
 
   expect(await client.callTool({
@@ -199,7 +199,7 @@ test('prompt dialog', async ({ client, server }) => {
       ref: 'e2',
     },
   })).toHaveResponse({
-    modalState: expect.stringContaining(`- ["prompt" dialog with message "Prompt"]: can be handled by the "browser_handle_dialog" tool`),
+    modalState: expect.stringContaining(`- ["prompt" dialog with message "Prompt"]: can be handled by browser_handle_dialog`),
   });
 
   const result = await client.callTool({
@@ -232,7 +232,7 @@ test('alert dialog w/ race', async ({ client, server }) => {
     },
   })).toHaveResponse({
     code: `await page.getByRole('button', { name: 'Button' }).click();`,
-    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert"]: can be handled by the "browser_handle_dialog" tool`),
+    modalState: expect.stringContaining(`- ["alert" dialog with message "Alert"]: can be handled by browser_handle_dialog`),
   });
 
   const result = await client.callTool({
diff --git a/tests/mcp/files.spec.ts b/tests/mcp/files.spec.ts
index 526ee9fac3c58..a41294ff6229e 100644
--- a/tests/mcp/files.spec.ts
+++ b/tests/mcp/files.spec.ts
@@ -52,7 +52,7 @@ test('browser_file_upload', async ({ client, server }, testInfo) => {
       ref: 'e2',
     },
   })).toHaveResponse({
-    modalState: expect.stringContaining(`- [File chooser]: can be handled by the "browser_file_upload" tool`),
+    modalState: expect.stringContaining(`- [File chooser]: can be handled by browser_file_upload`),
   });
 
   const filePath = testInfo.outputPath('test.txt');
@@ -82,7 +82,7 @@ test('browser_file_upload', async ({ client, server }, testInfo) => {
     });
 
     expect(response).toHaveResponse({
-      modalState: `- [File chooser]: can be handled by the "browser_file_upload" tool`,
+      modalState: `- [File chooser]: can be handled by browser_file_upload`,
     });
   }
 
@@ -98,7 +98,7 @@ test('browser_file_upload', async ({ client, server }, testInfo) => {
     expect(response).toHaveResponse({
       isError: true,
       error: `Error: Tool "browser_click" does not handle the modal state.`,
-      modalState: expect.stringContaining(`- [File chooser]: can be handled by the "browser_file_upload" tool`),
+      modalState: expect.stringContaining(`- [File chooser]: can be handled by browser_file_upload`),
     });
   }
 });
diff --git a/utils/build/build.js b/utils/build/build.js
index bcc5be51390fe..00802b7cbd12f 100644
--- a/utils/build/build.js
+++ b/utils/build/build.js
@@ -642,6 +642,12 @@ copyFiles.push({
   to: 'packages/playwright/lib',
 });
 
+copyFiles.push({
+  files: 'packages/playwright/src/mcp/terminal/*.md',
+  from: 'packages/playwright/src',
+  to: 'packages/playwright/lib',
+});
+
 if (watchMode) {
   // Run TypeScript for type checking.
   steps.push(new ProgramStep({

PATCH

echo "Patch applied successfully."
