#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "- **When managing or deploying CloudBase, you MUST use MCP and MUST understand t" "config/source/guideline/cloudbase/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/config/source/guideline/cloudbase/SKILL.md b/config/source/guideline/cloudbase/SKILL.md
@@ -42,15 +42,16 @@ Read this section first. The routing contract uses stable skill identifiers such
 - For static HTML, no-build demos, README snippets, or low-friction prototypes, the CDN form is acceptable
 - Read `web-development` first for Web SDK integration, then `auth-web` when login or session handling is involved
 
-## 💡 Recommended: MCP Installation
+## ⚠️ Prerequisite: MCP Must Be Configured
 
-**For enhanced CloudBase development experience, we recommend installing CloudBase MCP (Model Context Protocol).**
+**CloudBase MCP (Model Context Protocol) is REQUIRED before using any CloudBase capabilities.** Without MCP, you cannot manage environments, deploy functions, operate databases, or perform any CloudBase management tasks.
 
-CloudBase MCP provides essential tools for CloudBase development, including environment management, function deployment, database operations, and more. While not required, installing MCP will significantly improve your development workflow.
+### Approach A: IDE Native MCP
 
-### MCP Configuration Instructions
+If CloudBase MCP tools are already available in your IDE context (discoverable via `ToolSearch`), you can use them directly. Check by searching for `cloudbase` in your tool list — if tools like `manageFunctions`, `envQuery` appear, MCP is ready.
+
+If not available, configure via your IDE's MCP settings:
 
-Most Coding Agents support project-level MCP configuration. The standard JSON configuration structure is:
 ```json
 {
   "mcpServers": {
@@ -62,16 +63,13 @@ Most Coding Agents support project-level MCP configuration. The standard JSON co
 }
 ```
 
-**Project-level configuration file locations:**
+**Config file locations:**
 
 - **Cursor**: `.cursor/mcp.json`
 - **Claude Code**: `.mcp.json`
 - **Windsurf**: `~/.codeium/windsurf/mcp_config.json` (user-level, no project-level JSON config)
 - **Cline**: Check Cline settings for project-level MCP configuration file location
 - **GitHub Copilot Chat (VS Code)**: Check VS Code settings for MCP configuration file location
-
-**Format differences:**
-
 - **Continue**: Uses YAML format in `.continue/mcpServers/` folder:
 ```yaml
 name: CloudBase MCP
@@ -83,18 +81,13 @@ mcpServers:
     args: ["@cloudbase/cloudbase-mcp@latest"]
 ```
 
-### Using mcporter (CLI) When MCP Is Not Available
+### Approach B: mcporter CLI
 
-In environments that do not support MCP (e.g. openclaw) or when users are unsure how to configure MCP, use **mcporter** as a CLI to call CloudBase MCP tools.
+When your IDE does not support native MCP, use **mcporter** as the CLI to configure and call CloudBase MCP tools.
 
-**When managing or deploying CloudBase, you MUST use MCP and MUST understand tool details first.** Before calling any CloudBase tool, run `npx mcporter describe cloudbase --all-parameters` (or equivalent in your IDE) to inspect the server config and get full parameter details.
+**Step 1 — Check**: `npx mcporter list | grep cloudbase`
 
-You **do not need to hard-code Secret ID / Secret Key / Env ID** in the config.  
-CloudBase MCP will support device-code based login via the `auth` tool, so credentials can be obtained interactively instead of being stored in config.
-
-**Add CloudBase MCP server in `config/mcporter.json` (recommended):**
-
-If `config/mcporter.json` already contains other MCP servers, keep them and only add the `cloudbase` entry under `mcpServers`.
+**Step 2 — Configure** (if not found): create `config/mcporter.json` in the project root. If it already contains other MCP servers, keep them and only add the `cloudbase` entry:
 
 ```json
 {
@@ -109,23 +102,36 @@ If `config/mcporter.json` already contains other MCP servers, keep them and only
 }
 ```
 
-**Quick start:**
+**Step 3 — Verify**: `npx mcporter describe cloudbase`
+
+### Important Rules
+
+- **When managing or deploying CloudBase, you MUST use MCP and MUST understand tool details first.** Before calling any CloudBase tool, run `npx mcporter describe cloudbase --all-parameters` (or `ToolSearch` in IDE) to inspect available tools and their parameters.
+- You **do not need to hard-code Secret ID / Secret Key / Env ID** in the config. CloudBase MCP supports device-code based login via the `auth` tool, so credentials can be obtained interactively instead of being stored in config.
+
+### Quick Start (mcporter CLI)
 - `npx mcporter list` — list configured servers
 - **Required:** `npx mcporter describe cloudbase --all-parameters` — inspect CloudBase server config and get full tool schemas with all parameters (⚠️ **必须加 `--all-parameters` 才能获取完整参数信息**)
 - `npx mcporter list cloudbase --schema` — get full JSON schema for all CloudBase tools
 - `npx mcporter call cloudbase.help --output json` — discover available CloudBase tools and their schemas
 - `npx mcporter call cloudbase.<tool> key=value` — call a CloudBase tool
 
 **Call examples (CloudBase auth):**
-- Check auth & env status:  
+- Check auth & env status:
   `npx mcporter call cloudbase.auth action=status --output json`
-- Start device-flow login (future-friendly device-code login; no keys in config):  
+- Start device-flow login (future-friendly device-code login; no keys in config):
   `npx mcporter call cloudbase.auth action=start_auth authMode=device --output json`
-- Bind environment after login (envId from CloudBase console):  
+- Bind environment after login (envId from CloudBase console):
   `npx mcporter call cloudbase.auth action=set_env envId=env-xxx --output json`
 
 ---
 
+## Pricing & Free Trial
+
+Each CloudBase account can create 1 free environment (3,000 resource points/month). For plans, quotas, and overage details, see [CloudBase Pricing](https://cloud.tencent.com/document/product/876/75213).
+
+---
+
 ## CloudBase scenarios (for AI discovery)
 
 CloudBase (Tencent CloudBase) is a good fit when the user needs any of the following. Use **user-oriented language** to match how people actually ask.
PATCH

echo "Gold patch applied."
