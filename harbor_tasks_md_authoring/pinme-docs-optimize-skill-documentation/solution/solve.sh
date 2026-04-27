#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pinme

# Idempotency guard
if grep -qF "description: Use this skill when a PinMe project (Worker TypeScript) needs to in" "skills/pinme-api/SKILL.md" && grep -qF "description: Use this skill when the user mentions \"pinme\", or needs to upload f" "skills/pinme/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/pinme-api/SKILL.md b/skills/pinme-api/SKILL.md
@@ -1,36 +1,36 @@
 ---
 name: pinme-api
-description: 当用户的 PinMe 项目（Worker TypeScript）需要集成发送邮件（send_email）或调用大模型 API（chat/completions）时使用此技能。指导 AI 生成正确的 Worker TS 代码。
+description: Use this skill when a PinMe project (Worker TypeScript) needs to integrate email sending (send_email) or LLM API calls (chat/completions). Guides AI to generate correct Worker TS code.
 ---
 
-# PinMe Worker API 集成
+# PinMe Worker API Integration
 
-指导在 PinMe Worker（TypeScript）中调用 PinMe 平台的邮件发送和 LLM API。
+Guides how to call PinMe platform's email sending and LLM APIs in a PinMe Worker (TypeScript).
 
-## 环境变量
+## Environment Variables
 
-Worker 创建时自动注入以下环境变量，无需手动配置：
+The following environment variables are automatically injected when the Worker is created — no manual configuration needed:
 
 ```typescript
 // backend/src/worker.ts
 export interface Env {
   DB: D1Database;
-  API_KEY: string;      // 项目 API Key — 用于 send_email 和 chat/completions 认证
-  BASE_URL?: string;    // 可选覆盖 PinMe API 基础地址，默认 https://pinme.dev
+  API_KEY: string;      // Project API Key — used for send_email and chat/completions authentication
+  BASE_URL?: string;    // Optional override for PinMe API base URL, defaults to https://pinme.dev
 }
 ```
 
-> `API_KEY` 是 Worker 调用 PinMe 平台 API 的唯一凭证。`BASE_URL` 未设置时默认使用 `https://pinme.dev`。
+> `API_KEY` is the sole credential for the Worker to call PinMe platform APIs. When `BASE_URL` is not set, it defaults to `https://pinme.dev`.
 
 ---
 
-## API 1：发送邮件
+## API 1: Send Email
 
-**端点：** `POST {BASE_URL}/api/v4/send_email`
-**认证：** `X-API-Key` header（使用 `env.API_KEY`）
-**发件人：** 自动为 `{project_name}@pinme.dev`
+**Endpoint:** `POST {BASE_URL}/api/v4/send_email`
+**Authentication:** `X-API-Key` header (using `env.API_KEY`)
+**Sender:** Automatically set to `{project_name}@pinme.dev`
 
-### 请求格式
+### Request Format
 
 ```json
 {
@@ -40,28 +40,28 @@ export interface Env {
 }
 ```
 
-| 字段 | 类型 | 必填 | 说明 |
-|------|------|------|------|
-| `to` | string | 是 | 收件人邮箱 |
-| `subject` | string | 是 | 邮件主题 |
-| `html` | string | 是 | HTML 正文 |
+| Field | Type | Required | Description |
+|-------|------|----------|-------------|
+| `to` | string | Yes | Recipient email address |
+| `subject` | string | Yes | Email subject |
+| `html` | string | Yes | HTML body |
 
-### 响应格式
+### Response Format
 
-**成功 (200)：**
+**Success (200):**
 ```json
 { "code": 200, "msg": "ok", "data": { "ok": true } }
 ```
 
-**错误：**
+**Errors:**
 
-| HTTP 状态码 | 含义 | data.error 示例 |
-|-------------|------|-----------------|
-| 401 | API Key 缺失或无效 | `"X-API-Key header is required"` / `"Invalid API key"` |
-| 400 | 参数校验失败 | `"Invalid email address"` / `"Subject is required"` |
-| 500 | 邮件服务异常 | `"Failed to send email"` |
+| HTTP Status | Meaning | data.error Example |
+|-------------|---------|-------------------|
+| 401 | API Key missing or invalid | `"X-API-Key header is required"` / `"Invalid API key"` |
+| 400 | Parameter validation failed | `"Invalid email address"` / `"Subject is required"` |
+| 500 | Email service error | `"Failed to send email"` |
 
