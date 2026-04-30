#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "name: 'install-skills'" packages/playwright/src/mcp/terminal/commands.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
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
index d4f6b736af93b..6c7d7763db41e 100644
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
index bad843297ab6c..e70dc89350c79 100644
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
diff --git a/packages/playwright/src/skill/SKILL.md b/packages/playwright/src/skill/SKILL.md
index 6d94d12372626..de63c48ddae1a 100644
--- a/packages/playwright/src/skill/SKILL.md
+++ b/packages/playwright/src/skill/SKILL.md
@@ -125,6 +125,16 @@ playwright-cli sessionstorage-delete step
 playwright-cli sessionstorage-clear
 ```
 
+### Network
+
+```bash
+playwright-cli route "**/*.jpg" --status=404
+playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
+playwright-cli route-list
+playwright-cli unroute "**/*.jpg"
+playwright-cli unroute
+```
+
 ### DevTools
 
 ```bash
@@ -138,8 +148,23 @@ playwright-cli video-start
 playwright-cli video-stop video.webm
 ```
 
+### Install
+
+```bash
+playwright-cli install-browser
+playwright-cli install-skills
+```
+
 ### Configuration
 ```bash
+# Use specific browser when creating session
+playwright-cli open --browser=chrome
+playwright-cli open --browser=firefox
+playwright-cli open --browser=webkit
+playwright-cli open --browser=msedge
+# Connect to browser via extension
+playwright-cli open --extension
+
 # Configure the session
 playwright-cli config --config my-config.json
 playwright-cli config --headed --in-memory --browser=firefox
@@ -156,6 +181,7 @@ playwright-cli --session=mysession open example.com
 playwright-cli --session=mysession click e6
 playwright-cli session-list
 playwright-cli session-stop mysession
+playwright-cli session-restart mysession
 playwright-cli session-stop-all
 playwright-cli session-delete
 playwright-cli session-delete mysession
@@ -201,22 +227,6 @@ playwright-cli fill e7 "test"
 playwright-cli tracing-stop
 ```
 
-## Example: Authentication state reuse
-
-```bash
-# Login and save auth state
-playwright-cli open https://app.example.com/login
-playwright-cli snapshot
-playwright-cli fill e1 "user@example.com"
-playwright-cli fill e2 "password123"
-playwright-cli click e3
-playwright-cli state-save auth.json
-
-# Later, restore state and skip login
-playwright-cli state-load auth.json
-playwright-cli open https://app.example.com/dashboard
-```
-
 ## Specific tasks
 
 * **Request mocking** [references/request-mocking.md](references/request-mocking.md)
diff --git a/packages/playwright/src/skill/references/request-mocking.md b/packages/playwright/src/skill/references/request-mocking.md
index f6e25c342e292..9005fda67dfc4 100644
--- a/packages/playwright/src/skill/references/request-mocking.md
+++ b/packages/playwright/src/skill/references/request-mocking.md
@@ -1,452 +1,87 @@
 # Request Mocking
 
-Intercept, mock, modify, and block network requests using `page.route()`.
+Intercept, mock, modify, and block network requests.
 
-## Basic Syntax
+## CLI Route Commands
 
 ```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/endpoint', route => {
-    // Handle the route
-  });
-}"
-```
+# Mock with custom status
+playwright-cli route "**/*.jpg" --status=404
 
-## URL Patterns
+# Mock with JSON body
+playwright-cli route "**/api/users" --body='[{"id":1,"name":"Alice"}]' --content-type=application/json
 
-```
-**/api/users           - Exact path match
-**/api/*/details       - Wildcard in path
-**/*.{png,jpg,jpeg}    - Match file extensions
-**/search?q=*          - Match query parameters
-/\/api\/v\d+\/users/   - Regex pattern (passed as RegExp)
-```
+# Mock with custom headers
+playwright-cli route "**/api/data" --body='{"ok":true}' --header="X-Custom: value"
 
-## Mock API Responses
+# Remove headers from requests
+playwright-cli route "**/*" --remove-header=cookie,authorization
 
-### Return Static JSON
+# List active routes
+playwright-cli route-list
 
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/users', route => {
-    route.fulfill({
-      status: 200,
-      contentType: 'application/json',
-      body: JSON.stringify([
-        { id: 1, name: 'Alice' },
-        { id: 2, name: 'Bob' }
-      ])
-    });
-  });
-}"
+# Remove a route or all routes
+playwright-cli unroute "**/*.jpg"
+playwright-cli unroute
 ```
 
-### Return with Custom Headers
+## URL Patterns
 
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/data', route => {
-    route.fulfill({
-      status: 200,
-      headers: {
-        'Content-Type': 'application/json',
-        'X-Custom-Header': 'custom-value',
-        'Cache-Control': 'no-cache'
-      },
-      body: JSON.stringify({ success: true })
-    });
-  });
-}"
 ```
-
-### Return HTML
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/page.html', route => {
-    route.fulfill({
-      status: 200,
-      contentType: 'text/html',
-      body: '<html><body><h1>Mocked Page</h1></body></html>'
-    });
-  });
-}"
+**/api/users           - Exact path match
+**/api/*/details       - Wildcard in path
+**/*.{png,jpg,jpeg}    - Match file extensions
+**/search?q=*          - Match query parameters
 ```
 
