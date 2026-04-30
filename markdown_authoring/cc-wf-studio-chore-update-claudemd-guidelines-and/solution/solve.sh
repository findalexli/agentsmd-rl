#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cc-wf-studio

# Idempotency guard
if grep -qF "- The chat UI-based AI editing features (Refinement Chat Panel, AI Workflow Gene" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -6,13 +6,8 @@ Auto-generated from all feature plans. Last updated: 2025-11-01
 - ローカルファイルシステム (`.vscode/workflows/*.json`, `.claude/skills/*.md`, `.claude/commands/*.md`) (001-cc-wf-studio)
 - TypeScript 5.3 (VSCode Extension Host), React 18.2 (Webview UI) (001-node-types-extension)
 - ローカルファイルシステム (`.vscode/workflows/*.json`) (001-node-types-extension)
-- TypeScript 5.3 (Extension Host & Webview shared types), React 18.2 (Webview UI) (001-ai-workflow-generation)
-- File system (workflow schema JSON in resources/, generated workflows in canvas state) (001-ai-workflow-generation)
 - TypeScript 5.3.0 (001-skill-node)
 - File system (SKILL.md files in `~/.claude/skills/` and `.claude/skills/`), workflow JSON files in `.vscode/workflows/` (001-skill-node)
-- TypeScript 5.3 (Extension Host), React 18.2 (Webview UI) (001-ai-skill-generation)
-- File system (existing SKILL.md files in `~/.claude/skills/` and `.claude/skills/`, workflow-schema.json in resources/) (001-ai-skill-generation)
-- Workflow JSON files in `.vscode/workflows/` directory (conversation history embedded in workflow metadata) (001-ai-workflow-refinement)
 - TypeScript 5.3.0 (VSCode Extension Host), TypeScript/React 18.2 (Webview UI) + VSCode Extension API 1.80.0+, React 18.2, React Flow (visual canvas), Zustand (state management), child_process (Claude Code CLI execution) (001-mcp-node)
 - Workflow JSON files in `.vscode/workflows/` directory, Claude Code MCP configuration (user/project/enterprise scopes) (001-mcp-node)
 - TypeScript 5.3.0 (VSCode Extension Host), TypeScript/React 18.2 (Webview UI) + VSCode Extension API 1.80.0+, React 18.2, React Flow (visual canvas), Zustand (state management), existing MCP SDK client services (001-mcp-natural-language-mode)
@@ -205,6 +200,57 @@ TypeScript 5.x (VSCode Extension Host), React 18.x (Webview UI): Follow standard
 
 <!-- MANUAL ADDITIONS START -->
 
+## Planning Guidelines
+
+### Gather Context from github-knowledge MCP (Required for Plan Mode)
+
+**When entering Plan Mode to design or plan implementation, always gather related knowledge from the github-knowledge MCP first.**
+
+#### Steps
+1. Use `search_decisions` to find past technical decisions by relevant modules, tags, or keywords
+2. Use `search_domain_knowledge` to find related business rules, domain terms, and constraints
+3. Use `get_decision_detail` as needed for full context on specific decisions
+4. Use `get_module_history` as needed to understand how a module has evolved
+
+#### Purpose
+- Maintain consistency with past technical decisions
+- Avoid re-proposing previously rejected alternatives
+- Incorporate domain knowledge (business rules, constraints) into design
+- Align implementation with established architectural patterns
+
+## AI Editing Features
+
+### MCP Server-based AI Editing (Active)
+- The built-in MCP server (`cc-workflow-ai-editor` skill) is the primary interface for external AI agents to create and edit workflows.
+- All new AI editing development should go through the MCP server approach.
+
+```mermaid
+sequenceDiagram
+    actor User
+    participant VSCode as CC Workflow Studio
+    participant MCP as MCP Server
+    participant Agent as AI Agent
+
+    User->>VSCode: Click agent button
+    VSCode->>MCP: Auto start server
+    VSCode->>Agent: Launch with editing skill
+
+    loop AI edits workflow
+        Agent->>MCP: get_workflow
+        MCP-->>Agent: workflow JSON
+        Agent->>MCP: apply_workflow
+        MCP->>VSCode: Update canvas
+    end
+```
+
+### Chat UI-based AI Editing (Discontinued)
+- The chat UI-based AI editing features (Refinement Chat Panel, AI Workflow Generation Dialog) are **no longer under active development**.
+- Existing functionality will be maintained but no new features or enhancements will be added.
+- Affected features:
+  - `001-ai-workflow-generation`: AI Workflow Generation via AiGenerationDialog
+  - `001-ai-workflow-refinement`: AI Workflow Refinement via RefinementChatPanel
+  - `001-ai-skill-generation`: AI Skill Node Generation via AiGenerationDialog
+
 ## Architecture Sequence Diagrams
 
 このセクションでは、cc-wf-studioの主要なデータフローをMermaid形式のシーケンス図で説明します。
