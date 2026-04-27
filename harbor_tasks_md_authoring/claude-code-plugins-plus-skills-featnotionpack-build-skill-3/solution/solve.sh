#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-plugins-plus-skills

# Idempotency guard
if grep -qF "Set up a fast, reproducible local development workflow for Notion integrations. " "plugins/saas-packs/notion-pack/skills/notion-local-dev-loop/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/saas-packs/notion-pack/skills/notion-local-dev-loop/SKILL.md b/plugins/saas-packs/notion-pack/skills/notion-local-dev-loop/SKILL.md
@@ -1,11 +1,12 @@
 ---
 name: notion-local-dev-loop
 description: |
-  Configure Notion local development with hot reload, testing, and mocks.
-  Use when setting up a development environment, writing tests for Notion code,
-  or establishing a fast iteration cycle with the Notion API.
-  Trigger with phrases like "notion dev setup", "notion local development",
-  "notion test", "develop with notion", "mock notion".
+  Configure Notion local development with a dedicated dev integration,
+  test mocking, and hot reload. Use when setting up a development
+  environment, writing tests for Notion code, or establishing a fast
+  iteration cycle with the Notion API.
+  Trigger: "notion dev setup", "notion local development",
+  "mock notion", "notion test environment".
 allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(pnpm:*), Grep
 version: 1.0.0
 license: MIT
@@ -17,42 +18,120 @@ compatible-with: claude-code
 # Notion Local Dev Loop
 
 ## Overview
-Set up a fast, reproducible local development workflow for Notion integrations with type-safe client, test mocking, and hot reload.
+
+Set up a fast, reproducible local development workflow for Notion integrations. This skill covers creating a dedicated dev integration with its own token, structuring the project for testability, mocking the Notion SDK in unit tests, and running integration tests against a sandboxed dev workspace. The approach keeps production data safe while enabling rapid iteration.
 
 ## Prerequisites
-- Completed `notion-install-auth` setup
-- Node.js 18+ with npm/pnpm
-- TypeScript configured
+
+- Completed `notion-install-auth` setup (you have a working Notion integration)
+- Node.js 18+ with npm/pnpm, or Python 3.10+
+- A Notion workspace where you can create test pages and databases
 
 ## Instructions
 
