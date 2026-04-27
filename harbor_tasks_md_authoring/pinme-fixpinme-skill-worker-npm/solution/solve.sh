#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pinme

# Idempotency guard
if grep -qF "> `API_KEY` is the sole credential for the Worker to call PinMe platform APIs. W" "skills/pinme-api/SKILL.md" && grep -qF "In this template, the Worker backend is primarily used for JSON APIs. Prefer sta" "skills/pinme/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/pinme-api/SKILL.md b/skills/pinme-api/SKILL.md
@@ -16,11 +16,11 @@ The following environment variables are automatically injected when the Worker i
 export interface Env {
   DB: D1Database;
   API_KEY: string;      // Project API Key — used for send_email and chat/completions authentication
-  BASE_URL?: string;    // Optional override for PinMe API base URL, defaults to https://pinme.dev
+  BASE_URL?: string;    // Optional override for PinMe API base URL, defaults to https://pinme.cloud
 }
 ```
 
-> `API_KEY` is the sole credential for the Worker to call PinMe platform APIs. When `BASE_URL` is not set, it defaults to `https://pinme.dev`.
+> `API_KEY` is the sole credential for the Worker to call PinMe platform APIs. When `BASE_URL` is not set, it defaults to `https://pinme.cloud`.
 
 ---
 