@@ -263,45 +309,6 @@ sequenceDiagram
     Toolbar->>User: Show notification
 ```
 
-### AI ワークフロー改善フロー (Refinement)
-
-```mermaid
-sequenceDiagram
-    actor User
-    participant Panel as RefinementChatPanel.tsx
-    participant Store as refinement-store.ts
-    participant Cmd as workflow-refinement.ts
-    participant Svc as refinement-service.ts
-    participant CLI as claude-code-service.ts
-
-    User->>Panel: Enter refinement request
-    Panel->>Store: addMessage(userMessage)
-    Panel->>Store: addLoadingAiMessage()
-    Panel->>Cmd: postMessage(REFINE_WORKFLOW)
-    Cmd->>Svc: refineWorkflow(workflow, history, onProgress)
-    Svc->>Svc: buildPromptWithHistory()
-    Svc->>CLI: executeClaudeCodeCLIStreaming()
-
-    Note over CLI,Panel: Streaming Phase
-    loop For each chunk
-        CLI->>Svc: onProgress(chunk)
-        Svc->>Cmd: Parse chunk & extract text
-        Cmd->>Panel: postMessage(REFINEMENT_PROGRESS)
-        Panel->>Store: updateMessageContent()
-        Store->>Panel: Update UI in real-time
-        Panel->>User: Display AI response progressively
-    end
-
-    CLI-->>Svc: Refined workflow JSON
-    Svc->>Svc: validateRefinedWorkflow()
-    Svc-->>Cmd: result
-    Cmd->>Panel: postMessage(REFINEMENT_SUCCESS)
-    Panel->>Store: updateWorkflow() & updateMessageContent()
-    Store->>Store: updateConversationHistory()
-    Store->>Panel: Update canvas & chat
-    Panel->>User: Show refined workflow
-```
-
 ### Slack ワークフロー共有フロー
 
 ```mermaid
@@ -392,161 +399,6 @@ sequenceDiagram
 
 ---
 