-### Step 1: Project Structure
+### Step 1: Create a Dev Integration and Workspace Sandbox
+
+Create a separate integration exclusively for development. This prevents accidental writes to production data.
+
+1. Go to **Settings & Members > Connections > Develop or manage integrations** (or visit [developers.notion.com](https://developers.notion.com))
+2. Click **New integration** and name it `My App — Dev`
+3. Copy the token (starts with `ntn_`) into `.env.development`
+4. Create a dedicated **Dev Workspace** page (or a top-level "Dev Testing" page) and share it with the dev integration
+5. Inside that page, create test databases that mirror your production schema
+
+```bash
+# .env.development — git-ignored, dev only
+NOTION_TOKEN=ntn_dev_xxxxxxxxxxxxxxxxxxxx
+NOTION_TEST_DATABASE_ID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
+NOTION_TEST_PAGE_ID=ffffffff-0000-1111-2222-333333333333
+
+# .env.example — commit this as a template
+NOTION_TOKEN=ntn_your_dev_token_here
+NOTION_TEST_DATABASE_ID=your_test_db_id
+NOTION_TEST_PAGE_ID=your_test_page_id
+```
+
+Project structure:
+
 ```
 my-notion-project/
 ├── src/
 │   ├── notion/
-│   │   ├── client.ts       # Singleton client
-│   │   ├── queries.ts      # Database query functions
-│   │   └── helpers.ts      # Property extractors, rich text builders
+│   │   ├── client.ts          # Singleton with retry + rate-limit awareness
+│   │   ├── queries.ts         # Database query wrappers
+│   │   └── helpers.ts         # Property extractors, rich text builders
 │   └── index.ts
 ├── tests/
-│   ├── notion.test.ts      # Unit tests with mocks
-│   └── integration.test.ts # Live API tests (uses real token)
-├── .env                    # NOTION_TOKEN (git-ignored)
-├── .env.example            # Template for team
+│   ├── unit/
+│   │   └── notion.test.ts     # Mocked SDK tests
+│   └── integration/
+│       └── notion.test.ts     # Live API tests (gated)
+├── .env.development            # Dev token (git-ignored)
+├── .env.example                # Template for team
 ├── .gitignore
 ├── package.json
-└── tsconfig.json
+├── tsconfig.json
+└── vitest.config.ts
+```
+
+### Step 2: Configure the Client with Retry and Rate-Limit Handling
+
+The Notion API enforces a hard limit of **3 requests per second** across all pricing tiers. Build retry logic into your client from day one.
+
+```typescript
+// src/notion/client.ts
+import { Client, LogLevel, isNotionClientError, APIResponseError } from '@notionhq/client';
+
+let instance: Client | null = null;
+
+export function getNotionClient(): Client {
+  if (!instance) {
+    instance = new Client({
+      auth: process.env.NOTION_TOKEN,   // SDK reads NOTION_TOKEN automatically if omitted
+      logLevel: process.env.NODE_ENV === 'development' ? LogLevel.DEBUG : LogLevel.WARN,
+      // baseUrl can be overridden for proxy/mock servers:
+      // baseUrl: process.env.NOTION_BASE_URL || 'https://api.notion.com',
+    });
+  }
+  return instance;
+}
+
+// Retry wrapper with exponential backoff for rate limits
+export async function withRetry<T>(
+  fn: () => Promise<T>,
+  maxRetries = 3
+): Promise<T> {
+  for (let attempt = 0; attempt <= maxRetries; attempt++) {
+    try {
+      return await fn();
+    } catch (error) {
+      if (
+        isNotionClientError(error) &&
+        error instanceof APIResponseError &&
+        error.status === 429 &&
+        attempt < maxRetries
+      ) {
+        const retryAfter = parseInt(error.headers?.get('retry-after') || '1', 10);
+        const delay = retryAfter * 1000 * Math.pow(2, attempt);
+        console.warn(`Rate limited. Retrying in ${delay}ms (attempt ${attempt + 1}/${maxRetries})`);
+        await new Promise(resolve => setTimeout(resolve, delay));
+        continue;
+      }
+      throw error;
+    }
+  }
+  throw new Error('Unreachable');
+}
 ```
 
-### Step 2: Package Setup
 ```json
 {
   "scripts": {
     "dev": "tsx watch src/index.ts",
+    "dev:debug": "NOTION_LOG_LEVEL=debug tsx watch src/index.ts",
     "test": "vitest",
     "test:watch": "vitest --watch",
-    "test:integration": "INTEGRATION=true vitest run tests/integration.test.ts",
+    "test:integration": "INTEGRATION=true vitest run tests/integration/",
     "typecheck": "tsc --noEmit"
   },
   "dependencies": {
@@ -67,60 +146,50 @@ my-notion-project/
 }
 ```
 
-### Step 3: Environment Setup
-```bash
-# Copy template
-cp .env.example .env
-
-# .env.example contents:
-# NOTION_TOKEN=ntn_your_token_here
-# NOTION_TEST_DATABASE_ID=your_test_db_id
-# NOTION_TEST_PAGE_ID=your_test_page_id
+### Step 3: Write Unit Tests with Mocked SDK and Integration Tests
 
-# Install and run
-npm install
-npm run dev
-```
+**Unit tests** mock the entire `@notionhq/client` module so they run instantly with no network calls. **Integration tests** hit the real API but are gated behind an environment variable and target only the dev workspace.
 
-### Step 4: Unit Tests with Mocked Client
 ```typescript
-// tests/notion.test.ts
+// tests/unit/notion.test.ts
 import { describe, it, expect, vi, beforeEach } from 'vitest';
 import { Client } from '@notionhq/client';
 
-// Mock the entire @notionhq/client module
 vi.mock('@notionhq/client', () => ({
   Client: vi.fn().mockImplementation(() => ({
     databases: {
       query: vi.fn(),
       retrieve: vi.fn(),
+      create: vi.fn(),
+      update: vi.fn(),
     },
     pages: {
       create: vi.fn(),
       update: vi.fn(),
       retrieve: vi.fn(),
     },
     blocks: {
-      children: {
-        list: vi.fn(),
-        append: vi.fn(),
-      },
+      children: { list: vi.fn(), append: vi.fn() },
+      retrieve: vi.fn(),
+      update: vi.fn(),
+      delete: vi.fn(),
     },
     search: vi.fn(),
-    users: { list: vi.fn() },
+    users: { list: vi.fn(), retrieve: vi.fn() },
   })),
-  isNotionClientError: vi.fn(),
+  isNotionClientError: vi.fn((err) => err?.code !== undefined),
+  LogLevel: { DEBUG: 'debug', WARN: 'warn' },
 }));
 
-describe('Database Queries', () => {
-  let notion: any;
+describe('Database queries', () => {
+  let notion: InstanceType<typeof Client>;
 
   beforeEach(() => {
-    notion = new Client({ auth: 'test-token' });
+    notion = new Client({ auth: 'ntn_test_token' });
   });
 
-  it('should query database with status filter', async () => {
-    notion.databases.query.mockResolvedValue({
+  it('queries database with a status filter', async () => {
+    const mockResponse = {
       results: [
         {
           id: 'page-1',
@@ -132,10 +201,11 @@ describe('Database Queries', () => {
       ],
       has_more: false,
       next_cursor: null,
-    });
+    };
+    (notion.databases.query as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse);
 
     const result = await notion.databases.query({
-      database_id: 'test-db',
+      database_id: 'test-db-id',
       filter: { property: 'Status', select: { equals: 'Done' } },
     });
 
@@ -147,74 +217,66 @@ describe('Database Queries', () => {
     );
   });
 
-  it('should handle pagination', async () => {
-    notion.databases.query
-      .mockResolvedValueOnce({
-        results: [{ id: '1' }],
-        has_more: true,
-        next_cursor: 'cursor-1',
-      })
-      .mockResolvedValueOnce({
-        results: [{ id: '2' }],
-        has_more: false,
-        next_cursor: null,
-      });
+  it('handles pagination across multiple pages', async () => {
+    const queryMock = notion.databases.query as ReturnType<typeof vi.fn>;
+    queryMock
+      .mockResolvedValueOnce({ results: [{ id: '1' }], has_more: true, next_cursor: 'cursor-abc' })
+      .mockResolvedValueOnce({ results: [{ id: '2' }], has_more: false, next_cursor: null });
 
-    // First call
     const page1 = await notion.databases.query({ database_id: 'db' });
     expect(page1.has_more).toBe(true);
 
-    // Second call with cursor
     const page2 = await notion.databases.query({
       database_id: 'db',
       start_cursor: page1.next_cursor,
     });
     expect(page2.has_more).toBe(false);
+    expect(queryMock).toHaveBeenCalledTimes(2);
   });
 });
 ```
 
-### Step 5: Integration Tests (Live API)
 ```typescript
-// tests/integration.test.ts
+// tests/integration/notion.test.ts
 import { describe, it, expect } from 'vitest';
 import { Client } from '@notionhq/client';
 
 const SKIP = !process.env.INTEGRATION;
 
-describe.skipIf(SKIP)('Notion Integration', () => {
+describe.skipIf(SKIP)('Notion Integration (live API)', () => {
   const notion = new Client({ auth: process.env.NOTION_TOKEN! });
   const testDbId = process.env.NOTION_TEST_DATABASE_ID!;
 
-  it('should connect and list users', async () => {
+  it('connects and lists workspace users', async () => {
     const { results } = await notion.users.list({});
     expect(results.length).toBeGreaterThan(0);
   });
 
-  it('should query test database', async () => {
+  it('queries the test database', async () => {
     const response = await notion.databases.query({
       database_id: testDbId,
       page_size: 1,
     });
     expect(response.results).toBeDefined();
   });
 
-  it('should create and archive a test page', async () => {
+  it('creates and archives a test page (cleanup)', async () => {
     const page = await notion.pages.create({
       parent: { database_id: testDbId },
       properties: {
-        Name: { title: [{ text: { content: `Test ${Date.now()}` } }] },
+        Name: { title: [{ text: { content: `DevLoop Test ${Date.now()}` } }] },
       },
     });
     expect(page.id).toBeTruthy();
 
-    // Clean up
+    // Always clean up
     await notion.pages.update({ page_id: page.id, archived: true });
   });
 });
 ```
 
-### Step 6: Vitest Configuration
+Vitest configuration:
+
 ```typescript
 // vitest.config.ts
 import { defineConfig } from 'vitest/config';
@@ -223,41 +285,99 @@ export default defineConfig({
   test: {
     globals: true,
     setupFiles: ['dotenv/config'],
-    testTimeout: 30_000, // Notion API can be slow
+    testTimeout: 30_000,  // Notion API can be slow under rate limits
+    include: ['tests/**/*.test.ts'],
   },
 });
 ```
 
 ## Output
-- Working development environment with hot reload via `tsx watch`
-- Unit tests with fully mocked Notion client
-- Integration tests gated behind `INTEGRATION=true`
-- Type checking with `tsc --noEmit`
+
+After completing these steps you will have:
+
+- A **dedicated dev integration** with its own token, isolated from production
+- A **singleton client** with built-in retry logic for the 3 req/s rate limit
+- **Unit tests** that run instantly using mocked `@notionhq/client`
+- **Integration tests** gated behind `INTEGRATION=true`, targeting dev-only pages
+- **Hot reload** via `tsx watch` for rapid iteration
+- **Type checking** via `tsc --noEmit`
 
 ## Error Handling
+
 | Error | Cause | Solution |
 |-------|-------|----------|
-| `NOTION_TOKEN undefined` | Missing .env file | Copy from .env.example |
-| Mock not working | Import order | Ensure `vi.mock` is at top of test file |
-| Integration test 404 | Test DB not shared | Add integration to test database |
-| Timeout in tests | Slow API | Increase `testTimeout` in vitest config |
+| `NOTION_TOKEN undefined` | Missing `.env.development` or not loaded | Run `cp .env.example .env.development` and fill in dev token |
+| `401 Unauthorized` | Token invalid or integration not connected to page | Re-share the dev page with the dev integration |
+| `404 Not found` (database/page) | Test DB not shared with dev integration | Open DB in Notion > `...` > Connections > add your dev integration |
+| Mock not intercepting calls | `vi.mock()` not at file top level | Move `vi.mock('@notionhq/client', ...)` above all imports |
+| `429 Rate Limited` | Exceeded 3 req/s | Use `withRetry` wrapper; add delay between batch operations |
+| Integration tests timeout | Slow API under rate limits | Increase `testTimeout` in vitest config; reduce test data volume |
+| `baseUrl` connection refused | Proxy or mock server not running | Verify proxy is up; remove `baseUrl` override for direct API access |
 
 ## Examples
 
-### Quick Smoke Test
-```bash
-# One-line connection test
-NOTION_TOKEN=ntn_xxx npx tsx -e "
-  const { Client } = require('@notionhq/client');
-  new Client({ auth: process.env.NOTION_TOKEN })
-    .users.list({}).then(r => console.log('OK:', r.results.length, 'users'));
-"
+### TypeScript: Quick Connection Test
+
+```typescript
+import { Client } from '@notionhq/client';
+
+const notion = new Client({ auth: process.env.NOTION_TOKEN });
+
+async function smokeTest() {
+  const { results } = await notion.users.list({});
+  console.log(`Connected. ${results.length} user(s) in workspace.`);
+
+  // Verify dev database access
+  const db = await notion.databases.retrieve({
+    database_id: process.env.NOTION_TEST_DATABASE_ID!,
+  });
+  console.log(`Dev database: "${(db as any).title?.[0]?.plain_text || db.id}"`);
+}
+
+smokeTest().catch(console.error);
+```
+
+### Python: Dev Environment with notion-client
+
+```python
+import os
+from notion_client import Client
+from dotenv import load_dotenv
+
+load_dotenv(".env.development")
+
+notion = Client(auth=os.environ["NOTION_TOKEN"])
+
+# Quick smoke test
+users = notion.users.list()
+print(f"Connected. {len(users['results'])} user(s) in workspace.")
+
+# Query dev database
+db_id = os.environ["NOTION_TEST_DATABASE_ID"]
+results = notion.databases.query(database_id=db_id, page_size=1)
+print(f"Dev database has {len(results['results'])} page(s) (showing 1)")
+
+# Mock example for pytest
+def test_query_with_mock(mocker):
+    mock_notion = mocker.patch("notion_client.Client")
+    mock_notion.return_value.databases.query.return_value = {
+        "results": [{"id": "page-1"}],
+        "has_more": False,
+        "next_cursor": None,
+    }
+    client = Client(auth="ntn_test")
+    result = client.databases.query(database_id="test-db")
+    assert len(result["results"]) == 1
 ```
 
 ## Resources
-- [Vitest Documentation](https://vitest.dev/)
-- [tsx Documentation](https://github.com/privatenumber/tsx)
-- [@notionhq/client npm](https://www.npmjs.com/package/@notionhq/client)
+
+- [@notionhq/client (npm)](https://www.npmjs.com/package/@notionhq/client) — official Node.js SDK
+- [notion-sdk-py (PyPI)](https://pypi.org/project/notion-client/) — official Python SDK
+- [Notion API Rate Limits](https://developers.notion.com/reference/request-limits) — 3 req/s across all tiers
+- [Notion API Errors](https://developers.notion.com/reference/errors) — status codes and retry guidance
+- [Vitest Mocking Guide](https://vitest.dev/guide/mocking.html) — `vi.mock` patterns for SDK mocking
 
 ## Next Steps
-See `notion-sdk-patterns` for production-ready code patterns.
+
+See `notion-sdk-patterns` for production-ready query helpers, pagination utilities, and property extraction functions.
PATCH

echo "Gold patch applied."
