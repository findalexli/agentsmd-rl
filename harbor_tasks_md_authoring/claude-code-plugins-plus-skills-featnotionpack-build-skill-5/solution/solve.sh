#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "**Fix:** Retry with exponential backoff. If persistent (>5 minutes), check [stat" "plugins/saas-packs/notion-pack/skills/notion-common-errors/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/notion-pack/skills/notion-common-errors/SKILL.md b/plugins/saas-packs/notion-pack/skills/notion-common-errors/SKILL.md
@@ -1,9 +1,9 @@
 ---
 name: notion-common-errors
 description: |
-  Diagnose and fix common Notion API errors and exceptions.
+  Diagnose and fix Notion API errors by HTTP status code and error code.
   Use when encountering Notion errors, debugging failed requests,
-  or troubleshooting integration issues.
+  or troubleshooting integration access, rate limiting, or validation issues.
   Trigger with phrases like "notion error", "fix notion",
   "notion not working", "debug notion", "notion 400", "notion 429".
 allowed-tools: Read, Grep, Bash(curl:*)
@@ -17,17 +17,9 @@ compatible-with: claude-code
 # Notion Common Errors
 
 ## Overview
-Quick reference for Notion API error codes, their causes, and solutions. All errors return a JSON body with `status`, `code`, and `message` fields.
 
-## Prerequisites
-- `@notionhq/client` installed
-- `NOTION_TOKEN` configured
-- Access to application logs
-
-## Instructions
+Quick reference for all Notion API error codes with exact HTTP statuses, error bodies, and fixes. The API returns errors as JSON with three fields:
 
-### Step 1: Identify the Error Code
-Notion API errors follow a consistent structure:
 ```json
 {
   "object": "error",
@@ -37,16 +29,34 @@ Notion API errors follow a consistent structure:
 }
 ```
 
-### Step 2: Match Error and Apply Fix
+All requests require `Authorization: Bearer <token>` and `Notion-Version: 2022-06-28` headers.
+
+## Prerequisites
+
+- `@notionhq/client` installed (`npm install @notionhq/client`)
+- `NOTION_TOKEN` environment variable set (internal integration token starting with `ntn_` or `secret_`)
+- Target pages/databases shared with the integration via the Connections menu
+
+## Instructions
+
+### Step 1: Identify the Error
+
+Run the diagnostic script below or check your application logs. Match the HTTP status and `code` field to the sections that follow.
+
+### Step 2: Match Error Code and Apply Fix
 
 ---
 
 ### 401 — `unauthorized`
-**Message:** `API token is invalid.`
 
-**Cause:** Token is missing, malformed, or revoked.
+```json
+{"object": "error", "status": 401, "code": "unauthorized", "message": "API token is invalid."}
+```
+
+**Cause:** Token is missing, malformed, expired, or revoked.
+
+**Fix:**
 
-**Solution:**
 ```bash
 # Verify token is set
 echo ${NOTION_TOKEN:+SET}
@@ -56,98 +66,115 @@ curl -s https://api.notion.com/v1/users/me \
   -H "Authorization: Bearer ${NOTION_TOKEN}" \
   -H "Notion-Version: 2022-06-28" | jq .
 ```
