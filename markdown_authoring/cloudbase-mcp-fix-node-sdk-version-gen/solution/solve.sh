#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "\u26a0\ufe0f **Node SDK AI feature requires version 3.16.0 or above.** Check your version " "config/.claude/skills/ai-model-cloudbase/SKILL.md" && grep -qF "- **AI Model Calling**: `rules/ai-model-cloudbase/rule.md` - Call AI models (Hun" "config/.cursor/rules/cloudbase-rules.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/config/.claude/skills/ai-model-cloudbase/SKILL.md b/config/.claude/skills/ai-model-cloudbase/SKILL.md
@@ -13,7 +13,7 @@ Use this skill for **calling AI models using CloudBase** across all platforms.
 | Platform | SDK/API | Section |
 |----------|---------|---------|
 | Web (Browser) | `@cloudbase/js-sdk` | Part 1 |
-| Node.js (Server/Cloud Functions) | `@cloudbase/node-sdk` | Part 1 (same API, different init) |
+| Node.js (Server/Cloud Functions) | `@cloudbase/node-sdk` ≥3.16.0 | Part 1 (same API, different init) |
 | Any platform (HTTP) | HTTP API / OpenAI SDK | Part 2 |
 | WeChat Mini Program | `wx.cloud.extend.AI` | Part 3 ⚠️ Different API |
 
@@ -38,10 +38,12 @@ Use this skill for **calling AI models using CloudBase** across all platforms.
 # For Web (Browser)
 npm install @cloudbase/js-sdk
 
-# For Node.js (Server/Cloud Functions) - Requires v3.16.0+
+# For Node.js (Server/Cloud Functions)
 npm install @cloudbase/node-sdk
 ```
 
+⚠️ **Node SDK AI feature requires version 3.16.0 or above.** Check your version with `npm list @cloudbase/node-sdk`.
+
 ## Initialization - Web (JS SDK)
 
 ```js
@@ -113,7 +115,10 @@ const usage = await res.usage;        // Token usage
 
 ## generateImage() - Image Generation
 
