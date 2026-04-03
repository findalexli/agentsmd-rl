#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'function asRef' packages/playwright-core/src/cli/daemon/commands.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright-core/src/cli/daemon/commands.ts b/packages/playwright-core/src/cli/daemon/commands.ts
index 42f256e8f8cab..d5c25bf7b07b7 100644
--- a/packages/playwright-core/src/cli/daemon/commands.ts
+++ b/packages/playwright-core/src/cli/daemon/commands.ts
@@ -31,6 +31,14 @@ const numberArg = z.preprocess((val, ctx) => {
   return number;
 }, z.number());

+function asRef(refOrSelector: string | undefined): { ref?: string, selector?: string } {
+  if (refOrSelector === undefined)
+    return {};
+  if (refOrSelector.match(/^(f\d+)?e\d+$/))
+    return { ref: refOrSelector };
+  return { ref: '', selector: refOrSelector };
+}
+
 // Navigation commands

 const open = declareCommand({
@@ -204,14 +212,14 @@ const click = declareCommand({
   description: 'Perform click on a web page',
   category: 'core',
   args: z.object({
-    ref: z.string().describe('Exact target element reference from the page snapshot'),
+    target: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
     button: z.string().optional().describe('Button to click, defaults to left'),
   }),
   options: z.object({
     modifiers: z.array(z.string()).optional().describe('Modifier keys to press'),
   }),
   toolName: 'browser_click',
-  toolParams: ({ ref, button, modifiers }) => ({ ref, button, modifiers }),
+  toolParams: ({ target, button, modifiers }) => ({ ...asRef(target), button, modifiers }),
 });

 const doubleClick = declareCommand({
@@ -219,14 +227,14 @@ const doubleClick = declareCommand({
   description: 'Perform double click on a web page',
   category: 'core',
   args: z.object({
-    ref: z.string().describe('Exact target element reference from the page snapshot'),
+    target: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
     button: z.string().optional().describe('Button to click, defaults to left'),
   }),
   options: z.object({
     modifiers: z.array(z.string()).optional().describe('Modifier keys to press'),
   }),
   toolName: 'browser_click',
-  toolParams: ({ ref, button, modifiers }) => ({ ref, button, modifiers, doubleClick: true }),
+  toolParams: ({ target, button, modifiers }) => ({ ...asRef(target), button, modifiers, doubleClick: true }),
 });

 const drag = declareCommand({
@@ -234,11 +242,15 @@ const drag = declareCommand({
   description: 'Perform drag and drop between two elements',
   category: 'core',
   args: z.object({
-    startRef: z.string().describe('Exact source element reference from the page snapshot'),
-    endRef: z.string().describe('Exact target element reference from the page snapshot'),
+    startElement: z.string().describe('Exact source element reference from the page snapshot, or a unique element selector'),
+    endElement: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
   }),
   toolName: 'browser_drag',
-  toolParams: ({ startRef, endRef }) => ({ startRef, endRef }),
+  toolParams: ({ startElement, endElement }) => {
+    const start = asRef(startElement);
+    const end = asRef(endElement);
+    return { startRef: start.ref, startSelector: start.selector, endRef: end.ref, endSelector: end.selector };
+  },
 });

 const fill = declareCommand({
@@ -246,14 +258,14 @@ const fill = declareCommand({
   description: 'Fill text into editable element',
   category: 'core',
   args: z.object({
-    ref: z.string().describe('Exact target element reference from the page snapshot'),
+    target: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
     text: z.string().describe('Text to fill into the element'),
   }),
   options: z.object({
     submit: z.boolean().optional().describe('Whether to submit entered text (press Enter after)'),
   }),
   toolName: 'browser_type',
-  toolParams: ({ ref, text, submit }) => ({ ref, text, submit }),
+  toolParams: ({ target, text, submit }) => ({ ...asRef(target), text, submit }),
 });

 const hover = declareCommand({
@@ -261,10 +273,10 @@ const hover = declareCommand({
   description: 'Hover over element on page',
   category: 'core',
   args: z.object({
-    ref: z.string().describe('Exact target element reference from the page snapshot'),
+    target: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
   }),
   toolName: 'browser_hover',
-  toolParams: ({ ref }) => ({ ref }),
+  toolParams: ({ target }) => ({ ...asRef(target) }),
 });

 const select = declareCommand({
@@ -272,11 +284,11 @@ const select = declareCommand({
   description: 'Select an option in a dropdown',
   category: 'core',
   args: z.object({
-    ref: z.string().describe('Exact target element reference from the page snapshot'),
+    target: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
     val: z.string().describe('Value to select in the dropdown'),
   }),
   toolName: 'browser_select_option',
-  toolParams: ({ ref, val: value }) => ({ ref, values: [value] }),
+  toolParams: ({ target, val: value }) => ({ ...asRef(target), values: [value] }),
 });

 const fileUpload = declareCommand({
@@ -295,10 +307,10 @@ const check = declareCommand({
   description: 'Check a checkbox or radio button',
   category: 'core',
   args: z.object({
-    ref: z.string().describe('Exact target element reference from the page snapshot'),
+    target: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
   }),
   toolName: 'browser_check',
-  toolParams: ({ ref }) => ({ ref }),
+  toolParams: ({ target }) => ({ ...asRef(target) }),
 });

 const uncheck = declareCommand({
@@ -306,10 +318,10 @@ const uncheck = declareCommand({
   description: 'Uncheck a checkbox or radio button',
   category: 'core',
   args: z.object({
-    ref: z.string().describe('Exact target element reference from the page snapshot'),
+    target: z.string().describe('Exact target element reference from the page snapshot, or a unique element selector'),
   }),
   toolName: 'browser_uncheck',
-  toolParams: ({ ref }) => ({ ref }),
+  toolParams: ({ target }) => ({ ...asRef(target) }),
 });

 const snapshot = declareCommand({
@@ -330,10 +342,10 @@ const evaluate = declareCommand({
   category: 'core',
   args: z.object({
     func: z.string().describe('() => { /* code */ } or (element) => { /* code */ } when element is provided'),
-    ref: z.string().optional().describe('Exact target element reference from the page snapshot'),
+    element: z.string().optional().describe('Exact target element reference from the page snapshot, or a unique element selector'),
   }),
   toolName: 'browser_evaluate',
-  toolParams: ({ func, ref }) => ({ function: func, ref }),
+  toolParams: ({ func, element }) => ({ function: func, ...asRef(element) }),
 });

 const dialogAccept = declareCommand({
@@ -686,14 +698,14 @@ const screenshot = declareCommand({
   description: 'screenshot of the current page or element',
   category: 'export',
   args: z.object({
-    ref: z.string().optional().describe('Exact target element reference from the page snapshot.'),
+    target: z.string().optional().describe('Exact target element reference from the page snapshot, or a unique element selector.'),
   }),
   options: z.object({
     filename: z.string().optional().describe('File name to save the screenshot to. Defaults to `page-{timestamp}.{png|jpeg}` if not specified.'),
     ['full-page']: z.boolean().optional().describe('When true, takes a screenshot of the full scrollable page, instead of the currently visible viewport.'),
   }),
   toolName: 'browser_take_screenshot',
-  toolParams: ({ ref, filename, ['full-page']: fullPage }) => ({ filename, ref, fullPage }),
+  toolParams: ({ target, filename, ['full-page']: fullPage }) => ({ filename, ...asRef(target), fullPage }),
 });

 const pdfSave = declareCommand({
diff --git a/packages/playwright-core/src/skill/SKILL.md b/packages/playwright-core/src/skill/SKILL.md
index 58dee97c43c9c..4865d3337e43d 100644
--- a/packages/playwright-core/src/skill/SKILL.md
+++ b/packages/playwright-core/src/skill/SKILL.md
@@ -196,6 +196,31 @@ You can also take a snapshot on demand using `playwright-cli snapshot` command.

 If `--filename` is not provided, a new snapshot file is created with a timestamp. Default to automatic file naming, use `--filename=` when artifact is a part of the workflow result.

+## Targeting elements
+
+By default, use refs from the snapshot to interact with page elements.
+
+```bash
+# get snapshot with refs
+playwright-cli snapshot
+
+# interact using a ref
+playwright-cli click e15
+```
+
+You can also use css or role selectors, for example when explicitly asked for it.
+
+```bash
+# css selector
+playwright-cli click "#main > button.submit"
+
+# role selector
+playwright-cli click "role=button[name=Submit]"
+
+# chaining css and role selectors
+playwright-cli click "#footer >> role=button[name=Submit]"
+```
+
 ## Browser Sessions

 ```bash
diff --git a/packages/playwright-core/src/tools/evaluate.ts b/packages/playwright-core/src/tools/evaluate.ts
index e71817a986638..b90a5a9316c1a 100644
--- a/packages/playwright-core/src/tools/evaluate.ts
+++ b/packages/playwright-core/src/tools/evaluate.ts
@@ -25,6 +25,7 @@ const evaluateSchema = z.object({
   function: z.string().describe('() => { /* code */ } or (element) => { /* code */ } when element is provided'),
   element: z.string().optional().describe('Human-readable element description used to obtain permission to interact with the element'),
   ref: z.string().optional().describe('Exact target element reference from the page snapshot'),
+  selector: z.string().optional().describe('CSS or role selector for the target element, when "ref" is not available.'),
 });

 const evaluate = defineTabTool({
@@ -42,7 +43,7 @@ const evaluate = defineTabTool({
     if (!params.function.includes('=>'))
       params.function = `() => (${params.function})`;
     if (params.ref) {
-      locator = await tab.refLocator({ ref: params.ref, element: params.element || 'element' });
+      locator = await tab.refLocator({ ref: params.ref, selector: params.selector, element: params.element || 'element' });
       response.addCode(`await page.${locator.resolved}.evaluate(${escapeWithQuotes(params.function)});`);
     } else {
       response.addCode(`await page.evaluate(${escapeWithQuotes(params.function)});`);
diff --git a/packages/playwright-core/src/tools/form.ts b/packages/playwright-core/src/tools/form.ts
index 6d2f536660b2c..88999d5c1a391 100644
--- a/packages/playwright-core/src/tools/form.ts
+++ b/packages/playwright-core/src/tools/form.ts
@@ -31,6 +31,7 @@ const fillForm = defineTabTool({
         name: z.string().describe('Human-readable field name'),
         type: z.enum(['textbox', 'checkbox', 'radio', 'combobox', 'slider']).describe('Type of the field'),
         ref: z.string().describe('Exact target field reference from the page snapshot'),
+        selector: z.string().optional().describe('CSS or role selector for the field element, when "ref" is not available. Either "selector" or "ref" is required.'),
         value: z.string().describe('Value to fill in the field. If the field is a checkbox, the value should be `true` or `false`. If the field is a combobox, the value should be the text of the option.'),
       })).describe('Fields to fill in'),
     }),
@@ -39,7 +40,7 @@ const fillForm = defineTabTool({

   handle: async (tab, params, response) => {
     for (const field of params.fields) {
-      const { locator, resolved } = await tab.refLocator({ element: field.name, ref: field.ref });
+      const { locator, resolved } = await tab.refLocator({ element: field.name, ref: field.ref, selector: field.selector });
       const locatorSource = `await page.${resolved}`;
       if (field.type === 'textbox' || field.type === 'slider') {
         const secret = tab.context.lookupSecret(field.value);
diff --git a/packages/playwright-core/src/tools/screenshot.ts b/packages/playwright-core/src/tools/screenshot.ts
index a940cb62f1689..05a073eb8a669 100644
--- a/packages/playwright-core/src/tools/screenshot.ts
+++ b/packages/playwright-core/src/tools/screenshot.ts
@@ -28,6 +28,7 @@ const screenshotSchema = z.object({
   filename: z.string().optional().describe('File name to save the screenshot to. Defaults to `page-{timestamp}.{png|jpeg}` if not specified. Prefer relative file names to stay within the output directory.'),
   element: z.string().optional().describe('Human-readable element description used to obtain permission to screenshot the element. If not provided, the screenshot will be taken of viewport. If element is provided, ref must be provided too.'),
   ref: z.string().optional().describe('Exact target element reference from the page snapshot. If not provided, the screenshot will be taken of viewport. If ref is provided, element must be provided too.'),
+  selector: z.string().optional().describe('CSS or role selector for the target element, when "ref" is not available.'),
   fullPage: z.boolean().optional().describe('When true, takes a screenshot of the full scrollable page, instead of the currently visible viewport. Cannot be used with element screenshots.'),
 });

@@ -55,7 +56,7 @@ const screenshot = defineTabTool({
     };

     const screenshotTarget = params.ref ? params.element || 'element' : (params.fullPage ? 'full page' : 'viewport');
-    const ref = params.ref ? await tab.refLocator({ element: params.element || '', ref: params.ref }) : null;
+    const ref = (params.ref || params.selector) ? await tab.refLocator({ element: params.element || '', ref: params.ref || '', selector: params.selector }) : null;
     const data = ref ? await ref.locator.screenshot(options) : await tab.page.screenshot(options);

     const resolvedFile = await response.resolveClientFile({ prefix: ref ? 'element' : 'page', ext: fileType, suggestedFilename: params.filename }, `Screenshot of ${screenshotTarget}`);
diff --git a/packages/playwright-core/src/tools/snapshot.ts b/packages/playwright-core/src/tools/snapshot.ts
index 6053505c23597..39dc76b10f163 100644
--- a/packages/playwright-core/src/tools/snapshot.ts
+++ b/packages/playwright-core/src/tools/snapshot.ts
@@ -40,6 +40,7 @@ const snapshot = defineTool({
 export const elementSchema = z.object({
   element: z.string().optional().describe('Human-readable element description used to obtain permission to interact with the element'),
   ref: z.string().describe('Exact target element reference from the page snapshot'),
+  selector: z.string().optional().describe('CSS or role selector for the target element, when "ref" is not available'),
 });

 const clickSchema = elementSchema.extend({
@@ -92,8 +93,10 @@ const drag = defineTabTool({
     inputSchema: z.object({
       startElement: z.string().describe('Human-readable source element description used to obtain the permission to interact with the element'),
       startRef: z.string().describe('Exact source element reference from the page snapshot'),
+      startSelector: z.string().optional().describe('CSS or role selector for the source element, when ref is not available'),
       endElement: z.string().describe('Human-readable target element description used to obtain the permission to interact with the element'),
       endRef: z.string().describe('Exact target element reference from the page snapshot'),
+      endSelector: z.string().optional().describe('CSS or role selector for the target element, when ref is not available'),
     }),
     type: 'input',
   },
@@ -102,8 +105,8 @@ const drag = defineTabTool({
     response.setIncludeSnapshot();

     const [start, end] = await tab.refLocators([
-      { ref: params.startRef, element: params.startElement },
-      { ref: params.endRef, element: params.endElement },
+      { ref: params.startRef, selector: params.startSelector, element: params.startElement },
+      { ref: params.endRef, selector: params.endSelector, element: params.endElement },
     ]);

     await tab.waitForCompletion(async () => {
diff --git a/packages/playwright-core/src/tools/tab.ts b/packages/playwright-core/src/tools/tab.ts
index 7ecb8981b17a1..ef5100eb63e3b 100644
--- a/packages/playwright-core/src/tools/tab.ts
+++ b/packages/playwright-core/src/tools/tab.ts
@@ -430,22 +430,32 @@ export class Tab extends EventEmitter<TabEventsInterface> {
     await this._raceAgainstModalStates(() => waitForCompletion(this, callback));
   }

-  async refLocator(params: { element?: string, ref: string }): Promise<{ locator: Locator, resolved: string }> {
+  async refLocator(params: { element?: string, ref: string, selector?: string }): Promise<{ locator: Locator, resolved: string }> {
     await this._initializedPromise;
     return (await this.refLocators([params]))[0];
   }

-  async refLocators(params: { element?: string, ref: string }[]): Promise<{ locator: Locator, resolved: string }[]> {
+  async refLocators(params: { element?: string, ref: string, selector?: string }[]): Promise<{ locator: Locator, resolved: string }[]> {
     await this._initializedPromise;
     return Promise.all(params.map(async param => {
-      try {
-        let locator = this.page.locator(`aria-ref=${param.ref}`);
-        if (param.element)
-          locator = locator.describe(param.element);
-        const { resolvedSelector } = await locator._resolveSelector();
-        return { locator, resolved: asLocator('javascript', resolvedSelector) };
-      } catch (e) {
-        throw new Error(`Ref ${param.ref} not found in the current page snapshot. Try capturing new snapshot.`);
+      if (param.selector) {
+        const locator = this.page.locator(param.selector);
+        try {
+          await locator._resolveSelector();
+        } catch {
+          throw new Error(`Selector ${param.selector} does not match any elements.`);
+        }
+        return { locator, resolved: asLocator('javascript', param.selector) };
+      } else {
+        try {
+          let locator = this.page.locator(`aria-ref=${param.ref}`);
+          if (param.element)
+            locator = locator.describe(param.element);
+          const { resolvedSelector } = await locator._resolveSelector();
+          return { locator, resolved: asLocator('javascript', resolvedSelector) };
+        } catch (e) {
+          throw new Error(`Ref ${param.ref} not found in the current page snapshot. Try capturing new snapshot.`);
+        }
       }
     }));
   }
diff --git a/packages/playwright-core/src/tools/tools.ts b/packages/playwright-core/src/tools/tools.ts
index ea7c4e5bd10f1..9ad0aebef7bb3 100644
--- a/packages/playwright-core/src/tools/tools.ts
+++ b/packages/playwright-core/src/tools/tools.ts
@@ -14,6 +14,8 @@
  * limitations under the License.
  */

+import { z } from '../mcpBundle';
+
 import common from './common';
 import config from './config';
 import console from './console';
@@ -72,5 +74,14 @@ export const browserTools: Tool<any>[] = [
 ];

 export function filteredTools(config: Pick<ContextConfig, 'capabilities'>) {
-  return browserTools.filter(tool => tool.capability.startsWith('core') || config.capabilities?.includes(tool.capability)).filter(tool => !tool.skillOnly);
+  return browserTools.filter(tool => tool.capability.startsWith('core') || config.capabilities?.includes(tool.capability)).filter(tool => !tool.skillOnly).map(tool => ({
+    ...tool,
+    schema: {
+      ...tool.schema,
+      // Note: we first ensure that "selector" property is present, so that we can omit() it without an error.
+      inputSchema: tool.schema.inputSchema
+          .extend({ selector: z.string(), startSelector: z.string(), endSelector: z.string() })
+          .omit({ selector: true, startSelector: true, endSelector: true }),
+    },
+  }));
 }
diff --git a/packages/playwright-core/src/tools/verify.ts b/packages/playwright-core/src/tools/verify.ts
index 495d3ed9858ae..bb5ff8e8255df 100644
--- a/packages/playwright-core/src/tools/verify.ts
+++ b/packages/playwright-core/src/tools/verify.ts
@@ -81,13 +81,14 @@ const verifyList = defineTabTool({
     inputSchema: z.object({
       element: z.string().describe('Human-readable list description'),
       ref: z.string().describe('Exact target element reference that points to the list'),
+      selector: z.string().optional().describe('CSS or role selector for the target list, when "ref" is not available.'),
       items: z.array(z.string()).describe('Items to verify'),
     }),
     type: 'assertion',
   },

   handle: async (tab, params, response) => {
-    const { locator } = await tab.refLocator({ ref: params.ref, element: params.element });
+    const { locator } = await tab.refLocator({ ref: params.ref, selector: params.selector, element: params.element });
     const itemTexts: string[] = [];
     for (const item of params.items) {
       const itemLocator = locator.getByText(item);
@@ -115,14 +116,15 @@ const verifyValue = defineTabTool({
     inputSchema: z.object({
       type: z.enum(['textbox', 'checkbox', 'radio', 'combobox', 'slider']).describe('Type of the element'),
       element: z.string().describe('Human-readable element description'),
-      ref: z.string().describe('Exact target element reference that points to the element'),
+      ref: z.string().describe('Exact target element reference from the page snapshot'),
+      selector: z.string().optional().describe('CSS or role selector for the target element, when "ref" is not available'),
       value: z.string().describe('Value to verify. For checkbox, use "true" or "false".'),
     }),
     type: 'assertion',
   },

   handle: async (tab, params, response) => {
-    const { locator, resolved } = await tab.refLocator({ ref: params.ref, element: params.element });
+    const { locator, resolved } = await tab.refLocator({ ref: params.ref, selector: params.selector, element: params.element });
     const locatorSource = `page.${resolved}`;
     if (params.type === 'textbox' || params.type === 'slider' || params.type === 'combobox') {
       const value = await locator.inputValue(tab.expectTimeoutOptions);

PATCH

echo "Patch applied successfully."
