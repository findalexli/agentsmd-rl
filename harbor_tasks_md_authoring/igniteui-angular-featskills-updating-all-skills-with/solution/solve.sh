#!/usr/bin/env bash
set -euo pipefail

cd /workspace/igniteui-angular

# Idempotency guard
if grep -qF "> **Full setup instructions for VS Code, Cursor, Claude Desktop, and JetBrains I" "skills/igniteui-angular-components/SKILL.md" && grep -qF "This reference gives high-level guidance on when to use each chart type, their k" "skills/igniteui-angular-components/references/charts.md" && grep -qF "This reference gives high-level guidance on when to use each data display compon" "skills/igniteui-angular-components/references/data-display.md" && grep -qF "This reference gives high-level guidance on when to use each directive, their ke" "skills/igniteui-angular-components/references/directives.md" && grep -qF "This reference gives high-level guidance on when to use each feedback and overla" "skills/igniteui-angular-components/references/feedback.md" && grep -qF "This reference gives high-level guidance on when to use each form control compon" "skills/igniteui-angular-components/references/form-controls.md" && grep -qF "This reference gives high-level guidance on when to use each layout manager comp" "skills/igniteui-angular-components/references/layout-manager.md" && grep -qF "This reference gives high-level guidance on when to use each layout component, t" "skills/igniteui-angular-components/references/layout.md" && grep -qF "The Ignite UI CLI MCP server enables AI assistants to discover Ignite UI compone" "skills/igniteui-angular-components/references/mcp-setup.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/igniteui-angular-components/SKILL.md b/skills/igniteui-angular-components/SKILL.md
@@ -6,6 +6,29 @@ user-invocable: true
 
 # Ignite UI for Angular — UI Components
 
