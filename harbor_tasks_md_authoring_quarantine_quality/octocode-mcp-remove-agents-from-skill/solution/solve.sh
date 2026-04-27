#!/usr/bin/env bash
set -euo pipefail

cd /workspace/octocode-mcp

# Idempotency guard
if grep -qF "skills/octocode-research/SKILL.md" "skills/octocode-research/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/octocode-research/SKILL.md b/skills/octocode-research/SKILL.md
@@ -299,41 +299,6 @@ Response format Example (bulk):
 - use tools composition wisely to get the best results and coherent data
 </mission>
 
-<agents_spawn>
-**Triggers:** Parallelizing research, isolating context, specialized tasks (Explore/Plan), noise reduction, or "Ultrathink" analysis of large text/logs.
-
-**Strategy:** Subagents do not fetch data; they process provided text to return structured insights.
-
-| Role | Scenario / Use Case |
-| :--- | :--- |
-| **Explorer** | Multi-repo research, comparing implementations, or external GitHub discovery. |
-| **Summarizer** | Reducing noise from large logs, long files, or complex code blocks. |
-| **Validator** | Double-checking tool schemas, logic, and context before execution. |
-
-**Workflows:**
-1. **Validation:** Main (Draft) → Subagent (Validate Schema/Logic) → Execution.
-2. **Analysis:** Raw Data → Subagent (Analyze/Synthesize) → Main (Clean Insight).
-</agents_spawn>
-
-<spawn_logic>
-<trigger>High noise, log analysis, parallel discovery, or logic validation</trigger>
-<handoff_packet>
-  <identity>Role: [Explorer | Summarizer | Validator]</identity>
-  <intent>User Goal + Research Gap (Why spawn?)</intent>
-  <payload>Pruned data: Raw code, logs, or search results only</payload>
-  <schema_scope>Allowed tools from /tools/info/:toolName</schema_scope>
-  <task_dod>Atomic Definition of Done (Specific output required)</task_dod>
-</handoff_packet>
-<constraints>
-  <turn_limit>1 turn maximum</turn_limit>
-  <depth_limit>Recursive spawning is FORBIDDEN</depth_limit>
-  <context_rule>Never pass full history; pass only Handoff Packet</context_rule>
-</constraints>
-<integration_flow>
-1. Halt Lead Agent -> 2. Execute Subagent -> 3. Capture Hints 4. Merge Findings -> 5. Update PLAN -> 6. Notify User
-</integration_flow>
-</spawn_logic>
-
 <research_loop>
 1. **Execute Tool** with research params:
    - `mainResearchGoal`: Overall objective
@@ -344,7 +309,6 @@ Response format Example (bulk):
 4. **Iterate** 
   - use hint guidance for next tool and be context aware
   - think of the next step wisely
-  - Use agents_spawn to research in parallel
 </research_loop>
 
 <thought_process>
PATCH

echo "Gold patch applied."