+⚠️ **Image generation is currently only available in Node SDK**, not in JS SDK (Web) or WeChat Mini Program.
+
 ```js
+// Node SDK only
 const imageModel = ai.createImageModel("hunyuan-image");
 
 const res = await imageModel.generateImage({
@@ -263,7 +268,7 @@ for await (let event of res.eventStream) {
 | **streamText params** | Direct object | ⚠️ Wrapped in `data: {...}` |
 | **streamText return** | `{ textStream, dataStream }` | `{ textStream, eventStream }` |
 | **Callbacks** | Not supported | `onText`, `onEvent`, `onFinish` |
-| **Image generation** | `ai.createImageModel()` | Not available |
+| **Image generation** | Node SDK only | Not available |
 
 ---
 
diff --git a/config/.cursor/rules/cloudbase-rules.mdc b/config/.cursor/rules/cloudbase-rules.mdc
@@ -42,6 +42,7 @@ When this document references a rule file, try locations in this order:
 | `ui-design` | UI Design Guidelines |
 | `spec-workflow` | Software Engineering Workflow |
 | `data-model-creation` | Data Model Creation |
+| `ai-model-cloudbase` | AI Model Calling (CloudBase) |
 
 ### Usage Example
 
@@ -91,6 +92,7 @@ When you see "Read `{auth-web}` rule file" in this document:
    - **MUST read** `{auth-tool}` rule file (using path resolution strategy) - Authentication configuration
 5. **Optional Rules**:
    - `rules/cloudbase-platform/rule.md` - Universal CloudBase platform knowledge
+   - `rules/ai-model-cloudbase/rule.md` - AI model calling (text generation, streaming, image generation via Node SDK ≥3.16.0)
    - `rules/ui-design/rule.md` - UI design guidelines (if UI is involved)
 6. **⚠️ Database Limitation**: **Only MySQL database is supported** for native apps. If users need to use MySQL database, **MUST prompt them to enable it in the console first**:
    - Enable MySQL database at: [CloudBase Console - MySQL Database](https://tcb.cloud.tencent.com/dev?envId=${envId}#/db/mysql/table/default/)
@@ -214,6 +216,7 @@ Identify current development scenario type, mainly for understanding project typ
 - **CloudRun Projects**: CloudBase Run backend service projects (supports any language: Java/Go/Python/Node.js/PHP/.NET, etc.)
 - **Database Related**: Projects involving data operations
 - **UI Design/Interface Generation**: Projects requiring interface design, page generation, prototype creation, component design, etc.
+- **AI Model Integration**: Projects requiring AI capabilities (text generation, streaming responses, image generation)
 
 ### 2. Platform-Specific Quick Guide
 
@@ -225,13 +228,15 @@ Identify current development scenario type, mainly for understanding project typ
 - `rules/relational-database-tool/rule.md` - MySQL database management (tools)
 - `rules/cloud-storage-web/rule.md` - Cloud storage operations (upload, download, file management)
 - `rules/cloudbase-platform/rule.md` - Universal CloudBase platform knowledge
+   - `rules/ai-model-cloudbase/rule.md` - AI model calling (text generation, streaming, image generation via Node SDK ≥3.16.0)
 
 **Mini Program Projects - Required Rule Files:**
 - `rules/miniprogram-development/rule.md` - Platform development rules (project structure, WeChat Developer Tools, wx.cloud)
 - `rules/auth-wechat/rule.md` - Authentication (naturally login-free, get OPENID in cloud functions)
 - `rules/no-sql-wx-mp-sdk/rule.md` - NoSQL database operations
 - `rules/relational-database-tool/rule.md` - MySQL database operations (via tools)
 - `rules/cloudbase-platform/rule.md` - Universal CloudBase platform knowledge
+   - `rules/ai-model-cloudbase/rule.md` - AI model calling (text generation, streaming, image generation via Node SDK ≥3.16.0)
 
 **Native App Projects (iOS/Android/Flutter/React Native/etc.) - Required Rule Files:**
 - **⚠️ `rules/http-api/rule.md`** - **MANDATORY** - HTTP API usage for all CloudBase operations (SDK not supported)
@@ -240,6 +245,7 @@ Identify current development scenario type, mainly for understanding project typ
 
 **Native App Projects (iOS/Android/Flutter/React Native/etc.) - Optional Rule Files:**
 - `rules/cloudbase-platform/rule.md` - Universal CloudBase platform knowledge
+   - `rules/ai-model-cloudbase/rule.md` - AI model calling (text generation, streaming, image generation via Node SDK ≥3.16.0)
 - `rules/ui-design/rule.md` - UI design guidelines (if UI is involved)
 
 **Universal Rule Files (All Projects):**
@@ -367,6 +373,9 @@ For example, many interfaces require a confirm parameter, which is a boolean typ
 ### Storage Skills
 - **Cloud Storage (Web)**: `rules/cloud-storage-web/rule.md` - Upload, download, temporary URLs, file management using Web SDK
 
+### AI Skills
+- **AI Model Calling**: `rules/ai-model-cloudbase/rule.md` - Call AI models (Hunyuan, DeepSeek) via CloudBase JS/Node SDK, HTTP API, and WeChat Mini Program. Supports text generation, streaming, and image generation (Node SDK only, requires ≥3.16.0)
+
 ### 🎨 ⚠️ UI Design Skill (CRITICAL - Read FIRST)
 - **`rules/ui-design/rule.md`** - **MANDATORY - HIGHEST PRIORITY**
   - **MUST read FIRST before generating ANY interface/page/component/style**
@@ -383,7 +392,7 @@ To ensure development quality, recommend completing the following checks before
 ### Recommended Steps
 0. **[ ] Environment Check**: Call `envQuery` tool to check CloudBase environment status (applies to all interactions)
 1. **[ ] Template Download Check (MANDATORY for New Projects)**: If starting a new project, have you called `downloadTemplate` tool FIRST? Do NOT manually create project files - use templates.
-2. **[ ] Scenario Identification**: Clearly identify what type of project this is (Web/Mini Program/Database/UI)
+2. **[ ] Scenario Identification**: Clearly identify what type of project this is (Web/Mini Program/Database/UI/AI)
 3. **[ ] Core Capability Confirmation**: Confirm all four core capabilities have been considered
    - UI Design: Have you explicitly read the file `rules/ui-design/rule.md` using file reading tools?
    - Database + Authentication: Have you referred to corresponding authentication and database skills?
PATCH

echo "Gold patch applied."
