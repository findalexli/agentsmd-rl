#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "The Notion API is **free with every workspace plan** \u2014 there is no per-call pric" "plugins/saas-packs/notion-pack/skills/notion-cost-tuning/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/notion-pack/skills/notion-cost-tuning/SKILL.md b/plugins/saas-packs/notion-pack/skills/notion-cost-tuning/SKILL.md
@@ -1,98 +1,156 @@
 ---
 name: notion-cost-tuning
 description: |
-  Optimize Notion API usage and reduce request volume.
-  Use when analyzing Notion API usage patterns, reducing unnecessary requests,
-  or implementing efficient data access strategies.
-  Trigger with phrases like "notion cost", "notion API usage",
-  "reduce notion requests", "notion optimization", "notion efficient".
-allowed-tools: Read, Grep
+  Optimize Notion API usage to minimize rate-limit pressure, reduce engineering
+  overhead, and maximize throughput. Use when auditing request volume, eliminating
+  redundant API calls, implementing caching, or restructuring queries for efficiency.
+  Trigger with "notion cost", "notion optimize", "notion API usage", "reduce notion
+  requests", "notion rate limit budget", "notion efficient", "notion caching".
+allowed-tools: Read, Write, Edit, Bash(npm:*), Glob, Grep
 version: 1.0.0
 license: MIT
 author: Jeremy Longshore <jeremy@intentsolutions.io>
-tags: [saas, productivity, notion]
+tags: [saas, productivity, notion, optimization, caching, cost]
 compatible-with: claude-code
 ---
 
 # Notion Cost Tuning
 
 ## Overview
-Optimize Notion API request volume through caching, batching, webhook-driven updates, and efficient query patterns. Notion does not charge per API request, but rate limits (3 req/s) make efficiency critical for performance.
+
+The Notion API is **free with every workspace plan** — there is no per-call pricing. The real "cost" is the **3 requests/second rate limit** (per integration token) and engineering time wasted on inefficient patterns. Apply six strategies below to reduce request volume by 80-95%.
+
+**Notion workspace pricing (for context — API access is included at every tier):**
+
+| Plan | Price | API Access | Rate Limit |
+|------|-------|------------|------------|
+| Free | $0 | Full API | 3 req/sec |
+| Plus | $12/user/mo | Full API | 3 req/sec |
+| Business | $28/user/mo | Full API | 3 req/sec |
+| Enterprise | Custom | Full API | 3 req/sec |
+
+The rate limit is identical across all plans. Optimization is about staying within 3 req/sec, not reducing a bill.
 
 ## Prerequisites