-## AI-Assisted Skill Node Generation (Feature 001-ai-skill-generation)
-
-### Key Files and Components
-
-#### Extension Host Services
-- **src/extension/services/skill-relevance-matcher.ts**
-  - Calculates relevance scores between user descriptions and Skills using keyword matching
-  - `tokenize()`: Removes stopwords, filters by min length (3 chars)
-  - `calculateSkillRelevance()`: Formula: `score = |intersection| / sqrt(|userTokens| * |skillTokens|)`
-  - `filterSkillsByRelevance()`: Filters by threshold (0.6), limits to 20, prefers project scope
-  - No new library dependencies (per user constraint)
-
-- **src/extension/commands/ai-generation.ts** (Enhanced)
-  - Scans personal + project Skills in parallel (`Promise.all`)
-  - Filters Skills by relevance to user description
-  - Constructs AI prompt with "Available Skills" section (JSON format)
-  - Resolves `skillPath` post-generation for AI-generated Skill nodes
-  - Marks missing Skills as `validationStatus: 'missing'`
-
-- **src/extension/utils/validate-workflow.ts** (Extended)
-  - `validateSkillNode()`: Validates required fields, name format, length constraints
-  - Error codes: SKILL_MISSING_FIELD, SKILL_INVALID_NAME, SKILL_NAME_TOO_LONG, etc.
-  - Integrated into `validateAIGeneratedWorkflow()` flow
-
-#### Resources
-- **resources/workflow-schema.json** (Updated)
-  - Added Skill node type documentation (~1.5KB addition)
-  - Instructions for AI: "Use when user description matches Skill's purpose"
-  - Field descriptions: name, description, scope, skillPath (auto-resolved), validationStatus
-  - File size: 16.5KB (within tolerance)
-
-### Message Flow
-```
-Webview (AiGenerationDialog)
-  → postMessage(GENERATE_WORKFLOW)
-  → Extension (ai-generation.ts)
-  → scanAllSkills() + loadWorkflowSchema() (parallel)
-  → filterSkillsByRelevance(userDescription, availableSkills)
-  → constructPrompt(description, schema, filteredSkills)
-  → ClaudeCodeService.executeClaudeCodeCLI()
-  → Parse & resolveSkillPaths(workflow, availableSkills)
-  → Validate (including Skill nodes)
-  → postMessage(GENERATION_SUCCESS | GENERATION_FAILED)
-  → Webview (workflow-store.addGeneratedWorkflow())
-```
-
-### Key Constraints
-- Max 20 Skills in AI prompt (prevent timeout)
-- Relevance threshold: 0.3 (30%) - tested 0.5 but 0.3 provides better recall without sacrificing quality
-- Keyword matching: O(n+m) complexity
-- Duplicate handling: Project scope preferred over personal
-- Generation timeout: 90 seconds
-
-### Error Handling
-- Skill not found → `validationStatus: 'missing'`
-- Skill file malformed → `validationStatus: 'invalid'`
-- All errors logged to "CC Workflow Studio" Output Channel
-
-### Design Decisions & Lessons Learned
-
-**Phase 5 (User Skill Selection) - Rejected**
-
-During development, we attempted to implement a UI feature allowing users to manually select which Skills to include/exclude in AI generation. This was intended to prevent timeouts when users have many Skills installed.
-
-**Why it was rejected:**
-- **AI generation control has inherent limitations**: The AI prompt is a "suggestion" not a "command"
-- **Unpredictable behavior**: Even when Skills are excluded from the prompt, the AI may still generate Skill nodes based on its own interpretation of the user's description
-- **Poor UX**: Users selecting "don't use this Skill" would experience confusion when the AI uses it anyway
-- **Uncontrollable AI behavior**: The final decision of which nodes to generate belongs to the AI, not the prompt engineering
-
-**Key lesson:**
-> Do not implement user-facing features that promise control over AI behavior that cannot be guaranteed. AI generation is inherently probabilistic, and features requiring deterministic outcomes should be avoided.
-
-**Alternative approaches for timeout prevention:**
-- Dynamic timeout adjustment based on Skill count
-- Adaptive relevance threshold tuning (e.g., 0.3 → 0.5 for high Skill counts)
-- Maintain strict MAX_SKILLS_IN_PROMPT limit (currently 20)
-
----
-
-## AI-Assisted Workflow Generation (Feature 001-ai-workflow-generation)
-
-### Key Files and Components
-
-#### Extension Host Services
-- **src/extension/services/claude-code-service.ts**
-  - Executes Claude Code CLI via child_process.spawn()
-  - Handles timeout (30s default), error mapping (COMMAND_NOT_FOUND, TIMEOUT, etc.)
-  - Includes comprehensive logging to VSCode Output Channel
-
-- **src/extension/services/schema-loader-service.ts**
-  - Loads workflow-schema.json from resources/ directory
-  - Implements in-memory caching for performance
-  - Provides schema to AI for context during generation
-
-- **src/extension/commands/ai-generation.ts**
-  - Main command handler for GENERATE_WORKFLOW messages from Webview
-  - Orchestrates: schema loading → CLI execution → parsing → validation
-  - Sends success/failure messages back to Webview with execution metrics
-
-- **src/extension/utils/validate-workflow.ts**
-  - Validates AI-generated workflows against VALIDATION_RULES
-  - Checks node count (<50), connection validity, required fields
-  - Returns structured validation errors for user feedback
-
-#### Webview Components
-- **src/webview/src/services/ai-generation-service.ts**
-  - Bridge between Webview UI and Extension Host
-  - Sends GENERATE_WORKFLOW messages via postMessage
-  - Returns Promise that resolves to workflow or AIGenerationError
-
-- **src/webview/src/components/dialogs/AiGenerationDialog.tsx**
-  - Modal dialog for user description input (max 2000 chars)
-  - Handles loading states, error display, success notifications
-  - Fully internationalized (5 languages: en, ja, ko, zh-CN, zh-TW)
-  - Keyboard shortcuts: Ctrl/Cmd+Enter (generate), Esc (cancel)
-
-#### Resources
-- **resources/workflow-schema.json**
-  - Comprehensive schema documentation for AI context
-  - Documents all 7 node types (Start, End, Prompt, SubAgent, AskUserQuestion, IfElse, Switch)
-  - Includes validation rules and 3 example workflows
-  - Size: <10KB (optimized for token efficiency)
-  - **IMPORTANT**: Included in VSIX package (not excluded by .vscodeignore)
-
-#### Documentation
-- **docs/schema-maintenance.md**
-  - Maintenance guide for workflow-schema.json
-  - Synchronization procedures between TypeScript types and JSON schema
-  - Update workflows, validation rules mapping, common tasks
-  - File size optimization guidelines (target <10KB, max 15KB)
-
-### Message Flow
-```
-Webview (AiGenerationDialog)
-  → postMessage(GENERATE_WORKFLOW)
-  → Extension (ai-generation.ts)
-  → ClaudeCodeService.executeClaudeCodeCLI()
-  → Parse & Validate
-  → postMessage(GENERATION_SUCCESS | GENERATION_FAILED)
-  → Webview (workflow-store.addGeneratedWorkflow())
-```
-
-### Error Handling
-- All errors mapped to specific error codes for i18n
-- Comprehensive logging to "CC Workflow Studio" Output Channel
-- Execution time tracking for all operations (success and failure)
-
-### Testing Notes
-- T052-T054: Manual testing scenarios (simple/medium/complex workflows, error scenarios)
-- T055: VSCode Output Channel logging implemented ✓
-- Unit/integration tests deferred (T011-T015, T019, T023, T028, T032, T035, T040)
-
----
-
 ## Dialog Component Design Guidelines
 
 ### ライブラリ選択
PATCH

echo "Gold patch applied."