-### Return Based on Request Data
+## Advanced Mocking with run-code
 
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/search', async route => {
-    const request = route.request();
-    const postData = request.postDataJSON();
+For conditional responses, request body inspection, response modification, or delays:
 
-    route.fulfill({
-      status: 200,
-      contentType: 'application/json',
-      body: JSON.stringify({
-        query: postData.query,
-        results: ['mock result 1', 'mock result 2']
-      })
-    });
-  });
-}"
-```
-
-## Modify Real Responses
-
-### Intercept and Transform
+### Conditional Response Based on Request
 
 ```bash
 playwright-cli run-code "async page => {
-  await page.route('**/api/products', async route => {
-    // Fetch the real response
-    const response = await route.fetch();
-    const json = await response.json();
-
-    // Modify it
-    json.products = json.products.map(p => ({
-      ...p,
-      price: 0,
-      discount: '100%'
-    }));
-
-    // Return modified response
-    await route.fulfill({ response, json });
+  await page.route('**/api/login', route => {
+    const body = route.request().postDataJSON();
+    if (body.username === 'admin') {
+      route.fulfill({ body: JSON.stringify({ token: 'mock-token' }) });
+    } else {
+      route.fulfill({ status: 401, body: JSON.stringify({ error: 'Invalid' }) });
+    }
   });
 }"
 ```
 
-### Add Fields to Response
+### Modify Real Response
 
 ```bash
 playwright-cli run-code "async page => {
-  await page.route('**/api/user/profile', async route => {
+  await page.route('**/api/user', async route => {
     const response = await route.fetch();
     const json = await response.json();
-
-    // Add mock fields
     json.isPremium = true;
-    json.credits = 9999;
-
     await route.fulfill({ response, json });
   });
 }"
 ```
 
-### Filter Response Data
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/items', async route => {
-    const response = await route.fetch();
-    const json = await response.json();
-
-    // Filter to only active items
-    json.items = json.items.filter(item => item.active);
-
-    await route.fulfill({ response, json });
-  });
-}"
-```
-
-## Modify Request Headers
-
-### Add Authorization
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/**', async route => {
-    const headers = {
-      ...route.request().headers(),
-      'Authorization': 'Bearer my-secret-token'
-    };
-    await route.continue({ headers });
-  });
-}"
-```
-
-### Add Custom Headers
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/*', async route => {
-    const headers = {
-      ...route.request().headers(),
-      'X-Test-Mode': 'true',
-      'X-Request-Id': Date.now().toString()
-    };
-    await route.continue({ headers });
-  });
-}"
-```
-
-### Remove Headers
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/*', async route => {
-    const headers = { ...route.request().headers() };
-    delete headers['cookie'];
-    delete headers['authorization'];
-    await route.continue({ headers });
-  });
-}"
-```
-
-## Block Requests
-
-### Block by URL Pattern
-
-```bash
-# Block images
-playwright-cli run-code "async page => {
-  await page.route('**/*.{png,jpg,jpeg,gif,webp,svg}', route => route.abort());
-}"
-
-# Block fonts
-playwright-cli run-code "async page => {
-  await page.route('**/*.{woff,woff2,ttf,otf}', route => route.abort());
-}"
-
-# Block CSS
-playwright-cli run-code "async page => {
-  await page.route('**/*.css', route => route.abort());
-}"
-```
-
-### Block Third-Party Scripts
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/*google-analytics*/**', route => route.abort());
-  await page.route('**/*googletagmanager*/**', route => route.abort());
-  await page.route('**/*facebook*/**', route => route.abort());
-  await page.route('**/*hotjar*/**', route => route.abort());
-  await page.route('**/*intercom*/**', route => route.abort());
-}"
-```
-
-### Block All External Requests
-
-```bash
-playwright-cli run-code "async page => {
-  const allowedDomain = 'example.com';
-  await page.route('**/*', route => {
-    const url = new URL(route.request().url());
-    if (url.hostname.includes(allowedDomain)) {
-      route.continue();
-    } else {
-      route.abort();
-    }
-  });
-}"
-```
-
-## Simulate Errors
-
-### HTTP Error Codes
+### Simulate Network Failures
 
 ```bash
-# 404 Not Found
-playwright-cli run-code "async page => {
-  await page.route('**/api/missing', route => {
-    route.fulfill({ status: 404, body: 'Not Found' });
-  });
-}"
-
-# 500 Internal Server Error
-playwright-cli run-code "async page => {
-  await page.route('**/api/broken', route => {
-    route.fulfill({
-      status: 500,
-      contentType: 'application/json',
-      body: JSON.stringify({ error: 'Internal Server Error' })
-    });
-  });
-}"
-
-# 401 Unauthorized
-playwright-cli run-code "async page => {
-  await page.route('**/api/protected', route => {
-    route.fulfill({
-      status: 401,
-      body: JSON.stringify({ error: 'Unauthorized' })
-    });
-  });
-}"
-
-# 429 Rate Limited
-playwright-cli run-code "async page => {
-  await page.route('**/api/limited', route => {
-    route.fulfill({
-      status: 429,
-      headers: { 'Retry-After': '60' },
-      body: JSON.stringify({ error: 'Too Many Requests' })
-    });
-  });
-}"
-```
-
-### Network Failures
-
-```bash
-# Connection refused
-playwright-cli run-code "async page => {
-  await page.route('**/api/unreachable', route => route.abort('connectionrefused'));
-}"
-
-# Timeout
-playwright-cli run-code "async page => {
-  await page.route('**/api/slow', route => route.abort('timedout'));
-}"
-
-# Connection reset
-playwright-cli run-code "async page => {
-  await page.route('**/api/reset', route => route.abort('connectionreset'));
-}"
-
-# Internet disconnected
 playwright-cli run-code "async page => {
   await page.route('**/api/offline', route => route.abort('internetdisconnected'));
 }"
+# Options: connectionrefused, timedout, connectionreset, internetdisconnected
 ```
 