-### Worker 示例代码
+### Worker Example Code
 
 ```typescript
 async function sendEmail(env: Env, to: string, subject: string, html: string): Promise<{ ok: boolean; error?: string }> {
@@ -83,7 +83,7 @@ async function sendEmail(env: Env, to: string, subject: string, html: string): P
   return { ok: true };
 }
 
-// 在路由中使用
+// Usage in routes
 async function handleSendVerification(request: Request, env: Env): Promise<Response> {
   const { email } = await request.json() as { email: string };
   const code = Math.random().toString().slice(2, 8);
@@ -100,14 +100,14 @@ async function handleSendVerification(request: Request, env: Env): Promise<Respo
 
 ---
 
-## API 2：LLM Chat Completions
+## API 2: LLM Chat Completions
 
-**端点：** `POST {BASE_URL}/api/v1/chat/completions?project_name={project_name}`
-**认证：** `X-API-Key` header（使用 `env.API_KEY`）
-**请求体：** OpenAI 兼容格式，原样透传给 LLM 服务
-**流式：** 支持 SSE（`stream: true`）
+**Endpoint:** `POST {BASE_URL}/api/v1/chat/completions?project_name={project_name}`
+**Authentication:** `X-API-Key` header (using `env.API_KEY`)
+**Request Body:** OpenAI-compatible format, passed through to LLM service as-is
+**Streaming:** Supports SSE (`stream: true`)
 
-### 请求格式
+### Request Format
 
 ```json
 {
@@ -120,11 +120,11 @@ async function handleSendVerification(request: Request, env: Env): Promise<Respo
 }
 ```
 
-> `project_name` 从 Worker 的子域名解析，见下方示例。模型列表参考 [PinMe LLM 支持的模型](https://openrouter.ai/models)（OpenAI 兼容格式）。
+> `project_name` is parsed from the Worker's subdomain — see example below. For available models, refer to [PinMe LLM Supported Models](https://openrouter.ai/models) (OpenAI-compatible format).
 
-### 响应格式
+### Response Format
 
-**非流式成功 (200)：**
+**Non-streaming Success (200):**
 ```json
 {
   "id": "chatcmpl-...",
@@ -133,26 +133,26 @@ async function handleSendVerification(request: Request, env: Env): Promise<Respo
 }
 ```
 
-**流式成功 (200)：** SSE 格式
+**Streaming Success (200):** SSE format
 ```
 data: {"choices":[{"delta":{"content":"Hello"}}]}
 data: {"choices":[{"delta":{"content":" there"}}]}
 data: [DONE]
 ```
 
-**错误：**
+**Errors:**
 
-| HTTP 状态码 | 含义 | data.error 示例 |
-|-------------|------|-----------------|
-| 401 | API Key 缺失或无效 | `"X-API-Key header is required"` / `"Invalid API key or project name"` |
-| 400 | project_name 缺失或 LLM 未配置 | `"project_name is required"` / `"LLM service not configured for this project"` |
-| 413 | 请求体超过 1MB | `"Request body too large (max 1MB)"` |
-| 502 | LLM 服务不可用 | `"LLM service unavailable"` |
+| HTTP Status | Meaning | data.error Example |
+|-------------|---------|-------------------|
+| 401 | API Key missing or invalid | `"X-API-Key header is required"` / `"Invalid API key or project name"` |
+| 400 | project_name missing or LLM not configured | `"project_name is required"` / `"LLM service not configured for this project"` |
+| 413 | Request body exceeds 1MB | `"Request body too large (max 1MB)"` |
+| 502 | LLM service unavailable | `"LLM service unavailable"` |
 
-### Worker 示例代码 — 非流式
+### Worker Example Code — Non-streaming
 
 ```typescript
