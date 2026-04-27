#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "The CloudBase console changes frequently. If a logged-in console shows a differe" "config/source/guideline/cloudbase/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/config/source/guideline/cloudbase/SKILL.md b/config/source/guideline/cloudbase/SKILL.md
@@ -283,39 +283,6 @@ For better UI/UX design, consider reading the `ui-design` skill which provides:
 
 ---
 
-## Platform-Specific Skills
-
-### Web Projects
-- `web-development` - SDK integration, static hosting, build configuration
-- `auth-web` - Web SDK built-in authentication
-- `no-sql-web-sdk` - NoSQL database operations
-- `relational-database-web` - MySQL database operations (Web)
-- `relational-database-tool` - MySQL database management
-- `cloud-storage-web` - Cloud storage operations
-- `ai-model-web` - AI model calling for Web apps
-
-### Mini Program Projects
-- `miniprogram-development` - Project structure, WeChat Developer Tools, wx.cloud
-- `auth-wechat` - Authentication (naturally login-free)
-- `no-sql-wx-mp-sdk` - NoSQL database operations
-- `relational-database-tool` - MySQL database operations
-- `ai-model-wechat` - AI model calling for Mini Program
-
-### Native App Projects
-- `http-api` - HTTP API usage (MANDATORY - SDK not supported)
-- `relational-database-tool` - MySQL database operations (MANDATORY)
-- `auth-tool` - Authentication configuration
-
-### Universal Skills
-- `cloudbase-platform` - Universal CloudBase platform knowledge
-- `ui-design` - UI design guidelines (recommended)
-- `spec-workflow` - Standard software engineering process
-
-### Agent Skills
-- `cloudbase-agent` - Build and deploy AI agents with AG-UI protocol (TypeScript & Python)
-
----
-
 ## Professional Skill Reference
 
 ### Platform Development Skills
@@ -408,22 +375,24 @@ When users request deployment to CloudBase:
 
 ## CloudBase Console Entry Points
 
-After creating/deploying resources, provide corresponding console management page links. All console URLs follow the pattern: `https://tcb.cloud.tencent.com/dev?envId=${envId}#/{path}`.
-
-The CloudBase console changes frequently. If a logged-in console shows a different hash path from this list, prefer the live console path and update the source skill docs instead of copying stale URLs forward.
-
-### Core Function Entry Points
-1. **Overview (概览)**: `#/overview` - Main dashboard
-2. **Template Center (模板中心)**: `#/cloud-template/market` - Project templates
-3. **Document Database (文档型数据库)**: `#/db/doc` - NoSQL collections: `#/db/doc/collection/${collectionName}`, Models: `#/db/doc/model/${modelName}`
-4. **MySQL Database (MySQL 数据库)**: `#/db/mysql` - Tables: `#/db/mysql/table/default/`
-5. **Cloud Functions (云函数)**: `#/scf` - Function detail: `#/scf/detail?id=${functionName}&NameSpace=${envId}`
-6. **CloudRun (云托管)**: `#/platform-run` - Container services
-7. **Cloud Storage (云存储)**: `#/storage` - File storage
-8. **AI+**: `#/ai` - AI capabilities
-9. **Static Website Hosting (静态网站托管)**: `#/static-hosting`
-10. **Identity Authentication (身份认证)**: `#/identity` - Login: `#/identity/login-manage`, Tokens: `#/identity/token-management`
-11. **Weida Low-Code (微搭低代码)**: `#/lowcode/apps`
-12. **Logs & Monitoring (日志监控)**: `#/devops/log`
-13. **Extensions (扩展功能)**: `#/apis`
-14. **Environment Settings (环境配置)**: `#/env/http-access`
+After creating or deploying resources, provide the corresponding console management link. All console URLs follow the pattern: `https://tcb.cloud.tencent.com/dev?envId=${envId}#/{path}`.
+
+The CloudBase console changes frequently. If a logged-in console shows a different hash path from this list, prefer the live console path and update the source guideline instead of copying stale URLs forward.
+
+### Common entry points
+- **Overview (概览)**: `#/overview`
+- **Document Database (文档型数据库)**: `#/db/doc` - Collections: `#/db/doc/collection/${collectionName}`, Models: `#/db/doc/model/${modelName}`
+- **MySQL Database (MySQL 数据库)**: `#/db/mysql` - Tables: `#/db/mysql/table/default/`
+- **Cloud Functions (云函数)**: `#/scf` - Detail: `#/scf/detail?id=${functionName}&NameSpace=${envId}`
+- **CloudRun (云托管)**: `#/platform-run`
+- **Cloud Storage (云存储)**: `#/storage`
+- **Identity Authentication (身份认证)**: `#/identity` - Login: `#/identity/login-manage`, Tokens: `#/identity/token-management`
+
+### Other useful entry points
+- **Template Center**: `#/cloud-template/market`
+- **AI+**: `#/ai`
+- **Static Website Hosting**: `#/static-hosting`
+- **Weida Low-Code**: `#/lowcode/apps`
+- **Logs & Monitoring**: `#/devops/log`
+- **Extensions**: `#/apis`
+- **Environment Settings**: `#/env/http-access`
PATCH

echo "Gold patch applied."
