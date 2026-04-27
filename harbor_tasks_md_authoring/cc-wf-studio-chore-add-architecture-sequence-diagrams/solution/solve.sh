#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cc-wf-studio

# Idempotency guard
if grep -qF "\u3053\u306e\u30bb\u30af\u30b7\u30e7\u30f3\u3067\u306f\u3001cc-wf-studio\u306e\u4e3b\u8981\u306a\u30c7\u30fc\u30bf\u30d5\u30ed\u30fc\u3092Mermaid\u5f62\u5f0f\u306e\u30b7\u30fc\u30b1\u30f3\u30b9\u56f3\u3067\u8aac\u660e\u3057\u307e\u3059\u3002" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -203,6 +203,214 @@ TypeScript 5.x (VSCode Extension Host), React 18.x (Webview UI): Follow standard
 
 <!-- MANUAL ADDITIONS START -->
 
+## Architecture Sequence Diagrams
+
+このセクションでは、cc-wf-studioの主要なデータフローをMermaid形式のシーケンス図で説明します。
+
+### アーキテクチャ概要
+
+```mermaid
+flowchart TB
+    subgraph VSCode["VSCode Extension"]
+        subgraph ExtHost["Extension Host (Node.js)"]
+            Commands["Commands<br/>src/extension/commands/"]
+            Services["Services<br/>src/extension/services/"]
+            Utils["Utilities<br/>src/extension/utils/"]
+        end
+        subgraph Webview["Webview (React)"]
+            Components["Components<br/>src/webview/src/components/"]
+            Stores["Zustand Stores<br/>src/webview/src/stores/"]
+            WVServices["Services<br/>src/webview/src/services/"]
+        end
+    end
+    subgraph External["External Services"]
+        FS["File System<br/>.vscode/workflows/"]
+        CLI["Claude Code CLI"]
+        Slack["Slack API"]
+        MCP["MCP Servers"]
+    end
+
+    Webview <-->|postMessage| ExtHost
+    ExtHost --> FS
+    ExtHost --> CLI
+    ExtHost --> Slack
+    ExtHost --> MCP
+```
+
+### ワークフロー保存フロー
+
+```mermaid
+sequenceDiagram
+    actor User
+    participant Toolbar as Toolbar.tsx
+    participant Bridge as vscode-bridge.ts
+    participant Cmd as save-workflow.ts
+    participant FS as file-service.ts
+    participant Disk as .vscode/workflows/
+
+    User->>Toolbar: Click Save
+    Toolbar->>Bridge: saveWorkflow(workflow)
+    Bridge->>Cmd: postMessage(SAVE_WORKFLOW)
+    Cmd->>Cmd: validateWorkflow()
+    Cmd->>FS: ensureDirectory()
+    FS->>Disk: mkdir -p
+    Cmd->>FS: writeFile()
+    FS->>Disk: write JSON
+    Cmd->>Bridge: postMessage(SAVE_SUCCESS)
+    Bridge->>Toolbar: resolve Promise
+    Toolbar->>User: Show notification
+```
+
+### AI ワークフロー生成フロー
+
+```mermaid
+sequenceDiagram
+    actor User
+    participant Dialog as AiGenerationDialog.tsx
+    participant Svc as ai-generation-service.ts
+    participant Cmd as ai-generation.ts
+    participant Schema as schema-loader-service.ts
+    participant Skill as skill-service.ts
+    participant CLI as claude-code-service.ts
+    participant Store as workflow-store.ts
+
+    User->>Dialog: Enter description
+    User->>Dialog: Click Generate
+    Dialog->>Svc: generateWorkflow(description)
+    Svc->>Cmd: postMessage(GENERATE_WORKFLOW)
+
+    par Parallel Loading
+        Cmd->>Schema: loadWorkflowSchema()
+        Cmd->>Skill: scanAllSkills()
+    end
+
+    Cmd->>Cmd: filterSkillsByRelevance()
+    Cmd->>Cmd: constructPrompt()
+    Cmd->>CLI: executeClaudeCodeCLI()
+    CLI-->>Cmd: JSON response
+    Cmd->>Cmd: parseAndValidate()
+    Cmd->>Svc: postMessage(GENERATION_SUCCESS)
+    Svc->>Store: addGeneratedWorkflow()
+    Store->>Dialog: Update canvas
+    Dialog->>User: Show success
+```
+
+### AI ワークフロー改善フロー (Refinement)
+
+```mermaid
+sequenceDiagram
+    actor User
+    participant Panel as RefinementChatPanel.tsx
+    participant Store as refinement-store.ts
+    participant Cmd as workflow-refinement.ts
+    participant Svc as refinement-service.ts
+    participant CLI as claude-code-service.ts
+
+    User->>Panel: Enter refinement request
+    Panel->>Store: addMessage(userMessage)
+    Panel->>Cmd: postMessage(REFINE_WORKFLOW)
+    Cmd->>Svc: refineWorkflow(workflow, history)
+    Svc->>Svc: buildPromptWithHistory()
+    Svc->>CLI: executeClaudeCodeCLI()
+    CLI-->>Svc: Refined workflow JSON
+    Svc->>Svc: validateRefinedWorkflow()
+    Svc-->>Cmd: result
+    Cmd->>Store: postMessage(REFINEMENT_SUCCESS)
+    Store->>Store: updateConversationHistory()
+    Store->>Panel: Update canvas & chat
+    Panel->>User: Show refined workflow
+```
+
+### Slack ワークフロー共有フロー
+
+```mermaid
+sequenceDiagram
+    actor User
+    participant Dialog as SlackShareDialog.tsx
+    participant Cmd as slack-share-workflow.ts
+    participant Detector as sensitive-data-detector.ts
+    participant API as slack-api-service.ts
+    participant Slack as Slack API
+
+    User->>Dialog: Select channel
+    User->>Dialog: Click Share
+    Dialog->>Cmd: postMessage(SHARE_WORKFLOW_TO_SLACK)
+    Cmd->>Detector: detectSensitiveData(workflow)
+    alt Sensitive data found
+        Cmd->>Dialog: postMessage(SENSITIVE_DATA_WARNING)
+        Dialog->>User: Show warning dialog
+        User->>Dialog: Confirm override
+        Dialog->>Cmd: postMessage(SHARE with override flag)
+    end
+    Cmd->>API: uploadFile(workflow.json)
+    API->>Slack: files.upload
+    Slack-->>API: file_id
+    Cmd->>API: postMessage(channel, blocks)
+    API->>Slack: chat.postMessage
+    Slack-->>API: permalink
+    Cmd->>Dialog: postMessage(SHARE_SUCCESS)
+    Dialog->>User: Show permalink
+```
+
+### Slack ワークフローインポートフロー (Deep Link)
+
+```mermaid
+sequenceDiagram
+    actor User
+    participant SlackMsg as Slack Message
+    participant URI as VSCode URI Handler
+    participant Ext as extension.ts
+    participant Cmd as slack-import-workflow.ts
+    participant API as slack-api-service.ts
+    participant Store as workflow-store.ts
+
+    User->>SlackMsg: Click "Import to VS Code"
+    SlackMsg->>URI: vscode://cc-wf-studio/import?fileId=...
+    URI->>Ext: handleUri(uri)
+    Ext->>Cmd: postMessage(IMPORT_WORKFLOW_FROM_SLACK)
+    Cmd->>API: downloadFile(fileId)
+    API->>SlackMsg: files.info + download
+    SlackMsg-->>API: workflow JSON
+    Cmd->>Cmd: validateWorkflow()
+    Cmd->>Store: postMessage(IMPORT_SUCCESS)
+    Store->>Store: deserializeWorkflow()
+    Store->>User: Display on canvas
+```
+
+### MCP サーバー/ツール取得フロー
+
+```mermaid
+sequenceDiagram
+    actor User
+    participant Dialog as McpNodeDialog.tsx
+    participant Cmd as mcp-handlers.ts
+    participant Cache as mcp-cache-service.ts
+    participant SDK as mcp-sdk-client.ts
+    participant MCP as MCP Server
+
+    User->>Dialog: Open MCP Node config
+    Dialog->>Cmd: postMessage(LIST_MCP_SERVERS)
+    Cmd->>Cache: getCachedServers()
+    alt Cache miss
+        Cmd->>SDK: listServers()
+        SDK->>MCP: Initialize connection
+        MCP-->>SDK: Server list
+        SDK-->>Cmd: servers[]
+        Cmd->>Cache: cacheServers()
+    end
+    Cmd->>Dialog: postMessage(MCP_SERVERS_LIST)
+
+    User->>Dialog: Select server
+    Dialog->>Cmd: postMessage(GET_MCP_TOOLS)
+    Cmd->>SDK: getTools(serverId)
+    SDK->>MCP: tools/list
+    MCP-->>SDK: tools[]
+    Cmd->>Dialog: postMessage(MCP_TOOLS_LIST)
+    Dialog->>User: Show available tools
+```
+
+---
+
 ## AI-Assisted Skill Node Generation (Feature 001-ai-skill-generation)
 
 ### Key Files and Components
PATCH

echo "Gold patch applied."