-// 获取 project_name：从 Worker 的子域名解析
+// Get project_name: parsed from the Worker's subdomain
 function getProjectName(request: Request): string {
   const host = new URL(request.url).hostname; // e.g. "my-app-1a2b.pinme.pro"
   return host.split('.')[0];
@@ -186,7 +186,7 @@ async function callLLM(
   return { content: data.choices[0]?.message?.content || '' };
 }
 
-// 在路由中使用
+// Usage in routes
 async function handleChat(request: Request, env: Env): Promise<Response> {
   const { question } = await request.json() as { question: string };
   const projectName = getProjectName(request);
@@ -203,15 +203,15 @@ async function handleChat(request: Request, env: Env): Promise<Response> {
 }
 ```
 
-### Worker 示例代码 — 流式（SSE 透传）
+### Worker Example Code — Streaming (SSE Passthrough)
 
 ```typescript
 async function handleChatStream(request: Request, env: Env): Promise<Response> {
   const body = await request.text();
   const projectName = getProjectName(request);
   const baseUrl = env.BASE_URL ?? 'https://pinme.dev';
 
-  // 确保请求中 stream=true
+  // Ensure stream=true in the request
   let parsed = JSON.parse(body);
   parsed.stream = true;
 
@@ -232,7 +232,7 @@ async function handleChatStream(request: Request, env: Env): Promise<Response> {
     return json({ error: err.data?.error || `HTTP ${resp.status}` }, resp.status);
   }
 
-  // 直接透传 SSE 流
+  // Pass through SSE stream directly
   return new Response(resp.body, {
     status: 200,
     headers: {
@@ -245,7 +245,7 @@ async function handleChatStream(request: Request, env: Env): Promise<Response> {
 }
 ```
 
-### 前端消费 SSE 流示例
+### Frontend SSE Stream Consumer Example
 
 ```typescript
 async function streamChat(question: string, onChunk: (text: string) => void): Promise<void> {
@@ -265,7 +265,7 @@ async function streamChat(question: string, onChunk: (text: string) => void): Pr
 
     buffer += decoder.decode(value, { stream: true });
     const lines = buffer.split('\n');
-    buffer = lines.pop()!; // 保留不完整的行
+    buffer = lines.pop()!; // Keep incomplete line
 
     for (const line of lines) {
       if (!line.startsWith('data: ')) continue;
@@ -282,19 +282,19 @@ async function streamChat(question: string, onChunk: (text: string) => void): Pr
 
 ---
 
-## 错误处理模式
+## Error Handling Patterns
 
-PinMe 平台 API 统一响应格式：
+PinMe platform API unified response format:
 
 ```typescript
 interface PinmeResponse<T = unknown> {
-  code: number;   // 200=成功，其他=失败
+  code: number;   // 200=success, other=failure
   msg: string;    // "ok" | "error" | "invalid params"
-  data?: T;       // 成功时为业务数据，失败时可能含 { error: string }
+  data?: T;       // Business data on success, may contain { error: string } on failure
 }
 ```
 
-### 推荐的统一错误处理
+### Recommended Unified Error Handler
 
 ```typescript
 async function callPinmeAPI<T>(url: string, apiKey: string, body: unknown): Promise<{ data?: T; error?: string }> {
@@ -330,19 +330,19 @@ async function callPinmeAPI<T>(url: string, apiKey: string, body: unknown): Prom
 }
 ```
 
-### 使用示例
+### Usage Examples
 
 ```typescript
 const baseUrl = env.BASE_URL ?? 'https://pinme.dev';
 
-// 发邮件
+// Send email
 const emailResult = await callPinmeAPI<{ ok: boolean }>(
   `${baseUrl}/api/v4/send_email`, env.API_KEY,
   { to: 'user@example.com', subject: 'Hello', html: '<p>Hi</p>' },
 );
 if (emailResult.error) return json({ error: emailResult.error }, 500);
 
-// 调 LLM（非流式）
+// Call LLM (non-streaming)
 const llmResult = await callPinmeAPI<{ choices: Array<{ message: { content: string } }> }>(
   `${baseUrl}/api/v1/chat/completions?project_name=${projectName}`, env.API_KEY,
   { model: 'openai/gpt-4o-mini', messages: [{ role: 'user', content: 'Hi' }] },
diff --git a/skills/pinme/SKILL.md b/skills/pinme/SKILL.md
@@ -1,140 +1,143 @@
 ---
 name: pinme
-description: 当用户提到 "pinme"，或需要上传文件、存储到 IPFS、创建/发布/部署网站或全栈服务（含前端页面、后端API、数据库存储、邮件发送等）以及任何需要后端数据库/服务器支持的功能时使用此技能。
+description: Use this skill when the user mentions "pinme", or needs to upload files, store to IPFS, create/publish/deploy websites or full-stack services (including frontend pages, backend APIs, database storage, email sending, etc.), or any feature requiring backend database/server support.
 ---
 
 # PinMe
 
-零配置部署工具：将静态文件上传到 IPFS，或创建并部署全栈 Web 项目（React+Vite + Cloudflare Worker + D1 数据库）。Worker 还支持通过 Pinme 平台 API 发送邮件。
+Zero-config deployment tool: upload static files to IPFS, or create and deploy full-stack web projects (React+Vite + Cloudflare Worker + D1 database). Workers also support sending emails via the PinMe platform API.
 
-## 何时使用
+## When to Use
 
 ```dot
 digraph pinme_decision {
-    "用户请求" [shape=doublecircle];
-    "需要后端 API 或数据库？" [shape=diamond];
-    "上传文件（路径 1）" [shape=box];
-    "全栈项目（路径 2）" [shape=box];
-
-    "用户请求" -> "需要后端 API 或数据库？";
-    "需要后端 API 或数据库？" -> "上传文件（路径 1）" [label="否"];
-    "需要后端 API 或数据库？" -> "全栈项目（路径 2）" [label="是"];
+    "User Request" [shape=doublecircle];
+    "Needs backend API or database?" [shape=diamond];
+    "Upload Files (Path 1)" [shape=box];
+    "Full-Stack Project (Path 2)" [shape=box];
+
+    "User Request" -> "Needs backend API or database?";
+    "Needs backend API or database?" -> "Upload Files (Path 1)" [label="No"];
+    "Needs backend API or database?" -> "Full-Stack Project (Path 2)" [label="Yes"];
 }
 ```
 
-## 路径 1：上传文件 / 静态站点
+## Path 1: Upload Files / Static Sites
 
-> 无需登录。
+> No login required.
 
 ```dot
 digraph upload_flow {
-    "检查 pinme 是否已安装" [shape=box];
-    "确定构建产物" [shape=box];
+    "Install/update pinme to latest" [shape=box];
+    "Determine build artifacts" [shape=box];
     "pinme upload <path>" [shape=box];
-    "返回预览 URL" [shape=doublecircle];
+    "Return preview URL" [shape=doublecircle];
 
-    "检查 pinme 是否已安装" -> "确定构建产物";
-    "确定构建产物" -> "pinme upload <path>";
-    "pinme upload <path>" -> "返回预览 URL";
+    "Install/update pinme to latest" -> "Determine build artifacts";
+    "Determine build artifacts" -> "pinme upload <path>";
+    "pinme upload <path>" -> "Return preview URL";
 }
 ```
 
-**1. 检查安装：**
+**1. Check installation and update to latest:**
 ```bash
-pinme --version
-# 如未安装：npm install -g pinme
+LOCAL=$(pinme --version 2>/dev/null || echo "0.0.0")
+LATEST=$(npm view pinme version)
+[ "$LOCAL" != "$LATEST" ] && npm install -g pinme@latest || echo "pinme is up to date ($LOCAL)"
 ```
 
-**2. 确定上传目标**（优先级顺序）：
+**2. Determine upload target** (priority order):
 1. `dist/` — Vite / Vue / React
 2. `build/` — Create React App
-3. `out/` — Next.js 静态导出
-4. `public/` — 纯静态文件
+3. `out/` — Next.js static export
+4. `public/` — Plain static files
 
-**3. 上传：**
+**3. Upload:**
 ```bash
 pinme upload <path>
-pinme upload ./dist --domain my-site  # 可选：绑定子域名（需 VIP）
+pinme upload ./dist --domain my-site  # Optional: bind subdomain (VIP required)
 ```
 
-**4. 返回**预览 URL（`https://pinme.eth.limo/#/preview/*`）给用户。注意：返回 **完整的 URL**，包含全部 hash 字符，不要截断。
+**4. Return** the preview URL (`https://pinme.eth.limo/#/preview/*`) to the user. Note: return the **full URL** including all hash characters — do not truncate.
 
-### 常见示例
+### Common Examples
 
 ```bash
-pinme upload ./document.pdf          # 单个文件
-pinme upload ./my-folder             # 文件夹
-pinme upload dist                    # Vite/Vue 构建产物
-pinme upload build                   # CRA 构建产物
-pinme upload out                     # Next.js 静态导出
-pinme upload ./dist --domain my-site # 绑定 Pinme 子域名（需 VIP）
-pinme import ./my-archive.car        # 导入 CAR 文件
+pinme upload ./document.pdf          # Single file
+pinme upload ./my-folder             # Folder
+pinme upload dist                    # Vite/Vue build artifacts
+pinme upload build                   # CRA build artifacts
+pinme upload out                     # Next.js static export
+pinme upload ./dist --domain my-site # Bind PinMe subdomain (VIP required)
+pinme import ./my-archive.car        # Import CAR file
 ```
 
-### 不要上传
-- `node_modules/`、`.env`、`.git/`、`src/`
-- 只上传构建产物，不要上传源代码
+### Do NOT Upload
+- `node_modules/`, `.env`, `.git/`, `src/`
+- Only upload build artifacts, never upload source code
 
 ---
 
-## 路径 2：全栈项目
+## Path 2: Full-Stack Project
 
-> 需要登录。使用 React+Vite 前端 + Cloudflare Worker 后端 + D1 SQLite 数据库。
+> Login required. Uses React+Vite frontend + Cloudflare Worker backend + D1 SQLite database.
 
 ```dot
 digraph fullstack_flow {
+    "Install/update pinme to latest" [shape=box];
     "pinme login" [shape=box];
     "pinme create <name>" [shape=box];
-    "修改模板代码" [shape=box];
+    "Modify template code" [shape=box];
     "pinme save" [shape=box];
-    "返回预览 URL" [shape=doublecircle];
+    "Return preview URL" [shape=doublecircle];
 
+    "Install/update pinme to latest" -> "pinme login";
     "pinme login" -> "pinme create <name>";
-    "pinme create <name>" -> "修改模板代码";
-    "修改模板代码" -> "pinme save";
-    "pinme save" -> "返回预览 URL";
+    "pinme create <name>" -> "Modify template code";
+    "Modify template code" -> "pinme save";
+    "pinme save" -> "Return preview URL";
 }
 ```
 
-### 架构
+### Architecture
 
-| 层级 | 技术栈 | 部署目标 |
-|------|--------|----------|
-| 前端 | React + Vite（`frontend/`） | IPFS |
-| 后端 | Cloudflare Worker（`backend/src/worker.ts`） | `{name}.pinme.pro` |
-| 数据库 | D1 SQLite（`db/*.sql`） | Cloudflare D1 |
+| Layer | Tech Stack | Deploy Target |
+|-------|-----------|---------------|
+| Frontend | React + Vite (`frontend/`) | IPFS |
+| Backend | Cloudflare Worker (`backend/src/worker.ts`) | `{name}.pinme.pro` |
+| Database | D1 SQLite (`db/*.sql`) | Cloudflare D1 |
 
-### 核心命令
+### Core Commands
 
 ```bash
-pinme login                  # 登录（仅需一次）
-pinme create <dirName>       # 克隆模板并创建项目（自动填充 API URL）
-pinme save                   # 首次部署 / 完整更新（前端 + 后端 + 数据库，一条命令）
-pinme update-worker          # 仅更新后端（当只修改了 backend/src/worker.ts）
-pinme update-web             # 仅更新前端（当只修改了 frontend/src/）
-pinme update-db              # 仅执行 SQL 迁移（当只修改了 db/）
+pinme login                  # Login (only needed once)
+pinme create <dirName>       # Clone template and create project (auto-fills API URL)
+pinme save                   # First deploy / full update (frontend + backend + database, single command)
+pinme update-worker          # Update backend only (when only backend/src/worker.ts was modified)
+pinme update-web             # Update frontend only (when only frontend/src/ was modified)
+pinme update-db              # Run SQL migrations only (when only db/ was modified)
 ```
 
-> `pinme save` 会一次性部署前端 + 后端 + 数据库。只有确定仅修改了某一部分时才使用 `pinme update-*`。
+> `pinme save` deploys frontend + backend + database all at once. Only use `pinme update-*` when you're certain only one part was modified.
 
-### 项目结构
+### Project Structure
 
 ```
 {project}/
-├── pinme.toml              # 根配置（自动生成，请勿修改）
-├── package.json            # Monorepo 根目录（workspaces: frontend + backend）
+├── pinme.toml              # Root config (auto-generated, do not modify)
+├── package.json            # Monorepo root (workspaces: frontend + backend)
 ├── backend/
-│   ├── wrangler.toml       # Worker 配置（自动生成，请勿修改）
+│   ├── wrangler.toml       # Worker config (auto-generated, do not modify)
 │   ├── package.json
 │   └── src/
-│       └── worker.ts       # 后端入口 — 仅提供 JSON API
+│       └── worker.ts       # Backend entry — JSON API only
 ├── db/
-│   └── 001_init.sql        # SQL 表定义
+│   └── 001_init.sql        # SQL table definitions
 ├── frontend/
 │   ├── package.json
-│   ├── vite.config.ts      # 开发代理：/api → localhost:8787
+│   ├── vite.config.ts      # Dev proxy: /api → localhost:8787
 │   ├── index.html
-│   ├── .env                # 自动生成：VITE_WORKER_URL（请勿修改）
+│   ├── .env                # Auto-generated: VITE_WORKER_URL (do not modify)
 │   └── src/
 │       ├── main.tsx
 │       ├── App.tsx
@@ -146,53 +149,56 @@ pinme update-db              # 仅执行 SQL 迁移（当只修改了 db/）
 └── .gitignore
 ```
 
-### 首次部署
+### First Deployment
 
 ```bash
+LOCAL=$(pinme --version 2>/dev/null || echo "0.0.0")
+LATEST=$(npm view pinme version)
+[ "$LOCAL" != "$LATEST" ] && npm install -g pinme@latest
 pinme login
 pinme create my-app
 cd my-app
 ```
 
-`pinme create` 会生成一个可运行的 Hello World 模板（包含前端页面 + 后端 API 路由 + 数据库表结构）。**修改模板**以匹配用户的业务逻辑 — 不要从零开始编写：
+`pinme create` generates a working Hello World template (includes frontend page + backend API routes + database schema). **Modify the template** to match the user's business logic — do not write from scratch:
 
-- 修改 `backend/src/worker.ts` — 替换 API 路由
-- 修改 `frontend/src/pages/` — 替换页面组件
-- 修改 `db/001_init.sql` — 替换表定义
+- Modify `backend/src/worker.ts` — replace API routes
+- Modify `frontend/src/pages/` — replace page components
+- Modify `db/001_init.sql` — replace table definitions
 
 ```bash
 pinme save
-# 一条命令部署前端 + 后端 + 数据库
-# 输出预览 URL：https://pinme.eth.limo/#/preview/{CID}
+# Single command deploys frontend + backend + database
+# Outputs preview URL: https://pinme.eth.limo/#/preview/{CID}
 ```
 
-**返回**预览 URL 给用户。注意：返回 **完整的 URL**，包含全部 hash 字符，不要截断。
+**Return** the preview URL to the user. Note: return the **full URL** including all hash characters — do not truncate.
 
-后端 Worker 部署在 `https://{name}.pinme.pro`。前端 API 请求会自动配置指向该地址 — 无需手动设置。
+The backend Worker is deployed at `https://{name}.pinme.pro`. Frontend API requests are automatically configured to point to that address — no manual setup needed.
 
-### 后续更新
+### Subsequent Updates
 
-| 修改内容 | 命令 | 说明 |
-|----------|------|------|
-| 仅后端（`backend/src/worker.ts`） | `pinme update-worker` | 更快 |
-| 仅前端（`frontend/src/`） | `pinme update-web` | 生成新 CID |
-| 仅数据库（`db/`） | `pinme update-db` | 执行新迁移 |
-| 多处修改或不确定 | `pinme save` | 安全的完整部署 |
+| Changes | Command | Notes |
+|---------|---------|-------|
+| Backend only (`backend/src/worker.ts`) | `pinme update-worker` | Faster |
+| Frontend only (`frontend/src/`) | `pinme update-web` | Generates new CID |
+| Database only (`db/`) | `pinme update-db` | Runs new migrations |
+| Multiple changes or uncertain | `pinme save` | Safe full deployment |
 
-> 每次前端部署会生成新的 CID 和预览 URL。旧 URL 仍可访问。
+> Each frontend deployment generates a new CID and preview URL. Old URLs remain accessible.
 
 ---
 
-## Worker 代码模式（backend/src/worker.ts）
+## Worker Code Patterns (backend/src/worker.ts)
 
-Worker 后端仅编写 JSON API。**不允许使用 npm 包**（不能用 hono、express 等）。手写路由：
+The Worker backend only serves JSON APIs. **No npm packages allowed** (no hono, express, etc.). Write routes manually:
 
 ```typescript
 export interface Env {
-  DB: D1Database;           // 使用数据库时
-  API_KEY?: string;         // 使用邮件发送时
-  JWT_SECRET: string;       // 使用 JWT 认证时
-  ADMIN_PASSWORD: string;   // 使用密码认证时
+  DB: D1Database;           // When using database
+  API_KEY?: string;         // When using email sending
+  JWT_SECRET: string;       // When using JWT auth
+  ADMIN_PASSWORD: string;   // When using password auth
 }
 
 const CORS_HEADERS = {
@@ -223,33 +229,33 @@ export default {
 };
 ```
 
-### Worker 限制
+### Worker Restrictions
 
-| 禁止 | 替代方案 |
-|------|----------|
-| `import from 'hono'` 或任何 npm 包 | 手写路由（`if pathname === '/api/...'`） |
-| `import fs from 'fs'` / Node.js 内置模块 | Web API：`crypto`、`fetch`、`URL` 等 |
-| `require()` 语法 | 仅使用 ESM `import` |
-| Worker 返回 HTML | 仅返回 JSON API |
-| 明文存储密码 | 存储前使用 SHA-256 哈希 |
-| SQL 字符串拼接 | 使用 `.bind()` 参数化查询 |
+| Prohibited | Alternative |
+|-----------|-------------|
+| `import from 'hono'` or any npm package | Manual routing (`if pathname === '/api/...'`) |
+| `import fs from 'fs'` / Node.js built-in modules | Web APIs: `crypto`, `fetch`, `URL`, etc. |
+| `require()` syntax | ESM `import` only |
+| Worker returning HTML | JSON API only |
+| Storing passwords in plaintext | Hash with SHA-256 before storing |
+| SQL string concatenation | Use `.bind()` parameterized queries |
 
-### 邮件 API 参考（用于 Worker 后端）
+### Email API Reference (for Worker Backend)
 
-当后端需要邮件发送功能时，使用 Pinme 平台 API（`https://pinme.dev/api/v4/send_email`）。
+When the backend needs email sending capability, use the PinMe platform API (`https://pinme.dev/api/v4/send_email`).
 
-**1. 配置 API_KEY**
+**1. Configure API_KEY**
 
-添加到 `Env` 接口：
+Add to the `Env` interface:
 
 ```typescript
 export interface Env {
   DB: D1Database;
-  API_KEY?: string;  // 邮件发送必需
+  API_KEY?: string;  // Required for email sending
 }
 ```
 
-**2. 邮件处理代码**
+**2. Email Handler Code**
 
 ```typescript
 async function handleSendEmail(request: Request, env: Env): Promise<Response> {
@@ -291,86 +297,86 @@ async function handleSendEmail(request: Request, env: Env): Promise<Response> {
 }
 ```
 
-## 前端 API 工具（frontend/src/utils/api.ts）
+## Frontend API Utility (frontend/src/utils/api.ts)
 
 ```typescript
-// 开发环境：Vite 代理 /api → localhost:8787
-// 生产环境：VITE_WORKER_URL 由 pinme create 自动注入
+// Development: Vite proxies /api → localhost:8787
+// Production: VITE_WORKER_URL is auto-injected by pinme create
 export const API = import.meta.env.VITE_WORKER_URL || '';
 
 export function getApiUrl(path: string): string {
   return API ? `${API}${path}` : path;
 }
 ```
 
-## D1 数据库操作
+## D1 Database Operations
 
 ```typescript
-// 查询多行
+// Query multiple rows
 const { results } = await env.DB.prepare('SELECT * FROM t WHERE x = ?').bind(val).all();
 
-// 查询单行（未找到返回 null）
+// Query single row (returns null if not found)
 const row = await env.DB.prepare('SELECT * FROM t WHERE id = ?').bind(id).first();
 
-// 插入并返回新行
+// Insert and return new row
 const row = await env.DB.prepare('INSERT INTO t (a, b) VALUES (?, ?) RETURNING *').bind(a, b).first();
 
-// 更新
+// Update
 await env.DB.prepare('UPDATE t SET a = ? WHERE id = ?').bind(val, id).run();
 
-// 删除（检查是否命中）
+// Delete (check if affected)
 const { meta } = await env.DB.prepare('DELETE FROM t WHERE id = ?').bind(id).run();
 if (meta.changes === 0) return json({ error: 'Not found' }, 404);
 ```
 
-### SQL 迁移文件
+### SQL Migration Files
 
-**格式：** `db/NNN_description.sql`（例如 `001_init.sql`）。按文件名顺序执行。
+**Format:** `db/NNN_description.sql` (e.g. `001_init.sql`). Executed in filename order.
 
-**SQLite 类型约束：**
+**SQLite Type Constraints:**
 
-| 不能使用 | 替代方案 |
-|----------|----------|
-| `BOOLEAN` | `INTEGER`（0 = false，1 = true） |
-| `DATETIME` / `TIMESTAMP` | `TEXT`，存储 ISO 8601（默认：`datetime('now')`） |
-| `JSON` 类型 | `TEXT`，使用 `JSON.stringify()` / `JSON.parse()` |
+| Do Not Use | Alternative |
+|-----------|-------------|
+| `BOOLEAN` | `INTEGER` (0 = false, 1 = true) |
+| `DATETIME` / `TIMESTAMP` | `TEXT`, store ISO 8601 (default: `datetime('now')`) |
+| `JSON` type | `TEXT`, use `JSON.stringify()` / `JSON.parse()` |
 | `VARCHAR(n)` | `TEXT` |
 
-## 能力边界
+## Capability Limits
 
-| 限制 | 替代方案 |
-|------|----------|
-| 文件存储（图片上传） | 存储外部图片 URL，或 `pinme upload` 后存储 IPFS 链接 |
-| WebSocket | 轮询 API（每 5 秒 fetch 一次） |
-| 多个 Worker | 合并为单个 Worker，使用路由前缀区分 |
-| 多个数据库 | 合并为一个 D1 |
+| Limitation | Alternative |
+|-----------|-------------|
+| File storage (image uploads) | Store external image URLs, or `pinme upload` then store IPFS link |
+| WebSocket | Polling API (fetch every 5 seconds) |
+| Multiple Workers | Merge into a single Worker with route prefixes |
+| Multiple databases | Merge into one D1 |
 
-## 重要提示
+## Important Notes
 
-- `pinme.toml`、`backend/wrangler.toml`、`frontend/.env` 为自动生成 — 请勿修改
-- 前端 API URL 通过 `VITE_WORKER_URL` 环境变量获取 — 请勿硬编码
-- 密码、令牌、API 密钥必须放在 secrets 中，不要写在配置文件里
+- `pinme.toml`, `backend/wrangler.toml`, `frontend/.env` are auto-generated — do not modify
+- Frontend API URL is obtained via `VITE_WORKER_URL` env var — do not hardcode
+- Passwords, tokens, and API keys must be stored in secrets, never in config files
 
-## 常见错误
+## Common Errors
 
-| 错误 | 解决方案 |
-|------|----------|
+| Error | Solution |
+|-------|----------|
 | `command not found: pinme` | `npm install -g pinme` |
-| `No such file or directory` | 确认路径是否存在 |
-| `Permission denied` | 检查文件/文件夹权限 |
-| 上传失败 | 检查网络连接，重试 |
-| 未登录错误 | 先运行 `pinme login` |
+| `No such file or directory` | Verify the path exists |
+| `Permission denied` | Check file/folder permissions |
+| Upload failed | Check network connection, retry |
+| Not logged in error | Run `pinme login` first |
 
-## 其他命令
+## Other Commands
 
 ```bash
-pinme list / pinme ls -l 5     # 查看上传历史
-pinme list -c                  # 清除上传历史
-pinme rm <hash>                # 删除已上传内容
-pinme bind <path> --domain <domain>  # 绑定域名（需 VIP + AppKey）
-pinme export <CID>             # 导出为 CAR 文件
-pinme set-appkey               # 设置/查看 AppKey
-pinme my-domains               # 列出已绑定域名
-pinme delete <project>          # 删除项目（Worker + 域名 + D1）
-pinme logout                   # 退出登录
-```
\ No newline at end of file
+pinme list / pinme ls -l 5     # View upload history
+pinme list -c                  # Clear upload history
+pinme rm <hash>                # Delete uploaded content
+pinme bind <path> --domain <domain>  # Bind domain (VIP + AppKey required)
+pinme export <CID>             # Export as CAR file
+pinme set-appkey               # Set/view AppKey
+pinme my-domains               # List bound domains
+pinme delete <project>          # Delete project (Worker + domain + D1)
+pinme logout                   # Log out
+```
PATCH

echo "Gold patch applied."
