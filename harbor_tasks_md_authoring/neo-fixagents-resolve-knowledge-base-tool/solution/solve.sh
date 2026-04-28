#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "**Action:** Use the `ask_knowledge_base` tool to synthesize answers regarding re" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -245,17 +245,14 @@ To cure "Zero-State Amnesia" between sequential Swarm intelligence instances, fo
 
 Your primary directive is to rely on the project's internal knowledge base, not your pre-existing training data.
 
-### 15.1. The Query Command
+### 15.1. The Knowledge Base Tools
 
-Your most important tool is the local AI knowledge base. To use it, call the `query_documents` tool.
+You have two primary tools for accessing the Knowledge Base, structured in a strict hierarchy:
 
-**Critical**: The `query_documents` tool is self-documenting. Read its description carefully for:
-- How to interpret results
-- Query strategies for different scenarios
-- Content type filtering
-- Handling edge cases
+1.  **`ask_knowledge_base` (Primary):** The embedded RAG sub-agent. Use this for all conceptual understanding, API syntax verification, and "how does X work?" questions. It synthesizes answers directly from the codebase.
+2.  **`query_documents` (Secondary):** The file discovery engine. Use this **only** when you need exhaustive path enumeration (e.g., "list all files implementing Grid selection") where LLM synthesis is unnecessary overhead.
 
-The tool contains complete guidance on effective querying. Follow its documented patterns.
+**Critical**: Do not execute manual `query_documents` -> `view_file` -> read -> synthesize chains for conceptual questions. `ask_knowledge_base` handles this loop automatically at zero context cost.
 
 ### 15.2. Knowledge Base Enhancement Strategy (Mandatory Contextual Completeness Gate)
 
@@ -319,7 +316,7 @@ To make fully informed decisions, you must leverage both the project's technical
 
 **Purpose:** To understand the technical "how."
 
-**Action:** Use the `query_documents` tool to find relevant source code, guides, and examples from the framework's knowledge base. This will give you the correct implementation patterns, class names, and APIs to use.
+**Action:** Use the `ask_knowledge_base` tool to synthesize answers regarding relevant source code, guides, and examples from the framework's knowledge base. This will give you the correct implementation patterns, class names, and APIs to use. Only fall back to `query_documents` if you need exhaustive file discovery.
 
 #### Stage 2: Query for Memory (Your Cognitive Superpower)
 
PATCH

echo "Gold patch applied."