@@ -65,7 +65,7 @@ export interface Env {
 
 ```typescript
 async function sendEmail(env: Env, to: string, subject: string, html: string): Promise<{ ok: boolean; error?: string }> {
-  const baseUrl = env.BASE_URL ?? 'https://pinme.dev';
+  const baseUrl = env.BASE_URL ?? 'https://pinme.cloud';
   const resp = await fetch(`${baseUrl}/api/v4/send_email`, {
     method: 'POST',
     headers: {
@@ -164,7 +164,7 @@ async function callLLM(
   messages: Array<{ role: string; content: string }>,
   model = 'openai/gpt-4o-mini',
 ): Promise<{ content: string; error?: string }> {
-  const baseUrl = env.BASE_URL ?? 'https://pinme.dev';
+  const baseUrl = env.BASE_URL ?? 'https://pinme.cloud';
   const resp = await fetch(
     `${baseUrl}/api/v1/chat/completions?project_name=${projectName}`,
     {
@@ -209,7 +209,7 @@ async function handleChat(request: Request, env: Env): Promise<Response> {
 async function handleChatStream(request: Request, env: Env): Promise<Response> {
   const body = await request.text();
   const projectName = getProjectName(request);
-  const baseUrl = env.BASE_URL ?? 'https://pinme.dev';
+  const baseUrl = env.BASE_URL ?? 'https://pinme.cloud';
 
   // Ensure stream=true in the request
   let parsed = JSON.parse(body);
@@ -333,7 +333,7 @@ async function callPinmeAPI<T>(url: string, apiKey: string, body: unknown): Prom
 ### Usage Examples
 
 ```typescript
-const baseUrl = env.BASE_URL ?? 'https://pinme.dev';
+const baseUrl = env.BASE_URL ?? 'https://pinme.cloud';
 
 // Send email
 const emailResult = await callPinmeAPI<{ ok: boolean }>(
diff --git a/skills/pinme/SKILL.md b/skills/pinme/SKILL.md
@@ -130,19 +130,19 @@ pinme update-db              # Run SQL migrations only (when only db/ was modifi
 │   ├── wrangler.toml       # Worker config (auto-generated, do not modify)
 │   ├── package.json
 │   └── src/
-│       └── worker.ts       # Backend entry — JSON API only
+│       └── worker.ts       # Backend entry — primarily used for JSON APIs in this template
 ├── db/
 │   └── 001_init.sql        # SQL table definitions
 ├── frontend/
 │   ├── package.json
 │   ├── vite.config.ts      # Dev proxy: /api → localhost:8787
 │   ├── index.html
-│   ├── .env                # Auto-generated: VITE_WORKER_URL (do not modify)
+│   ├── .env                # Auto-generated: VITE_API_URL (do not modify)
 │   └── src/
 │       ├── main.tsx
 │       ├── App.tsx
 │       ├── utils/
-│       │   └── api.ts      # export const API = import.meta.env.VITE_WORKER_URL || ''
+│       │   └── api.ts      # export const API = import.meta.env.VITE_API_URL || ''
 │       └── pages/
 │           └── Home/
 │               └── index.tsx
@@ -189,9 +189,9 @@ The backend Worker is deployed at `https://{name}.pinme.pro`. Frontend API reque
 
 ---
 
-## Worker Code Patterns (backend/src/worker.ts)
+## Worker Code Patterns (`backend/src/worker.ts`)
 
-The Worker backend only serves JSON APIs. **No npm packages allowed** (no hono, express, etc.). Write routes manually:
+In this template, the Worker backend is primarily used for JSON APIs. Prefer standard Web APIs and simple manual routing by default. Worker-compatible libraries can be added when needed, but the default template does not rely on extra frameworks. Avoid packages that depend on a full Node.js runtime, a persistent local filesystem, native binaries, or child processes.
 
 ```typescript
 export interface Env {
@@ -229,20 +229,20 @@ export default {
 };
 ```
 
-### Worker Restrictions
+### Worker Constraints and Default Conventions
 
-| Prohibited | Alternative |
-|-----------|-------------|
-| `import from 'hono'` or any npm package | Manual routing (`if pathname === '/api/...'`) |
-| `import fs from 'fs'` / Node.js built-in modules | Web APIs: `crypto`, `fetch`, `URL`, etc. |
-| `require()` syntax | ESM `import` only |
-| Worker returning HTML | JSON API only |
-| Storing passwords in plaintext | Hash with SHA-256 before storing |
-| SQL string concatenation | Use `.bind()` parameterized queries |
+| Item | Notes |
+|------|------|
+| Dependency choice | Prefer standard Web APIs and simple manual routing by default. If extra dependencies are needed, prefer Worker-compatible libraries. |
+| Node.js capability | Workers now support part of Node.js compatibility, but they are not a full Node.js runtime. Do not assume all Node.js built-in modules are available or behave exactly the same. |
+| Filesystem | Do not treat a Worker like a server with a persistent local disk. Even if some `fs` capabilities are available, do not rely on persistence across requests. |
+| Response types | This template mainly uses the Worker for JSON APIs. If there is a clear need, it can also be adapted to return HTML or other content. |
+| Password storage | Never store passwords in plaintext. Use a dedicated password hashing algorithm such as bcrypt, scrypt, or Argon2. |
+| SQL | Do not build SQL by string concatenation. Use parameterized queries such as `.bind()`. |
 
 ### Email API Reference (for Worker Backend)
 
-When the backend needs email sending capability, use the PinMe platform API (`https://pinme.dev/api/v4/send_email`).
+When the backend needs email sending, use the PinMe platform API (`https://pinme.cloud/api/v4/send_email`).
 
 **1. Configure API_KEY**
 
@@ -279,7 +279,7 @@ async function handleSendEmail(request: Request, env: Env): Promise<Response> {
     return json({ error: 'Invalid email address' }, 400);
   }
 
-  const response = await fetch('https://pinme.dev/api/v4/send_email', {
+  const response = await fetch('https://pinme.cloud/api/v4/send_email', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
@@ -300,9 +300,9 @@ async function handleSendEmail(request: Request, env: Env): Promise<Response> {
 ## Frontend API Utility (frontend/src/utils/api.ts)
 
 ```typescript
-// Development: Vite proxies /api → localhost:8787
-// Production: VITE_WORKER_URL is auto-injected by pinme create
-export const API = import.meta.env.VITE_WORKER_URL || '';
+// Development: Vite proxies /api to localhost:8787
+// Production: VITE_API_URL is auto-injected by pinme create
+export const API = import.meta.env.VITE_API_URL || '';
 
 export function getApiUrl(path: string): string {
   return API ? `${API}${path}` : path;
@@ -331,41 +331,41 @@ if (meta.changes === 0) return json({ error: 'Not found' }, 404);
 
 ### SQL Migration Files
 
-**Format:** `db/NNN_description.sql` (e.g. `001_init.sql`). Executed in filename order.
+**Format:** `db/NNN_description.sql` (for example, `001_init.sql`). Files are executed in filename order.
 
 **SQLite Type Constraints:**
 
 | Do Not Use | Alternative |
 |-----------|-------------|
 | `BOOLEAN` | `INTEGER` (0 = false, 1 = true) |
-| `DATETIME` / `TIMESTAMP` | `TEXT`, store ISO 8601 (default: `datetime('now')`) |
-| `JSON` type | `TEXT`, use `JSON.stringify()` / `JSON.parse()` |
+| `DATETIME` / `TIMESTAMP` | `TEXT`, stored as ISO 8601 (default: `datetime('now')`) |
+| `JSON` type | `TEXT`, using `JSON.stringify()` / `JSON.parse()` |
 | `VARCHAR(n)` | `TEXT` |
 
-## Capability Limits
+## Template Architecture Suggestions
 
-| Limitation | Alternative |
+| Scenario | Default Suggestion |
 |-----------|-------------|
-| File storage (image uploads) | Store external image URLs, or `pinme upload` then store IPFS link |
-| WebSocket | Polling API (fetch every 5 seconds) |
-| Multiple Workers | Merge into a single Worker with route prefixes |
-| Multiple databases | Merge into one D1 |
+| File storage (image uploads) | Store external image URLs, or upload with `pinme upload` first and then store the resulting link |
+| Real-time communication | This template defaults to regular HTTP APIs. If there is no clear real-time requirement, start with polling |
+| Multiple Workers | This template defaults to combining functionality into a single Worker and separating routes by prefix |
+| Multiple databases | This template defaults to combining data into one D1 database and only splitting when isolation is truly needed |
 
 ## Important Notes
 
-- `pinme.toml`, `backend/wrangler.toml`, `frontend/.env` are auto-generated — do not modify
-- Frontend API URL is obtained via `VITE_WORKER_URL` env var — do not hardcode
-- Passwords, tokens, and API keys must be stored in secrets, never in config files
+- `pinme.toml`, `backend/wrangler.toml`, and `frontend/.env` are generated by PinMe. Do not edit them manually by default. If extra runtime configuration is truly needed, prefer doing it through PinMe-supported mechanisms.
+- Obtain the frontend API URL from the `VITE_API_URL` environment variable. Do not hardcode it.
+- Passwords, tokens, and API keys must be stored in secrets. Never put them in config files.
 
 ## Common Errors
 
 | Error | Solution |
 |-------|----------|
 | `command not found: pinme` | `npm install -g pinme` |
-| `No such file or directory` | Verify the path exists |
-| `Permission denied` | Check file/folder permissions |
-| Upload failed | Check network connection, retry |
-| Not logged in error | Run `pinme login` first |
+| `No such file or directory` | Verify that the path exists |
+| `Permission denied` | Check file or directory permissions |
+| Upload failed | Check the network connection and retry |
+| Not logged in | Run `pinme login` first |
 
 ## Other Commands
 
PATCH

echo "Gold patch applied."