-- Understanding of your integration's request patterns
-- Access to request logging or monitoring
-- `@notionhq/client` installed
+
+- `@notionhq/client` v2.x installed (`npm install @notionhq/client`)
+- Integration token from [notion.so/my-integrations](https://www.notion.so/my-integrations)
+- Token shared with target pages/databases via the **Connections** menu in Notion
+- For queue patterns: `p-queue` v8+ (`npm install p-queue`)
+- For caching: `node-cache` or `lru-cache` (`npm install lru-cache`)
 
 ## Instructions
 
-### Step 1: Audit Current Usage
+### Step 1: Audit Current Request Volume
+
+Before optimizing, measure your baseline. Instrument the Notion client to track every API call by method, endpoint, and timestamp.
 
 ```typescript
-// Instrument the client to track request volume
-let requestCount = 0;
-const requestLog: { method: string; endpoint: string; timestamp: number }[] = [];
-
-// Wrap notion calls with tracking
-async function trackedCall<T>(method: string, fn: () => Promise<T>): Promise<T> {
-  requestCount++;
-  requestLog.push({ method, endpoint: method, timestamp: Date.now() });
-  return fn();
+import { Client } from '@notionhq/client';
+
+interface RequestEntry {
+  method: string;
+  endpoint: string;
+  timestamp: number;
+  durationMs: number;
 }
 
-// Periodic report
-setInterval(() => {
+const requestLog: RequestEntry[] = [];
+const notion = new Client({ auth: process.env.NOTION_TOKEN });
+
+// Wrap any Notion call with tracking
+async function tracked<T>(
+  method: string,
+  endpoint: string,
+  fn: () => Promise<T>,
+): Promise<T> {
+  const start = Date.now();
+  try {
+    return await fn();
+  } finally {
+    requestLog.push({
+      method,
+      endpoint,
+      timestamp: start,
+      durationMs: Date.now() - start,
+    });
+  }
+}
+
+// Generate audit report
+function auditReport() {
   const last60s = requestLog.filter(r => r.timestamp > Date.now() - 60_000);
-  console.log({
-    totalRequests: requestCount,
+  const byMethod = Object.groupBy(last60s, r => r.method);
+
+  console.table({
+    totalAllTime: requestLog.length,
     lastMinute: last60s.length,
-    reqPerSecond: (last60s.length / 60).toFixed(1),
-    breakdown: Object.groupBy(last60s, r => r.method),
+    reqPerSecond: (last60s.length / 60).toFixed(2),
+    avgLatencyMs: (
+      last60s.reduce((sum, r) => sum + r.durationMs, 0) / last60s.length
+    ).toFixed(0),
   });
-}, 60_000);
+
+  // Show hotspots — which methods consume the most budget
+  for (const [method, entries] of Object.entries(byMethod)) {
+    console.log(`  ${method}: ${entries!.length} calls (${((entries!.length / last60s.length) * 100).toFixed(0)}%)`);
+  }
+}
+
+// Example: track a database query
+const results = await tracked('databases.query', `/databases/${dbId}/query`, () =>
+  notion.databases.query({ database_id: dbId }),
+);
+
+// Run report every 60 seconds
+setInterval(auditReport, 60_000);
 ```
 
-### Step 2: Eliminate Redundant Reads
+**Target:** identify which operations consume > 50% of your request budget. Common culprits are polling loops, page retrieves that duplicate database query data, and unfiltered full-table scans.
 
-```typescript
-import { Client } from '@notionhq/client';
+### Step 2: Eliminate Redundant Reads and Reduce Payload Size
 
-const notion = new Client({ auth: process.env.NOTION_TOKEN });
+Three high-impact patterns to cut reads immediately:
 
-// BAD: Fetching full page when you only need the status
-const page = await notion.pages.retrieve({ page_id: pageId });       // 1 request
-const blocks = await notion.blocks.children.list({ block_id: pageId }); // 1 request
-// 2 requests when you might only need properties
+**Pattern A: Stop retrieving pages you already have from database queries.** Database query results include all properties — a separate `pages.retrieve` is redundant unless you need blocks.
 
-// GOOD: Properties are already in the database query result
-const { results } = await notion.databases.query({
-  database_id: dbId,
-  filter: { property: 'Assignee', people: { contains: userId } },
-});
-// 1 request, all properties included — no separate retrieve needed
+```typescript
+// WASTEFUL: 2 requests per page (query + retrieve)
+const { results } = await notion.databases.query({ database_id: dbId });
+for (const page of results) {
+  const full = await notion.pages.retrieve({ page_id: page.id }); // redundant!
+  processPage(full);
+}
+
+// EFFICIENT: 1 request total — properties are already in query results
+const { results } = await notion.databases.query({ database_id: dbId });
+for (const page of results) {
+  processPage(page); // same properties, no extra request
+}
 ```
 
-### Step 3: Use Filters to Reduce Page Size
+**Pattern B: Use `filter_properties` to reduce response size.** When you only need specific properties, pass their IDs to shrink the payload by 60-90%.
 
 ```typescript
-// BAD: Fetch all pages then filter in code
-const all = await getAllPages(dbId); // May need 10+ paginated requests
-const active = all.filter(p => getSelect(p, 'Status') === 'Active');
-
-// GOOD: Filter server-side
-const active = await notion.databases.query({
+// First, discover property IDs (one-time setup)
+const db = await notion.databases.retrieve({ database_id: dbId });
+console.log(
+  Object.entries(db.properties).map(([name, prop]) => `${name}: ${prop.id}`),
+);
+// Output: ["Status: abc1", "Assignee: def2", "Due Date: ghi3", ...]
+
+// Then query with only the properties you need
+const { results } = await notion.databases.query({
   database_id: dbId,
-  filter: { property: 'Status', select: { equals: 'Active' } },
-  page_size: 100,
+  filter_properties: ['abc1', 'def2'], // Only Status and Assignee
 });
-// Typically 1 request instead of 10+
+// Response is 60-90% smaller — faster network, faster parsing
 ```
 
-### Step 4: Use Timestamps to Fetch Only Changes
+**Pattern C: Use `last_edited_time` to fetch only changes since last sync.**
 
 ```typescript
-// Instead of re-fetching everything, use last_edited_time filter
-async function getRecentlyModified(dbId: string, sinceISO: string) {
+async function getChangesSince(dbId: string, sinceISO: string) {
   return notion.databases.query({
     database_id: dbId,
     filter: {
@@ -104,114 +162,287 @@ async function getRecentlyModified(dbId: string, sinceISO: string) {
   });
 }
 
-// Usage: only fetch changes since last sync
+// Incremental sync: only fetch what changed
 let lastSync = new Date().toISOString();
-setInterval(async () => {
-  const changes = await getRecentlyModified(dbId, lastSync);
+
+async function syncLoop() {
+  const changes = await getChangesSince(dbId, lastSync);
   if (changes.results.length > 0) {
-    console.log(`${changes.results.length} pages changed since last sync`);
+    console.log(`${changes.results.length} pages modified since ${lastSync}`);
     await processChanges(changes.results);
     lastSync = new Date().toISOString();
   }
-}, 60_000); // Check every minute instead of re-fetching everything
+}
+// 1-5 requests/minute instead of re-fetching entire database each time
 ```
 
-### Step 5: Replace Polling with Webhooks
+### Step 3: Cache, Batch, and Replace Polling
+
+**Caching:** Most Notion data is read-heavy. Cache database query results and page content with TTL-based invalidation.
 
 ```typescript
-// BAD: Polling every 10 seconds (360 requests/hour for ONE database)
-setInterval(async () => {
-  const pages = await notion.databases.query({ database_id: dbId });
-  await processPages(pages.results);
-}, 10_000);
+import { LRUCache } from 'lru-cache';
 
-// GOOD: Webhook-driven (0 requests for monitoring, only on-demand reads)
-app.post('/webhooks/notion', express.json(), async (req, res) => {
-  res.status(200).json({ ok: true });
+const pageCache = new LRUCache<string, any>({
+  max: 500,
+  ttl: 5 * 60 * 1000, // 5-minute TTL
+});
 
-  if (req.body.type === 'page.properties_updated') {
-    // Only fetch the specific page that changed
-    const page = await notion.pages.retrieve({ page_id: req.body.data.id });
-    await processPage(page);
-  }
+async function getCachedPage(pageId: string) {
+  const cached = pageCache.get(pageId);
+  if (cached) return cached; // 0 API requests
+
+  const page = await notion.pages.retrieve({ page_id: pageId });
+  pageCache.set(pageId, page);
+  return page;
+}
+
+// Cache database queries by filter hash
+const queryCache = new LRUCache<string, any>({
+  max: 100,
+  ttl: 2 * 60 * 1000, // 2-minute TTL for queries
 });
+
+async function cachedQuery(dbId: string, filter: any) {
+  const key = `${dbId}:${JSON.stringify(filter)}`;
+  const cached = queryCache.get(key);
+  if (cached) return cached;
+
+  const result = await notion.databases.query({
+    database_id: dbId,
+    filter,
+    page_size: 100,
+  });
+  queryCache.set(key, result);
+  return result;
+}
 ```
 
-### Step 6: Batch Write Operations
+**Batching writes:** The Notion API has no true batch endpoint, but `blocks.children.append` accepts up to 100 blocks per call.
 
 ```typescript
-// BAD: Create pages one at a time
-for (const task of tasks) {
+import PQueue from 'p-queue';
+
+// Rate-limited queue: respects 3 req/sec
+const queue = new PQueue({ concurrency: 3, interval: 1000, intervalCap: 3 });
+
+// BAD: 100 page creates = 100 sequential requests (~34 seconds at 3/sec)
+for (const item of items) {
   await notion.pages.create({
     parent: { database_id: dbId },
-    properties: taskToProperties(task),
+    properties: toProperties(item),
   });
-} // 100 tasks = 100 requests
-
-// BETTER: Throttle with p-queue but still one at a time
-import PQueue from 'p-queue';
-const queue = new PQueue({ concurrency: 3, interval: 1000, intervalCap: 3 });
+}
 
+// BETTER: 100 page creates via queue = 100 requests but 3x faster (~34 sec → 34 sec but concurrent)
 await Promise.all(
-  tasks.map(task =>
-    queue.add(() => notion.pages.create({
-      parent: { database_id: dbId },
-      properties: taskToProperties(task),
-    }))
-  )
-); // Same 100 requests but completes 3x faster
-
-// BEST: Batch blocks into single append calls
-const blocks = tasks.map(task => ({
-  paragraph: { rich_text: [{ text: { content: task.description } }] },
+  items.map(item =>
+    queue.add(() =>
+      notion.pages.create({
+        parent: { database_id: dbId },
+        properties: toProperties(item),
+      }),
+    ),
+  ),
+);
+
+// BEST for content: batch blocks into single append calls (100 blocks = 1 request)
+const blocks = items.map(item => ({
+  type: 'paragraph' as const,
+  paragraph: {
+    rich_text: [{ type: 'text' as const, text: { content: item.text } }],
+  },
 }));
-// 100 blocks in 1 request (max 100 per call)
-await notion.blocks.children.append({
-  block_id: parentPageId,
-  children: blocks,
+
+// Chunk into groups of 100 (API limit per call)
+for (let i = 0; i < blocks.length; i += 100) {
+  await queue.add(() =>
+    notion.blocks.children.append({
+      block_id: parentPageId,
+      children: blocks.slice(i, i + 100),
+    }),
+  );
+}
+```
+
+**Replace polling with webhooks:** Polling a single database every 10 seconds costs 360 requests/hour (3600s / 10s interval). Webhooks cost zero.
+
+```typescript
+import express from 'express';
+
+// POLLING (wasteful): 360 requests/hour per database (3600s / 10s = 360)
+setInterval(async () => {
+  const pages = await notion.databases.query({ database_id: dbId });
+  await processPages(pages.results);
+}, 10_000);
+
+// WEBHOOK (efficient): 0 polling requests, fetch only on change
+const app = express();
+app.post('/webhooks/notion', express.json(), async (req, res) => {
+  // Acknowledge immediately (Notion expects 200 within 3 seconds)
+  res.status(200).json({ ok: true });
+
+  const { type, data } = req.body;
+  if (type === 'page.properties_updated' || type === 'page.content_updated') {
+    // Invalidate cache, then fetch only the changed page
+    pageCache.delete(data.id);
+    const page = await notion.pages.retrieve({ page_id: data.id });
+    await processPage(page);
+  }
 });
 ```
 
 ## Output
-- Request volume analyzed and baseline established
-- Redundant reads eliminated
-- Server-side filtering replacing client-side filtering
-- Polling replaced with webhooks where possible
-- Write operations batched
+
+After applying these optimizations:
+
+- **Audit report** showing request volume baseline and hotspots
+- **Redundant reads eliminated** — no duplicate `pages.retrieve` after `databases.query`
+- **Payload sizes reduced** 60-90% via `filter_properties`
+- **Incremental sync** via `last_edited_time` filter replacing full-table scans
+- **Cache layer** with TTL-based invalidation for reads
+- **Write throughput maximized** via queue-based throttling and block batching
+- **Polling eliminated** where webhooks are available (360 req/hr per database saved)
+
+**Typical impact:** integrations drop from 500+ requests/hour to under 200 requests/hour (80-95% reduction), staying well within the 3 req/sec limit even with multiple databases.
 
 ## Error Handling
+
 | Issue | Cause | Solution |
 |-------|-------|----------|
-| Rate limited despite optimization | Shared token across services | Use separate integrations |
-| Stale data from caching | TTL too long | Reduce TTL or use webhook invalidation |
-| Webhook not triggering | Integration not shared with page | Add via Connections menu |
-| Large result sets | No filter applied | Always filter server-side |
+| 429 Too Many Requests despite optimization | Shared token across multiple services | Use separate integration tokens per service; each gets its own 3 req/sec budget |
+| Stale cached data causing bugs | Cache TTL too long for the use case | Shorten TTL to 30-60s for volatile data, or use webhook-based cache invalidation |
+| Webhook not triggering | Integration not connected to the page/database | Share via **Connections** menu in Notion; verify webhook URL is publicly accessible |
+| `filter_properties` returning empty results | Using property names instead of IDs | Run `databases.retrieve` to get property IDs (short strings like `abc1`), not display names |
+| Incremental sync missing updates | Clock skew between client and Notion server | Subtract 5-second buffer from `lastSync` timestamp to create overlap window |
+| `blocks.children.append` failing with 400 | More than 100 children in single call | Chunk arrays into groups of 100 before appending |
 
 ## Examples
 
 ### Request Reduction Calculator
+
+Estimate savings before implementing changes:
+
 ```typescript
 function estimateRequestSavings(config: {
   databases: number;
   avgPagesPerDb: number;
   pollIntervalSeconds: number;
   hoursPerDay: number;
+  retrievePerPage: number; // extra retrieve calls per page (0 = none)
 }) {
   const pollsPerHour = 3600 / config.pollIntervalSeconds;
-  const beforePerHour = config.databases * pollsPerHour *
-    Math.ceil(config.avgPagesPerDb / 100); // pagination
-  const afterPerHour = 0; // webhooks = 0 polling requests
+  const paginationCalls = Math.ceil(config.avgPagesPerDb / 100);
+
+  // Before: polling + pagination + redundant retrieves
+  const beforePerHour =
+    config.databases * pollsPerHour * paginationCalls +
+    config.databases * pollsPerHour * config.avgPagesPerDb * config.retrievePerPage;
+
+  // After: webhook-driven (0 polling) + no redundant retrieves
+  // Estimate ~5% of pages change per hour, triggering on-demand reads
+  const changedPagesPerHour = config.databases * config.avgPagesPerDb * 0.05;
+  const afterPerHour = changedPagesPerHour; // 1 request per changed page
 
-  console.log(`Before: ${beforePerHour} requests/hour`);
-  console.log(`After: ${afterPerHour} requests/hour (webhook-driven)`);
-  console.log(`Savings: ${beforePerHour * config.hoursPerDay}/day`);
+  const dailySavings = (beforePerHour - afterPerHour) * config.hoursPerDay;
+
+  console.log(`=== Request Budget Analysis ===`);
+  console.log(`Before: ${beforePerHour.toFixed(0)} requests/hour`);
+  console.log(`After:  ${afterPerHour.toFixed(0)} requests/hour`);
+  console.log(`Savings: ${dailySavings.toFixed(0)} requests/day (${((1 - afterPerHour / beforePerHour) * 100).toFixed(0)}% reduction)`);
+  console.log(`Rate limit headroom: ${((3 * 3600 - afterPerHour) / (3 * 3600) * 100).toFixed(0)}% of 3 req/sec budget unused`);
+}
+
+// Example: 5 databases, 200 pages each, polling every 30 seconds, 12 hours/day
+estimateRequestSavings({
+  databases: 5,
+  avgPagesPerDb: 200,
+  pollIntervalSeconds: 30,
+  hoursPerDay: 12,
+  retrievePerPage: 1,
+});
+// Before: 121,200 requests/hour
+// After:  50 requests/hour
+// Savings: 1,453,800 requests/day (99% reduction)
+```
+
+### Full Optimization Wrapper
+
+Drop-in wrapper that adds caching, tracking, and queue management to the Notion client:
+
+```typescript
+import { Client } from '@notionhq/client';
+import { LRUCache } from 'lru-cache';
+import PQueue from 'p-queue';
+
+export function createOptimizedClient(token: string) {
+  const notion = new Client({ auth: token });
+  const cache = new LRUCache<string, any>({ max: 1000, ttl: 5 * 60 * 1000 });
+  const writeQueue = new PQueue({ concurrency: 3, interval: 1000, intervalCap: 3 });
+  let requestCount = 0;
+
+  return {
+    // Cached page retrieve
+    async getPage(pageId: string) {
+      const cached = cache.get(`page:${pageId}`);
+      if (cached) return cached;
+      requestCount++;
+      const page = await notion.pages.retrieve({ page_id: pageId });
+      cache.set(`page:${pageId}`, page);
+      return page;
+    },
+
+    // Cached + filtered database query
+    async queryDatabase(dbId: string, filter?: any, filterProps?: string[]) {
+      const key = `query:${dbId}:${JSON.stringify(filter)}:${filterProps?.join(',')}`;
+      const cached = cache.get(key);
+      if (cached) return cached;
+      requestCount++;
+      const result = await notion.databases.query({
+        database_id: dbId,
+        ...(filter && { filter }),
+        ...(filterProps && { filter_properties: filterProps }),
+        page_size: 100,
+      });
+      cache.set(key, result);
+      return result;
+    },
+
+    // Queued page create (respects rate limit)
+    async createPage(dbId: string, properties: any) {
+      return writeQueue.add(() => {
+        requestCount++;
+        return notion.pages.create({
+          parent: { database_id: dbId },
+          properties,
+        });
+      });
+    },
+
+    // Invalidate cache for a specific page or database
+    invalidate(id: string) {
+      for (const key of cache.keys()) {
+        if (key.includes(id)) cache.delete(key);
+      }
+    },
+
+    // Stats
+    get stats() {
+      return { requestCount, cacheSize: cache.size, queuePending: writeQueue.pending };
+    },
+  };
 }
 ```
 
 ## Resources
-- [Request Limits](https://developers.notion.com/reference/request-limits)
-- [Filter Database Entries](https://developers.notion.com/reference/post-database-query-filter)
-- [Notion Webhooks](https://developers.notion.com/reference/webhooks)
+
+- [Notion API Rate Limits](https://developers.notion.com/reference/request-limits) — 3 req/sec per token, `Retry-After` header on 429
+- [Database Query Filter](https://developers.notion.com/reference/post-database-query-filter) — push filtering server-side
+- [Filter Properties Parameter](https://developers.notion.com/reference/retrieve-a-page#filter-properties) — reduce response payload size
+- [Notion Webhooks](https://developers.notion.com/reference/webhooks) — event-driven updates replacing polling
+- [Block Children Append](https://developers.notion.com/reference/patch-block-children) — batch up to 100 blocks per call
+- [Notion Pricing](https://www.notion.so/pricing) — API included at all tiers, no per-call charges
 
 ## Next Steps
-For architecture patterns, see `notion-reference-architecture`.
+
+For rate-limit retry patterns, see `notion-rate-limits`. For query and search patterns, see `notion-search-retrieve`. For overall architecture guidance, see `notion-reference-architecture`.
PATCH

echo "Gold patch applied."