-## Delayed Responses
+### Delayed Response
 
 ```bash
-# Simulate slow API
 playwright-cli run-code "async page => {
-  await page.route('**/api/slow-endpoint', async route => {
-    await new Promise(r => setTimeout(r, 3000)); // 3 second delay
-    route.fulfill({
-      status: 200,
-      body: JSON.stringify({ data: 'finally loaded' })
-    });
+  await page.route('**/api/slow', async route => {
+    await new Promise(r => setTimeout(r, 3000));
+    route.fulfill({ body: JSON.stringify({ data: 'loaded' }) });
   });
 }"
 ```
-
-## Conditional Mocking
-
-### Based on Request Method
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/resource', route => {
-    const method = route.request().method();
-
-    if (method === 'GET') {
-      route.fulfill({
-        body: JSON.stringify({ items: [] })
-      });
-    } else if (method === 'POST') {
-      route.fulfill({
-        status: 201,
-        body: JSON.stringify({ id: 123, created: true })
-      });
-    } else if (method === 'DELETE') {
-      route.fulfill({ status: 204 });
-    } else {
-      route.continue();
-    }
-  });
-}"
-```
-
-### Based on Request Body
-
-```bash
-playwright-cli run-code "async page => {
-  await page.route('**/api/login', route => {
-    const body = route.request().postDataJSON();
-
-    if (body.username === 'admin' && body.password === 'secret') {
-      route.fulfill({
-        body: JSON.stringify({ token: 'mock-jwt-token' })
-      });
-    } else {
-      route.fulfill({
-        status: 401,
-        body: JSON.stringify({ error: 'Invalid credentials' })
-      });
-    }
-  });
-}"
-```
-
-## Remove Routes
-
-```bash
-# Remove specific route
-playwright-cli run-code "async page => {
-  const handler = route => route.abort();
-  await page.route('**/api/blocked', handler);
-
-  // Later, remove the route
-  await page.unroute('**/api/blocked', handler);
-}"
-
-# Remove all routes for a pattern
-playwright-cli run-code "async page => {
-  await page.unroute('**/api/**');
-}"
-```
-
-## Logging Requests
-
-```bash
-# Log all requests and responses
-playwright-cli run-code "async page => {
-  page.on('request', request => {
-    console.log('>>', request.method(), request.url());
-  });
-  page.on('response', response => {
-    console.log('<<', response.status(), response.url());
-  });
-}"
-
-# Log only failed requests
-playwright-cli run-code "async page => {
-  page.on('requestfailed', request => {
-    console.log('FAILED:', request.url(), request.failure().errorText);
-  });
-}"
-```
-
-## Wait for Requests
-
-```bash
-# Wait for specific request after action
-playwright-cli run-code "async page => {
-  const [response] = await Promise.all([
-    page.waitForResponse('**/api/submit'),
-    page.click('button[type=submit]')
-  ]);
-  return { status: response.status(), ok: response.ok() };
-}"
-
-# Wait for request with custom condition
-playwright-cli run-code "async page => {
-  const response = await page.waitForResponse(
-    response => response.url().includes('/api/') && response.status() === 200
-  );
-  return await response.json();
-}"
-```
-
-## HAR File Mocking
-
-```bash
-# Record network to HAR
-playwright-cli run-code "async page => {
-  await page.routeFromHAR('network.har', { update: true });
-  // Navigate and interact - requests are recorded
-}"
-
-# Replay from HAR
-playwright-cli run-code "async page => {
-  await page.routeFromHAR('network.har');
-  // Requests matching HAR entries return recorded responses
-}"
-```

PATCH

echo "Patch applied successfully."
