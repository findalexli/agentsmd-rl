#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency guard
if grep -qF "- [ ] `lib/db.ts` creates `db` using `createSqliteDatabaseAdapter(...)` and `cre" "app-skills/add-sqlite-database/SKILL.md" && grep -qF "description: Add a new route to a Remix app by defining it in app/routes.ts, imp" "app-skills/new-route/SKILL.md" && grep -qF "description: Use when you are in a newly created project directory and want to s" "app-skills/scaffold-remix-app/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/app-skills/add-sqlite-database/SKILL.md b/app-skills/add-sqlite-database/SKILL.md
@@ -0,0 +1,111 @@
+---
+name: add-sqlite-database
+description: Add a SQLite database to a Remix app.
+---
+
+# Add a Database to a New Remix App
+
+Use this skill when you need to add SQLite persistence to a Remix app.
+
+## Additional File Structure
+
+Add these paths to the base app structure:
+
+```text
+<app-name>/
+├── data/
+│   └── db.sqlite
+├── lib/
+│   ├── render.ts
+│   └── db.ts
+└── app/
+    └── root/
+        ├── controller.tsx
+        └── HomePage.tsx
+```
+
+Notes:
+
+- `data/` is at the project root and is a sibling of `app/`.
+- `lib/` is also at the project root and is a sibling of `app/`.
+- `data/db.sqlite` is created by SQLite when `lib/db.ts` opens the database file.
+
+## Workflow
+
+1. Install SQLite runtime dependency.
+
+```sh
+npm i better-sqlite3
+```
+
+2. Create the root `data` directory.
+
+```sh
+mkdir -p data
+```
+
+3. Create `lib/db.ts` with database setup logic.
+
+This module must export `db` as a `Database` object from `remix/data-table`.
+
+```ts
+import * as path from 'node:path'
+import BetterSqlite3 from 'better-sqlite3'
+import { createDatabase, type Database } from 'remix/data-table'
+import { createSqliteDatabaseAdapter } from 'remix/data-table-sqlite'
+
+let databaseFilePath = path.resolve(import.meta.dirname, '..', 'data', 'db.sqlite')
+let sqlite = new BetterSqlite3(databaseFilePath)
+
+sqlite.pragma('foreign_keys = ON')
+sqlite.pragma('journal_mode = WAL')
+
+let adapter = createSqliteDatabaseAdapter(sqlite)
+
+export let db: Database = createDatabase(adapter)
+```
+
+4. Use `db` in the root controller (same controller style as the scaffolding skill).
+
+```tsx
+import type { Controller } from 'remix/fetch-router'
+import { sql } from 'remix/data-table'
+
+import { routes } from '../../routes.ts'
+import { DatabaseContext } from '../../lib/db.ts'
+import { render } from '../../lib/render.ts'
+import { HomePage } from './HomePage.tsx'
+
+export default {
+  middleware: [],
+  actions: {
+    async home({ storage }) {
+      let db = storage.get(DatabaseContext)
+      await db.exec(sql`select 1`)
+
+      return render(
+        <HomePage title="My Remix App">
+          <h1>My Remix App</h1>
+          <p>Database is connected.</p>
+        </HomePage>,
+      )
+    },
+  },
+} satisfies Controller<typeof routes.root>
+```
+
+5. Keep SQLite files out of source control.
+
+Add a rule to `.gitignore`:
+
+```gitignore
+data/*.sqlite
+```
+
+## Checklist
+
+- [ ] `data/` exists at the project root (sibling of `app/`)
+- [ ] `lib/db.ts` exists at the project root (sibling of `app/`)
+- [ ] `lib/db.ts` exports `db` typed as `Database` from `remix/data-table`
+- [ ] `lib/db.ts` creates `db` using `createSqliteDatabaseAdapter(...)` and `createDatabase(...)`
+- [ ] `app/root/controller.tsx` imports and uses `db` in the root `Controller` object
diff --git a/app-skills/new-route/SKILL.md b/app-skills/new-route/SKILL.md
@@ -0,0 +1,102 @@
+---
+name: new-route
+description: Add a new route to a Remix app by defining it in app/routes.ts, implementing the handler, wiring it in app/router.ts, and using route href helpers for links and forms.
+---
+
+# Create a New Route
+
+Use this skill when adding a page or endpoint to a Remix app built with `remix/fetch-router`.
+
+## Workflow
+
+1. Define the route in `app/routes.ts`.
+
+- Keep route names descriptive and group related routes under nested objects.
+- Use method helpers when a route should match only one method (`get`, `post`, `put`, `del`, `form`).
+
+```ts
+import { get, route } from 'remix/fetch-router/routes'
+
+export let routes = route({
+  home: '/',
+  dashboard: get('/dashboard'),
+})
+```
+
+2. Implement the route handler.
+
+- For a single action, export a typed `BuildAction`.
+- For multi-action routes (such as form GET + POST), export a `Controller` with `actions`.
+
+```ts
+import type { BuildAction } from 'remix/fetch-router'
+
+import { routes } from './routes.ts'
+
+export let dashboard: BuildAction<'GET', typeof routes.dashboard> = {
+  async action() {
+    return new Response('Dashboard')
+  },
+}
+```
+
+3. Map the route in `app/router.ts`.
+
+- Import the handler and register it with `router.map(...)`.
+
+```ts
+import { routes } from './routes.ts'
+import { dashboard } from './dashboard.tsx'
+
+router.map(routes.dashboard, dashboard)
+```
+
+4. Link to the new route with `href()`.
+
+- Use route helpers instead of hard-coded path strings.
+
+```tsx
+<a href={routes.dashboard.href()}>Dashboard</a>
+```
+
+5. Add a focused test.
+
+- Add or update `app/router.test.ts` (or a route-specific `*.test.ts`) to verify method + path + response behavior.
+
+## Example: GET + POST Form Route
+
+```ts
+import { form, route } from 'remix/fetch-router/routes'
+
+export let routes = route({
+  contact: form('contact'),
+})
+```
+
+```ts
+import type { Controller } from 'remix/fetch-router'
+
+import { routes } from './routes.ts'
+
+export let contactController: Controller<typeof routes.contact> = {
+  actions: {
+    index() {
+      return new Response('<form method="post"></form>', {
+        headers: { 'Content-Type': 'text/html' },
+      })
+    },
+    async action({ formData }) {
+      let message = String(formData.get('message') ?? '')
+      return new Response(`Thanks: ${message}`)
+    },
+  },
+}
+```
+
+## Checklist
+
+- [ ] Route added in `app/routes.ts`
+- [ ] Handler/controller implemented and typed
+- [ ] Route registered in `app/router.ts`
+- [ ] Navigation/form actions use `routes.<name>.href()`
+- [ ] Test coverage added for the new behavior
diff --git a/app-skills/scaffold-remix-app/SKILL.md b/app-skills/scaffold-remix-app/SKILL.md
@@ -0,0 +1,264 @@
+---
+name: scaffold-remix-app
+description: Use when you are in a newly created project directory and want to scaffold the initial structure for a Remix app you can build features on top of.
+---
+
+# Scaffold a Remix App (Node.js)
+
+Use this skill when you are in a newly created directory and need to scaffold a basic Remix app that runs on Node.js.
+
+## File Structure
+
+```text
+.
+├── package.json
+├── server.ts
+├── routes.ts
+├── router.ts
+├── lib/
+│   ├── render.ts
+│   └── <shared>.ts
+└── app/
+    ├── root/
+    │   ├── controller.tsx
+    │   ├── controller.test.ts
+    │   ├── Layout.tsx
+    │   └── HomePage.tsx
+    └── <feature>/
+        ├── controller.tsx
+        ├── controller.test.ts
+        └── <component>.tsx
+```
+
+## Workflow
+
+1. Create the project subdirectories.
+
+```sh
+mkdir -p lib app/root
+```
+
+2. Create `package.json` with a test script.
+
+```json
+{
+  "scripts": {
+    "test": "tsx --test \"./app/**/*.test.ts\"",
+    "start": "tsx server.ts"
+  }
+}
+```
+
+3. Install dependencies.
+
+```sh
+npm i remix@3.0.0-alpha.3
+npm i tsx
+npm i -D @types/node
+```
+
+4. Use JSX with Remix components.
+
+Make sure your `tsconfig.json` enables JSX for `remix/component`:
+
+```json
+{
+  "compilerOptions": {
+    "jsx": "react-jsx",
+    "jsxImportSource": "remix/component",
+    "types": ["node"]
+  }
+}
+```
+
+Components in `remix/component` are not React components. They follow the Remix component model, where a component function returns a render function.
+
+5. Create `routes.ts`.
+
+```ts
+import { route } from 'remix/fetch-router/routes'
+
+export let routes = route({
+  root: {
+    home: '/',
+  },
+})
+```
+
+6. Create `lib/render.ts`.
+
+```ts
+import type { RemixNode } from 'remix/component'
+import { renderToStream } from 'remix/component/server'
+import { createHtmlResponse } from 'remix/response/html'
+
+export function render(node: RemixNode, init?: ResponseInit): Response {
+  return createHtmlResponse(renderToStream(node), init)
+}
+```
+
+7. Create `app/root/Layout.tsx`.
+
+```tsx
+import type { RemixNode } from 'remix/component'
+
+type LayoutProps = {
+  children?: RemixNode
+}
+
+export function Layout() {
+  return ({ children }: LayoutProps) => (
+    <html lang="en">
+      <head>
+        <meta charSet="utf-8" />
+        <meta name="viewport" content="width=device-width, initial-scale=1" />
+      </head>
+      <body>
+        {children}
+      </body>
+    </html>
+  )
+}
+```
+
+8. Create `app/root/HomePage.tsx`.
+
+```tsx
+export function HomePage() {
+  return () => (
+    <>
+      <h1>My Remix App</h1>
+      <p>Server is running.</p>
+    </>
+  )
+}
+```
+
+9. Create `app/root/controller.tsx`.
+
+```tsx
+import type { Controller } from 'remix/fetch-router'
+
+import { routes } from '../../routes.ts'
+import { render } from '../../lib/render.ts'
+import { Layout } from './Layout.tsx'
+import { HomePage } from './HomePage.tsx'
+
+export default {
+  middleware: [],
+  actions: {
+    home() {
+      return render(
+        <Layout>
+          <title>My Remix App</title>
+          <HomePage />
+        </Layout>,
+      )
+    },
+  },
+} satisfies Controller<typeof routes.root>
+```
+
+10. Create `router.ts`.
+
+```ts
+import { createRouter } from 'remix/fetch-router'
+
+import rootController from './app/root/controller.tsx'
+import { routes } from './routes.ts'
+
+export let router = createRouter()
+
+router.map(routes.root, rootController)
+```
+
+11. Create `app/root/controller.test.ts`.
+
+```ts
+import * as assert from 'node:assert/strict'
+import { describe, it } from 'node:test'
+
+import { router } from '../../router.ts'
+
+describe('root controller', () => {
+  it('serves the home page through router.fetch', async () => {
+    let response = await router.fetch('http://example.com/')
+    assert.equal(response.status, 200)
+
+    let contentType = response.headers.get('content-type') ?? ''
+    assert.match(contentType, /^text\/html/)
+
+    let body = await response.text()
+    assert.match(body, /<h1>My Remix App<\/h1>/)
+  })
+})
+```
+
+12. Create `server.ts`.
+
+```ts
+import * as http from 'node:http'
+import { createRequestListener } from 'remix/node-fetch-server'
+
+import { router } from './router.ts'
+
+let server = http.createServer(
+  createRequestListener(async (request) => {
+    try {
+      return await router.fetch(request)
+    } catch (error) {
+      console.error(error)
+      return new Response('Internal Server Error', { status: 500 })
+    }
+  }),
+)
+
+let port = process.env.PORT ? parseInt(process.env.PORT, 10) : 44100
+
+server.listen(port, () => {
+  console.log(`Server listening on http://localhost:${port}`)
+})
+
+let shuttingDown = false
+
+function shutdown() {
+  if (shuttingDown) return
+  shuttingDown = true
+  server.close(() => {
+    process.exit(0)
+  })
+}
+
+process.on('SIGINT', shutdown)
+process.on('SIGTERM', shutdown)
+```
+
+13. Run the test.
+
+```sh
+npm test
+```
+
+14. Run the app.
+
+```sh
+npm run start
+```
+
+Visit:
+
+- `http://localhost:44100/`
+
+## Checklist
+
+- [ ] `package.json` has `remix` in `dependencies`
+- [ ] `package.json` has `tsx` in `dependencies`
+- [ ] `package.json` has `@types/node` in `devDependencies`
+- [ ] `package.json` has a `test` script that runs `./app/**/*.test.ts` via `tsx`
+- [ ] `package.json` has a `start` script that runs `tsx server.ts`
+- [ ] `tsconfig.json` includes `"types": ["node"]`
+- [ ] `routes.ts` and `router.ts` are in the project root
+- [ ] `app/root/` contains `controller.tsx`, `controller.test.ts`, `Layout.tsx`, and `HomePage.tsx`
+- [ ] `router.ts` maps root route definitions to feature controllers
+- [ ] `server.ts` uses `createRequestListener(...)` and `router.fetch(...)`
+- [ ] Server handles `SIGINT` and `SIGTERM` for clean shutdown
PATCH

echo "Gold patch applied."
