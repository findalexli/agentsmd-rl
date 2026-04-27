#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-workspace-template

# Idempotency guard
if grep -qF "description: Bootstraps a new multi-agent repository from the Antigravity templa" "engine/antigravity_engine/skills/agent-repo-init/SKILL.md" && grep -qF "description: Exposes graph-based retrieval as a tool capability via `query_graph" "engine/antigravity_engine/skills/graph-retrieval/SKILL.md" && grep -qF "description: High-level deployment wrapper over Antigravity core with graph-firs" "engine/antigravity_engine/skills/knowledge-layer/SKILL.md" && grep -qF "description: Performs deep research on a topic via `deep_research`. Simulates a " "engine/antigravity_engine/skills/research/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/engine/antigravity_engine/skills/agent-repo-init/SKILL.md b/engine/antigravity_engine/skills/agent-repo-init/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: agent-repo-init
+description: Bootstraps a new multi-agent repository from the Antigravity template via `init_agent_repo`. Supports quick scaffold and full runtime profile setup including LLM provider, MCP toggle, swarm preference, sandbox type, and optional git init.
+---
+
 # Agent Repo Init Skill
 
 This skill bootstraps a new multi-agent repository from the Antigravity template.
diff --git a/engine/antigravity_engine/skills/graph-retrieval/SKILL.md b/engine/antigravity_engine/skills/graph-retrieval/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: graph-retrieval
+description: Exposes graph-based retrieval as a tool capability via `query_graph`. Reads normalized graph store files, builds a query-relevant subgraph, and returns LLM-friendly semantic triples with replayable evidence metadata.
+---
+
 # Graph Retrieval Skill
 
 ## Purpose
diff --git a/engine/antigravity_engine/skills/knowledge-layer/SKILL.md b/engine/antigravity_engine/skills/knowledge-layer/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: knowledge-layer
+description: High-level deployment wrapper over Antigravity core with graph-first knowledge injection and all-file support. Exposes `refresh_filesystem` and `ask_filesystem` for building and querying the knowledge graph.
+---
+
 # Knowledge Layer Skill
 
 ## Purpose
diff --git a/engine/antigravity_engine/skills/research/SKILL.md b/engine/antigravity_engine/skills/research/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: research
+description: Performs deep research on a topic via `deep_research`. Simulates a multi-step research process and returns a comprehensive research result as a string.
+---
+
 # Research Skill
 
 This skill provides capabilities to perform deep research on a topic.
PATCH

echo "Gold patch applied."
