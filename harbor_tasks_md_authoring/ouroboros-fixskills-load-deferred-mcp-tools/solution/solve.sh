#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ouroboros

# Idempotency guard
if grep -qF "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable ju" "skills/evaluate/SKILL.md" && grep -qF "2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboro" "skills/evolve/SKILL.md" && grep -qF "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable ju" "skills/interview/SKILL.md" && grep -qF "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable ju" "skills/run/SKILL.md" && grep -qF "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable ju" "skills/seed/SKILL.md" && grep -qF "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable ju" "skills/status/SKILL.md" && grep -qF "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable ju" "skills/unstuck/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/evaluate/SKILL.md b/skills/evaluate/SKILL.md
@@ -39,6 +39,21 @@ The evaluation pipeline runs three progressive stages:
 
 When the user invokes this skill:
 
+### Load MCP Tools (Required first)
+
+The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**
+
+1. Use the `ToolSearch` tool to find and load the evaluate MCP tool:
+   ```
+   ToolSearch query: "+ouroboros evaluate"
+   ```
+2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_evaluate` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.
+3. If ToolSearch finds the tool → proceed with the MCP-based evaluation below. If not → skip to **Fallback** section.
+
+**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.
+
+### Evaluation Steps
+
 1. Determine what to evaluate:
    - If `session_id` provided: Use it directly
    - If no session_id: Check conversation for recent execution session IDs
diff --git a/skills/evolve/SKILL.md b/skills/evolve/SKILL.md
@@ -41,7 +41,20 @@ ooo evolve --rewind <lineage_id> <generation_number>
 
 ## Instructions
 
-### Path A: MCP Available (check for `ouroboros_evolve_step` tool)
+### Load MCP Tools (Required before Path A/B decision)
+
+The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**
+
+1. Use the `ToolSearch` tool to find and load the evolve MCP tools:
+   ```
+   ToolSearch query: "+ouroboros evolve"
+   ```
+2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_evolve_step`, `ouroboros_interview`, `ouroboros_generate_seed`). After ToolSearch returns, the tools become callable.
+3. If ToolSearch finds the tools → proceed to **Path A**. If not → proceed to **Path B**.
+
+**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.
+
+### Path A: MCP Available (loaded via ToolSearch above)
 
 **Starting a new evolutionary loop:**
 1. Parse the user's input as `initial_context`
diff --git a/skills/interview/SKILL.md b/skills/interview/SKILL.md
@@ -57,9 +57,26 @@ Compare the result with the current version in `.claude-plugin/plugin.json`.
 
 Then choose the execution path:
 
+### Step 0.5: Load MCP Tools (Required before Path A/B decision)
+
+The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**
+
+1. Use the `ToolSearch` tool to find and load the interview MCP tool:
+   ```
+   ToolSearch query: "+ouroboros interview"
+   ```
+   This searches for tools with "ouroboros" in the name related to "interview".
+
+2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_interview` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.
+
+3. If ToolSearch finds the tool → proceed to **Path A**.
+   If ToolSearch returns no matching tools → proceed to **Path B**.
+
+**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.
+
 ### Path A: MCP Mode (Preferred)
 
-If the `ouroboros_interview` MCP tool is available, use it for persistent, structured interviews:
+If the `ouroboros_interview` MCP tool is available (loaded via ToolSearch above), use it for persistent, structured interviews:
 
 1. **Start a new interview**:
    ```
diff --git a/skills/run/SKILL.md b/skills/run/SKILL.md
@@ -27,6 +27,21 @@ Execute a Seed specification through the Ouroboros workflow engine.
 
 When the user invokes this skill:
 
+### Load MCP Tools (Required first)
+
+The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**
+
+1. Use the `ToolSearch` tool to find and load the execution MCP tools:
+   ```
+   ToolSearch query: "+ouroboros execute"
+   ```
+2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_execute_seed`, `ouroboros_session_status`). After ToolSearch returns, the tools become callable.
+3. If ToolSearch finds the tools → proceed with the steps below. If not → skip to **Fallback** section.
+
+**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.
+
+### Execution Steps
+
 1. **Detect git workflow** (before any code changes):
    - Read the project's `CLAUDE.md` for git workflow preferences
    - If PR-based workflow detected and currently on `main`/`master`:
diff --git a/skills/seed/SKILL.md b/skills/seed/SKILL.md
@@ -18,11 +18,24 @@ ooo seed [session_id]
 
 ## Instructions
 
-When the user invokes this skill, choose the execution path:
+When the user invokes this skill:
+
+### Load MCP Tools (Required before Path A/B decision)
+
+The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**
+
+1. Use the `ToolSearch` tool to find and load the seed generation MCP tool:
+   ```
+   ToolSearch query: "+ouroboros seed"
+   ```
+2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_generate_seed` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.
+3. If ToolSearch finds the tool → proceed to **Path A**. If not → proceed to **Path B**.
+
+**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.
 
 ### Path A: MCP Mode (Preferred)
 
-If the `ouroboros_generate_seed` MCP tool is available:
+If the `ouroboros_generate_seed` MCP tool is available (loaded via ToolSearch above):
 
 1. Determine the interview session:
    - If `session_id` provided: Use it directly
diff --git a/skills/status/SKILL.md b/skills/status/SKILL.md
@@ -24,6 +24,21 @@ Check session status and measure goal drift.
 
 When the user invokes this skill:
 
+### Load MCP Tools (Required first)
+
+The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**
+
+1. Use the `ToolSearch` tool to find and load the status MCP tools:
+   ```
+   ToolSearch query: "+ouroboros session status"
+   ```
+2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_session_status`, `ouroboros_measure_drift`). After ToolSearch returns, the tools become callable.
+3. If ToolSearch finds the tools → proceed with the steps below. If not → skip to **Fallback** section.
+
+**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.
+
+### Status Steps
+
 1. Determine the session to check:
    - If `session_id` provided: Use it directly
    - If no session_id: Check conversation for recent session IDs
diff --git a/skills/unstuck/SKILL.md b/skills/unstuck/SKILL.md
@@ -29,6 +29,21 @@ Break through stagnation with lateral thinking personas.
 
 When the user invokes this skill:
 
+### Load MCP Tools (Required first)
+
+The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**
+
+1. Use the `ToolSearch` tool to find and load the lateral thinking MCP tool:
+   ```
+   ToolSearch query: "+ouroboros lateral"
+   ```
+2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_lateral_think` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.
+3. If ToolSearch finds the tool → use MCP mode below. If not → skip to **Fallback** section.
+
+**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need to be loaded first.
+
+### Unstuck Steps
+
 1. Determine the context:
    - What is the user stuck on? (Check recent conversation)
    - What approaches have been tried?
PATCH

echo "Gold patch applied."