-Regenerate at https://www.notion.so/my-integrations if needed.
+
+If the response shows your integration bot user, the token is valid. Otherwise regenerate at [notion.so/my-integrations](https://www.notion.so/my-integrations). Tokens starting with `secret_` are legacy format — new integrations use `ntn_` prefix.
 
 ---
 
 ### 403 — `restricted_resource`
-**Message:** `Insufficient permissions for this resource.`
 
-**Cause:** Integration lacks required capabilities (read/update/insert content, read comments, etc.).
+```json
+{"object": "error", "status": 403, "code": "restricted_resource", "message": "Insufficient permissions for this resource."}
+```
+
+**Cause:** The integration exists and the page is shared, but the integration lacks the required capability (read content, update content, insert content, read comments).
 
-**Solution:** Edit integration capabilities at notion.so/my-integrations. Ensure the integration has the needed capability enabled.
+**Fix:** Go to [notion.so/my-integrations](https://www.notion.so/my-integrations), select your integration, and enable the needed capabilities under "Capabilities." Common missing capability: "Read comments" when querying comments, or "Insert content" when creating pages.
 
 ---
 
 ### 404 — `object_not_found`
-**Message:** `Could not find [object type] with ID: ...`
 
-**Cause:** The page/database either does not exist OR is not shared with your integration. This is the most common Notion API error.
+```json
+{"object": "error", "status": 404, "code": "object_not_found", "message": "Could not find page with ID: abc123..."}
+```
+
+**Cause:** The page, database, or block either does not exist or has not been shared with your integration. This is the single most common Notion API error.
+
+**Fix:**
 
-**Solution:**
-1. Open the page in Notion
-2. Click `...` menu -> **Connections** -> Add your integration
-3. Parent pages must also be shared — sharing a child page alone is not enough
+1. Open the target page in Notion
+2. Click the `...` menu at top right
+3. Select **Connections** and add your integration
+4. Parent pages must also be shared — sharing only a child page is not enough
 
 ```typescript
-// Defensive pattern
-const { data, error } = await safeNotionCall(() =>
-  notion.pages.retrieve({ page_id: pageId })
-);
-if (error?.includes('not found')) {
-  console.log('Page not shared with integration. Add via Connections menu.');
+// Defensive retrieval pattern
+try {
+  const page = await notion.pages.retrieve({ page_id: pageId });
+} catch (error) {
+  if (isNotionClientError(error) && error.code === APIErrorCode.ObjectNotFound) {
+    console.error('Page not shared with integration. Add via Connections menu.');
+  }
 }
 ```
 
+**Page ID gotcha:** Notion URLs use 32-character hex IDs without dashes (`https://notion.so/Page-abc123def456...`). The API accepts both dashed (`abc123de-f456-...`) and undashed formats. If you're extracting IDs from URLs, strip the page title prefix and use the last 32 characters.
+
 ---
 
 ### 400 — `validation_error`
-**Message varies:** Property name/type mismatches, invalid filter syntax, malformed requests.
 
-**Common causes and fixes:**
+```json
+{"object": "error", "status": 400, "code": "validation_error", "message": "..."}
+```
+
+**Message varies.** This is the broadest error category. Common sub-cases:
 
-```typescript
-// Wrong: Property name doesn't match database schema
-{ property: 'title', title: { contains: 'x' } }
-// Right: Use the exact property name from the database
-{ property: 'Name', title: { contains: 'x' } }
+| Message Pattern | Cause | Fix |
+|----------------|-------|-----|
+| `Title is not a property that exists` | Wrong property name | Use exact name from database schema (case-sensitive) |
+| `... should be an array` | Rich text passed as string | Wrap in `[{ text: { content: "value" } }]` |
+| `body.parent.database_id should be defined` | Missing parent in page create | Include `parent: { database_id: "..." }` |
+| `... should be a string, instead was ...` | Wrong property type for filter | Match filter type to property type (see below) |
+| `Could not find property with name or id` | Property renamed in Notion UI | Retrieve schema with `databases.retrieve()` to get current names |
+
+**Filter type mismatches** — the most common validation error:
 
-// Wrong: Using wrong filter type for property
+```typescript
+// WRONG: Status is a status property, not text
 { property: 'Status', text: { equals: 'Done' } }
-// Right: Status is a select, not text
-{ property: 'Status', select: { equals: 'Done' } }
-
-// Wrong: Creating page without required title property
-notion.pages.create({
-  parent: { database_id: dbId },
-  properties: { Status: { select: { name: 'New' } } },  // Missing title!
-});
-// Right: Always include the title property
-notion.pages.create({
-  parent: { database_id: dbId },
-  properties: {
-    Name: { title: [{ text: { content: 'New item' } }] },  // Title required
-    Status: { select: { name: 'New' } },
-  },
-});
-```
-
-**Debug tip:** Retrieve the database schema first:
+// RIGHT: Use the matching filter type
+{ property: 'Status', status: { equals: 'Done' } }
+
+// WRONG: Passing plain string for title
+{ Name: { title: 'My Page' } }
+// RIGHT: Title requires rich text array
+{ Name: { title: [{ text: { content: 'My Page' } }] } }
+```
+
+**Debug tip:** Always retrieve the database schema first to avoid property name/type errors:
+
 ```typescript
 const db = await notion.databases.retrieve({ database_id: dbId });
-console.log(Object.entries(db.properties).map(([k, v]) => `${k}: ${v.type}`));
+console.log(Object.entries(db.properties).map(([name, prop]) => `${name}: ${prop.type}`));
+// Output: "Name: title", "Status: status", "Tags: multi_select", ...
 ```
 
 ---
 
 ### 429 — `rate_limited`
-**Message:** `Rate limited`
 
-**Cause:** Exceeded average of 3 requests per second.
+```json
+{"object": "error", "status": 429, "code": "rate_limited", "message": "Rate limited"}
+```
+
+**Cause:** Exceeded Notion's average rate limit of 3 requests per second per integration.
+
+**Fix:**
 
-**Solution:**
 ```typescript
-import { isNotionClientError, APIErrorCode } from '@notionhq/client';
+import { Client, isNotionClientError, APIErrorCode } from '@notionhq/client';
 
 async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
-  for (let attempt = 0; attempt < maxRetries; attempt++) {
+  for (let attempt = 0; attempt <= maxRetries; attempt++) {
     try {
       return await fn();
     } catch (error) {
       if (isNotionClientError(error) && error.code === APIErrorCode.RateLimited) {
-        const retryAfter = parseInt(error.headers?.['retry-after'] ?? '1');
-        console.log(`Rate limited. Waiting ${retryAfter}s...`);
-        await new Promise(r => setTimeout(r, retryAfter * 1000));
+        const wait = Math.pow(2, attempt) * 1000; // exponential backoff
+        console.log(`Rate limited. Waiting ${wait}ms (attempt ${attempt + 1}/${maxRetries})...`);
+        await new Promise(r => setTimeout(r, wait));
         continue;
       }
       throw error;
@@ -157,80 +184,164 @@ async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
 }
 ```
 
-Note: `@notionhq/client` has built-in retry (default 2 retries with backoff).
+The `@notionhq/client` SDK has built-in retry with exponential backoff. If you hit rate limits frequently, batch operations and add delays between sequential calls. For bulk operations, see `notion-rate-limits`.
 
 ---
 
 ### 409 — `conflict_error`
-**Message:** `Resource was updated by another request.`
 
-**Cause:** Concurrent updates to the same page/block.
+```json
+{"object": "error", "status": 409, "code": "conflict_error", "message": "Transaction has an existing lock on the object."}
+```
+
+**Cause:** Concurrent modifications to the same page, block, or database. Common in parallel scripts or multi-user workflows.
+
+**Fix:** Retry the operation. The SDK handles this automatically. If writing your own retry logic, a simple retry after 1-2 seconds resolves most conflicts. Avoid parallelizing writes to the same page.
+
+---
+
+### 500 — `internal_server_error`
+
+```json
+{"object": "error", "status": 500, "code": "internal_server_error", "message": "Internal Server Error"}
+```
+
+**Cause:** Bug or transient failure on Notion's servers.
 
-**Solution:** Retry the operation. The SDK's built-in retry handles this automatically.
+**Fix:** Retry with exponential backoff. If persistent (>5 minutes), check [status.notion.so](https://status.notion.so) for ongoing incidents. Consider filing a bug report at [developers.notion.com](https://developers.notion.com) with the request ID from the response headers (`x-request-id`).
 
 ---
 
 ### 502/503 — `service_unavailable`
-**Message:** `Notion encountered an internal error.`
 
-**Cause:** Notion's servers are temporarily unavailable.
+```json
+{"object": "error", "status": 503, "code": "service_unavailable", "message": "Notion is unavailable. Try again later."}
+```
+
+**Cause:** Notion's servers are down or under maintenance.
+
+**Fix:**
 
-**Solution:**
 ```bash
 # Check Notion status
-curl -s https://status.notion.com/api/v2/status.json | jq '.status.description'
+curl -s https://status.notion.so/api/v2/status.json | jq '.status.description'
 ```
-Wait and retry. Check https://status.notion.com for ongoing incidents.
+
+Wait and retry. Monitor [status.notion.so](https://status.notion.so) for incident updates.
 
 ---
 
-### Step 3: Common Non-HTTP Errors
+### Step 3: Common Non-HTTP Gotchas
 
 ```typescript
-// "Could not find property with name or id: ..."
-// → Property was renamed in Notion UI. Update your code to match.
+// "body failed validation: body.children should be an array"
+// → Block children must always be an array, even for a single child.
+
+// Rich text structure — the #1 source of frustration
+// WRONG: "Hello"
+// RIGHT: [{ type: "text", text: { content: "Hello" } }]
+// Rich text is ALWAYS an array of rich text objects.
 
-// "body failed validation: ... should be a string"
-// → You passed a number or object where a string was expected.
-// Common with rich_text — must be an array of rich text objects.
+// Block type mismatch when appending children
+// → Each block type has its own structure. A paragraph block needs:
+//   { type: "paragraph", paragraph: { rich_text: [{ text: { content: "..." } }] } }
 
-// "body.properties.Name.title should be defined"
-// → Every database page requires its title property.
+// Timeout errors (default 60s)
+// → Increase via Client constructor:
+//   new Client({ auth: token, timeoutMs: 120_000 })
 
-// Timeout errors
-// → Increase timeoutMs on the Client constructor (default is 60s).
+// Pagination: missing results
+// → Always check has_more and pass start_cursor for next page.
+//   Notion returns max 100 items per request.
 ```
 
 ## Output
-- Identified error cause from code and message
-- Applied targeted fix
+
+- Identified error cause from HTTP status and `code` field
+- Applied targeted fix from the matching section
 - Verified resolution with test API call
 
 ## Error Handling
-| Code | HTTP | Retryable | Action |
-|------|------|-----------|--------|
-| `unauthorized` | 401 | No | Fix token |
-| `restricted_resource` | 403 | No | Add capability |
-| `object_not_found` | 404 | No | Share page |
-| `validation_error` | 400 | No | Fix request |
-| `rate_limited` | 429 | Yes | Respect Retry-After |
-| `conflict_error` | 409 | Yes | Retry |
-| `internal_server_error` | 500 | Yes | Retry |
-| `service_unavailable` | 503 | Yes | Wait + retry |
+
+| Code | HTTP | Error Name | Retryable | Recommended Action |
+|------|------|------------|-----------|-------------------|
+| `unauthorized` | 401 | Authentication failure | No | Regenerate token at notion.so/my-integrations |
+| `restricted_resource` | 403 | Missing capability | No | Enable capability in integration settings |
+| `object_not_found` | 404 | Not shared / not found | No | Share page with integration via Connections menu |
+| `validation_error` | 400 | Malformed request | No | Fix request body — retrieve schema first |
+| `rate_limited` | 429 | Rate limit exceeded | Yes | Respect `Retry-After` header, use exponential backoff |
+| `conflict_error` | 409 | Concurrent modification | Yes | Retry after 1-2s, serialize writes to same object |
+| `internal_server_error` | 500 | Notion server error | Yes | Retry with backoff, check status.notion.so |
+| `service_unavailable` | 502/503 | Notion down | Yes | Wait and retry, check status.notion.so |
+| `gateway_timeout` | 504 | Request timeout | Yes | Retry, reduce query complexity or page size |
 
 ## Examples
 
-### Diagnostic One-Liner
+### Full SDK Error Handler
+
+```typescript
+import { Client, isNotionClientError, APIErrorCode, ClientErrorCode } from '@notionhq/client';
+
+const notion = new Client({ auth: process.env.NOTION_TOKEN });
+
+try {
+  const page = await notion.pages.retrieve({ page_id: pageId });
+} catch (error) {
+  if (isNotionClientError(error)) {
+    switch (error.code) {
+      case APIErrorCode.ObjectNotFound:
+        console.error('Page not found or not shared with integration');
+        break;
+      case APIErrorCode.Unauthorized:
+        console.error('Invalid API token');
+        break;
+      case APIErrorCode.RestrictedResource:
+        console.error('Integration lacks required capability');
+        break;
+      case APIErrorCode.RateLimited:
+        console.error('Rate limited — retry with backoff');
+        break;
+      case APIErrorCode.ValidationError:
+        console.error(`Validation error: ${error.message}`);
+        break;
+      case ClientErrorCode.RequestTimeout:
+        console.error('Request timed out');
+        break;
+      default:
+        console.error(`Notion error: ${error.code} — ${error.message}`);
+    }
+  } else {
+    throw error; // Non-Notion error
+  }
+}
+```
+
+### Quick Diagnostic Script
+
 ```bash
+# 1. Check Notion status
+curl -s https://status.notion.so/api/v2/status.json | jq '.status.description'
+
+# 2. Verify token
 curl -s https://api.notion.com/v1/users/me \
   -H "Authorization: Bearer ${NOTION_TOKEN}" \
   -H "Notion-Version: 2022-06-28" | jq '{id, type, name}'
+
+# 3. Test database access (replace DB_ID)
+curl -s "https://api.notion.com/v1/databases/${DB_ID}" \
+  -H "Authorization: Bearer ${NOTION_TOKEN}" \
+  -H "Notion-Version: 2022-06-28" | jq '{id, title: .title[0].plain_text}'
 ```
 
 ## Resources
-- [Notion API Error Codes](https://developers.notion.com/reference/request-limits)
-- [Notion Status Page](https://status.notion.com)
+
+- [Notion API Error Codes](https://developers.notion.com/reference/errors)
+- [Request Limits & Rate Limiting](https://developers.notion.com/reference/request-limits)
+- [Notion Status Page](https://status.notion.so)
 - [API Introduction](https://developers.notion.com/reference/intro)
+- [Working with Databases](https://developers.notion.com/docs/working-with-databases)
+- [@notionhq/client npm](https://www.npmjs.com/package/@notionhq/client)
 
 ## Next Steps
-For comprehensive debugging, see `notion-debug-bundle`.
+
+For comprehensive debugging workflows, see `notion-debug-bundle`. For rate limit strategies at scale, see `notion-rate-limits`.
PATCH

echo "Gold patch applied."
