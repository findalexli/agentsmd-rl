#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'requestBody.*z\.boolean' packages/playwright-core/src/tools/backend/network.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
new file mode 100644
index 0000000000000..231189577e90c
--- /dev/null
+++ b/.github/copilot-instructions.md
@@ -0,0 +1,9 @@
+## PR Review Guidelines
+
+When reviewing pull requests:
+
+- Only comment on semantically meaningful issues: bugs, incorrect logic, security problems, or API contract violations.
+- Skip style, formatting, naming, and whitespace observations unless they cause functional problems.
+- Keep each comment short — one or two sentences maximum.
+- Do not write long descriptions or summaries of what the code does.
+- Do not suggest refactors or improvements unrelated to the PR's stated goal.
diff --git a/packages/playwright-core/src/tools/backend/network.ts b/packages/playwright-core/src/tools/backend/network.ts
index 2e3040528678e..4097422b63357 100644
--- a/packages/playwright-core/src/tools/backend/network.ts
+++ b/packages/playwright-core/src/tools/backend/network.ts
@@ -27,7 +27,10 @@ const requests = defineTabTool({
     title: 'List network requests',
     description: 'Returns all network requests since loading the page',
     inputSchema: z.object({
-      includeStatic: z.boolean().default(false).describe('Whether to include successful static resources like images, fonts, scripts, etc. Defaults to false.'),
+      static: z.boolean().default(false).describe('Whether to include successful static resources like images, fonts, scripts, etc. Defaults to false.'),
+      requestBody: z.boolean().default(false).describe('Whether to include request body. Defaults to false.'),
+      requestHeaders: z.boolean().default(false).describe('Whether to include request headers. Defaults to false.'),
+      filter: z.string().optional().describe('Only return requests whose URL matches this regexp (e.g. "/api/.*user").'),
       filename: z.string().optional().describe('Filename to save the network requests to. If not provided, requests are returned as text.'),
     }),
     type: 'readOnly',
@@ -35,11 +38,17 @@ const requests = defineTabTool({

   handle: async (tab, params, response) => {
     const requests = await tab.requests();
+    const filter = params.filter ? new RegExp(params.filter) : undefined;
     const text: string[] = [];
     for (const request of requests) {
-      if (!params.includeStatic && !isFetch(request) && isSuccessfulResponse(request))
+      if (!params.static && !isFetch(request) && isSuccessfulResponse(request))
         continue;
-      text.push(await renderRequest(request));
+      if (filter) {
+        filter.lastIndex = 0;
+        if (!filter.test(request.url()))
+          continue;
+      }
+      text.push(await renderRequest(request, params.requestBody, params.requestHeaders));
     }
     await response.addResult('Network', text.join('\n'), { prefix: 'network', ext: 'log', suggestedFilename: params.filename });
   },
@@ -71,16 +80,27 @@ export function isFetch(request: playwright.Request): boolean {
   return ['fetch', 'xhr'].includes(request.resourceType());
 }

-export async function renderRequest(request: playwright.Request): Promise<string> {
+export async function renderRequest(request: playwright.Request, includeBody = false, includeHeaders = false): Promise<string> {
   const response = request.existingResponse();

   const result: string[] = [];
   result.push(`[${request.method().toUpperCase()}] ${request.url()}`);
   if (response)
-    result.push(`=> [${response.status()}] ${response.statusText()}`);
+    result.push(` => [${response.status()}] ${response.statusText()}`);
   else if (request.failure())
-    result.push(`=> [FAILED] ${request.failure()?.errorText ?? 'Unknown error'}`);
-  return result.join(' ');
+    result.push(` => [FAILED] ${request.failure()?.errorText ?? 'Unknown error'}`);
+  if (includeHeaders) {
+    const headers = request.headers();
+    const headerLines = Object.entries(headers).map(([k, v]) => `    ${k}: ${v}`).join('\n');
+    if (headerLines)
+      result.push(`\n  Request headers:\n${headerLines}`);
+  }
+  if (includeBody) {
+    const postData = request.postData();
+    if (postData)
+      result.push(`\n  Request body: ${postData}`);
+  }
+  return result.join('');
 }

 const networkStateSet = defineTool({
diff --git a/packages/playwright-core/src/tools/cli-daemon/commands.ts b/packages/playwright-core/src/tools/cli-daemon/commands.ts
index 98e691f02f579..f410a7856090e 100644
--- a/packages/playwright-core/src/tools/cli-daemon/commands.ts
+++ b/packages/playwright-core/src/tools/cli-daemon/commands.ts
@@ -743,10 +743,13 @@ const networkRequests = declareCommand({
   args: z.object({}),
   options: z.object({
     static: z.boolean().optional().describe('Whether to include successful static resources like images, fonts, scripts, etc. Defaults to false.'),
+    ['request-body']: z.boolean().optional().describe('Whether to include request body. Defaults to false.'),
+    ['request-headers']: z.boolean().optional().describe('Whether to include request headers. Defaults to false.'),
+    filter: z.string().optional().describe('Only return requests whose URL matches this regexp (e.g. "/api/.*user").'),
     clear: z.boolean().optional().describe('Whether to clear the network list'),
   }),
   toolName: ({ clear }) => clear ? 'browser_network_clear' : 'browser_network_requests',
-  toolParams: ({ static: includeStatic, clear }) => clear ? ({}) : ({ includeStatic }),
+  toolParams: ({ static: s, 'request-body': requestBody, 'request-headers': requestHeaders, filter, clear }) => clear ? ({}) : ({ static: s, requestBody, requestHeaders, filter }),
 });

 const tracingStart = declareCommand({

PATCH

echo "Patch applied successfully."