+## Prerequisites
+- Angular 20+ project
+- `@angular/cli` installed
+- `igniteui-angular` or `@infragistics/igniteui-angular` added to the project via `ng add igniteui-angular` (or the `@infragistics` variant) or `npm install` — see [Package Variants](#package-variants) below.
+- A theme applied to the application (see [`igniteui-angular-theming`](../igniteui-angular-theming/SKILL.md)).
+- `provideAnimations()` in `app.config.ts` — **required before using any overlay or animated component**
+- The **Ignite UI CLI MCP server** (`igniteui-cli`) is available as a tool provider
+
+> **AGENT INSTRUCTION — MCP Server Setup (REQUIRED)**
+>
+> Before using any Ignite UI CLI MCP tools, you MUST verify the MCP server is available
+> by calling `list_components`. If the tool is not available or the call fails,
+> you MUST automatically configure it by following the setup process steps described below.
+>
+> After writing the file, inform the user that the MCP server has been
+> configured and they may need to reload the editor for the tools to activate.
+> Start the MCP server and wait for that MCP server to start before continuing the component-related work.
+> Do NOT skip this step or ask the user to do it manually.
+
+## Setting Up the Ignite UI CLI MCP Server
+
+> **Full setup instructions for VS Code, Cursor, Claude Desktop, and JetBrains IDEs are in [`references/mcp-setup.md`](./references/mcp-setup.md).** Read that file for editor-specific configuration steps and verification.
+
 ## MANDATORY AGENT PROTOCOL — YOU MUST FOLLOW THIS BEFORE PRODUCING ANY OUTPUT
 
 **This file is a routing hub only. It contains NO code examples and NO API details.**
@@ -41,15 +64,6 @@ Base your code and explanation exclusively on what you read. If the reference fi
 
 ---
 
-## Prerequisites
-
-- Angular 20+ project
-- `@angular/cli` installed
-- `igniteui-angular` or `@infragistics/igniteui-angular` added to the project via `ng add igniteui-angular` (or the `@infragistics` variant) or `npm install` — see [Package Variants](#package-variants) below.
-- A theme applied to the application (see [`igniteui-angular-theming`](../igniteui-angular-theming/SKILL.md)).
-- `provideAnimations()` in `app.config.ts` — **required before using any overlay or animated component**
-
-
 ## Package Variants
 
 | Package | Install | Who uses it |
diff --git a/skills/igniteui-angular-components/references/charts.md b/skills/igniteui-angular-components/references/charts.md
@@ -15,6 +15,7 @@
 ## Overview
 
 Ignite UI for Angular Charts provides 65+ chart types for data visualization. Charts are packaged separately in `igniteui-angular-charts` (or `@infragistics/igniteui-angular-charts` for licensed users).
+This reference gives high-level guidance on when to use each chart type, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cli` with the specific chart component or feature you're interested in.
 
 ### Chart Component packages
 - `igniteui-angular-charts` — Category Chart, Financial Chart, Data Chart, and Pie Chart components (NPM)
diff --git a/skills/igniteui-angular-components/references/data-display.md b/skills/igniteui-angular-components/references/data-display.md
@@ -16,6 +16,9 @@
 - [Progress Indicators](#progress-indicators)
 - [Chat (AI Chat Component)](#chat-ai-chat-component)
 
+## Overview
+This reference gives high-level guidance on when to use each data display component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cli` with the specific component or feature you're interested in.
+
 ## List
 
 > **Docs:** [List Component](https://www.infragistics.com/products/ignite-ui-angular/angular/components/list)
diff --git a/skills/igniteui-angular-components/references/directives.md b/skills/igniteui-angular-components/references/directives.md
@@ -11,6 +11,9 @@
 - [Tooltip](#tooltip)
 - [Drag and Drop](#drag-and-drop)
 
+## Overview
+This reference gives high-level guidance on when to use each directive, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cli` with the specific directive or feature you're interested in.
+
 ## Button & Icon Button
 
 > **Docs:** [Button Component](https://www.infragistics.com/products/ignite-ui-angular/angular/components/button)
diff --git a/skills/igniteui-angular-components/references/feedback.md b/skills/igniteui-angular-components/references/feedback.md
@@ -13,6 +13,9 @@
 - [Banner](#banner)
 - [Key Rules](#key-rules)
 
+## Overview
+This reference gives high-level guidance on when to use each feedback and overlay component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cli` with the specific component or feature you're interested in.
+
 ## Dialog
 
 > **Docs:** [Dialog Component](https://www.infragistics.com/products/ignite-ui-angular/angular/components/dialog)
diff --git a/skills/igniteui-angular-components/references/form-controls.md b/skills/igniteui-angular-components/references/form-controls.md
@@ -18,6 +18,9 @@
 - [Reactive Forms Integration](#reactive-forms-integration)
 - [Key Rules](#key-rules)
 
+## Overview
+This reference gives high-level guidance on when to use each form control component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cli` with the specific component or feature you're interested in.
+
 ## Input Group
 
 > **Docs:** [Input Group](https://www.infragistics.com/products/ignite-ui-angular/angular/components/input-group)
diff --git a/skills/igniteui-angular-components/references/layout-manager.md b/skills/igniteui-angular-components/references/layout-manager.md
@@ -9,6 +9,9 @@
 - [Dock Manager](#dock-manager)
 - [Tile Manager](#tile-manager)
 
+## Overview
+This reference gives high-level guidance on when to use each layout manager component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cli` with the specific component or feature you're interested in.
+
 ---
 
 ## Layout Manager Directives
diff --git a/skills/igniteui-angular-components/references/layout.md b/skills/igniteui-angular-components/references/layout.md
@@ -12,6 +12,9 @@
 - [Splitter](#splitter)
 - [Navigation Drawer](#navigation-drawer)
 
+## Overview
+This reference gives high-level guidance on when to use each layout component, their key features, and common API members. For detailed documentation, call `get_doc` and `get_api_reference` from `igniteui-cli` with the specific component or feature you're interested in.
+
 ## Tabs
 
 > **Docs:** [Tabs Component](https://www.infragistics.com/products/ignite-ui-angular/angular/components/tabs)
diff --git a/skills/igniteui-angular-components/references/mcp-setup.md b/skills/igniteui-angular-components/references/mcp-setup.md
@@ -0,0 +1,77 @@
+# Setting Up the Ignite UI CLI MCP Server
+
+> **Part of the [`igniteui-angular-components`](../SKILL.md) skill hub.**
+
+## Contents
+
+- [VS Code](#vs-code)
+- [Cursor](#cursor)
+- [Claude Desktop](#claude-desktop)
+- [WebStorm / JetBrains IDEs](#webstorm--jetbrains-ides)
+- [Verifying the Setup](#verifying-the-setup)
+
+The Ignite UI CLI MCP server enables AI assistants to discover Ignite UI components, access component documentation, and support related Ignite UI workflows. It must be configured in your editor before these tools become available.
+
+## VS Code
+
+Create or edit `.vscode/mcp.json` in your project:
+
+```json
+{
+  "servers": {
+    "igniteui-cli": {
+      "command": "npx",
+      "args": ["-y", "igniteui-cli@next", "mcp"]
+    }
+  }
+}
+```
+
+This works whether `igniteui-cli` is installed locally in `node_modules` or needs to be pulled from the npm registry — `npx -y` handles both cases.
+
+## Cursor
+
+Create or edit `.cursor/mcp.json`:
+
+```json
+{
+  "mcpServers": {
+    "igniteui-cli": {
+      "command": "npx",
+      "args": ["-y", "igniteui-cli@next", "mcp"]
+    }
+  }
+}
+```
+
+## Claude Desktop
+
+Edit the Claude Desktop config file:
+- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
+- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
+
+```json
+{
+  "mcpServers": {
+    "igniteui-cli": {
+      "command": "npx",
+      "args": ["-y", "igniteui-cli@next", "mcp"]
+    }
+  }
+}
+```
+
+## WebStorm / JetBrains IDEs
+
+1. Go to **Settings → Tools → AI Assistant → MCP Servers**
+2. Click **+ Add MCP Server**
+3. Set Command to `npx` and Arguments to `igniteui-cli@next mcp`
+4. Click OK and restart the AI Assistant
+
+## Verifying the Setup
+
+After configuring the MCP server, ask your AI assistant:
+
+> "List all available Ignite UI components"
+
+If the MCP server is running, the `list_components` tool will return all available components for the detected framework.
PATCH

echo "Gold patch applied."
