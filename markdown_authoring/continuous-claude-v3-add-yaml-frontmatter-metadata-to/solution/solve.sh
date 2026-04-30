#!/usr/bin/env bash
set -euo pipefail

cd /workspace/continuous-claude-v3

# Idempotency guard
if grep -qF "name: commit" ".claude/skills/commit/SKILL.md" && grep -qF "name: continuity-ledger" ".claude/skills/continuity_ledger/SKILL.md" && grep -qF "name: create-handoff" ".claude/skills/create_handoff/SKILL.md" && grep -qF ".claude/skills/debug/SKILL.md" ".claude/skills/debug/SKILL.md" && grep -qF "name: describe-pr" ".claude/skills/describe_pr/SKILL.md" && grep -qF "name: discovery-interview" ".claude/skills/discovery-interview/SKILL.md" && grep -qF "description: Search Mathlib for lemmas by type signature pattern" ".claude/skills/loogle-search/SKILL.md" && grep -qF "name: planning-agent" ".claude/skills/plan-agent/SKILL.md" && grep -qF "description: Query the memory system for relevant learnings from past sessions" ".claude/skills/recall/SKILL.md" && grep -qF "description: Store a learning, pattern, or decision in the memory system for fut" ".claude/skills/remember/SKILL.md" && grep -qF "name: repo-research-analyst" ".claude/skills/repo-research-analyst/SKILL.md" && grep -qF "name: resume-handoff" ".claude/skills/resume_handoff/SKILL.md" && grep -qF "description: Show users how Continuous Claude works - the opinionated setup with" ".claude/skills/system_overview/SKILL.md" && grep -qF "description: Full 5-layer analysis of a specific function. Use when debugging or" ".claude/skills/tldr-deep/SKILL.md" && grep -qF "description: Get a token-efficient overview of any project using the TLDR stack" ".claude/skills/tldr-overview/SKILL.md" && grep -qF "description: Maps questions to the optimal tldr command. Use this to pick the ri" ".claude/skills/tldr-router/SKILL.md" && grep -qF "name: tldr-stats" ".claude/skills/tldr-stats/SKILL.md" && grep -qF "description: Friendly onboarding when users ask about capabilities" ".claude/skills/tour/SKILL.md" && grep -qF "name: validate-agent" ".claude/skills/validate-agent/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/commit/SKILL.md b/.claude/skills/commit/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: commit
 description: Create git commits with user approval and no Claude attribution
 ---
 
diff --git a/.claude/skills/continuity_ledger/SKILL.md b/.claude/skills/continuity_ledger/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: continuity-ledger
 description: Create or update continuity ledger for state preservation across clears
 ---
 
diff --git a/.claude/skills/create_handoff/SKILL.md b/.claude/skills/create_handoff/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: create-handoff
 description: Create handoff document for transferring work to another session
 ---
 
diff --git a/.claude/skills/debug/SKILL.md b/.claude/skills/debug/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: debug
 description: Debug issues by investigating logs, database state, and git history
 ---
 
diff --git a/.claude/skills/describe_pr/SKILL.md b/.claude/skills/describe_pr/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: describe-pr
 description: Generate comprehensive PR descriptions following repository templates
 ---
 
diff --git a/.claude/skills/discovery-interview/SKILL.md b/.claude/skills/discovery-interview/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: discovery-interview
 description: Deep interview process to transform vague ideas into detailed specs. Works for technical and non-technical users.
 user-invocable: true
 model: claude-opus-4-5-20251101
diff --git a/.claude/skills/loogle-search/SKILL.md b/.claude/skills/loogle-search/SKILL.md
@@ -1,3 +1,7 @@
+---
+name: loogle-search
+description: Search Mathlib for lemmas by type signature pattern
+---
 # Loogle Search - Mathlib Type Signature Search
 
 Search Mathlib for lemmas by type signature pattern.
diff --git a/.claude/skills/plan-agent/SKILL.md b/.claude/skills/plan-agent/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: planning-agent
 description: Planning agent that creates implementation plans and handoffs from conversation context
 ---
 
diff --git a/.claude/skills/recall/SKILL.md b/.claude/skills/recall/SKILL.md
@@ -1,3 +1,9 @@
+---
+name: recall
+description: Query the memory system for relevant learnings from past sessions
+user-invocable: false
+---
+
 # Recall - Semantic Memory Retrieval
 
 Query the memory system for relevant learnings from past sessions.
diff --git a/.claude/skills/remember/SKILL.md b/.claude/skills/remember/SKILL.md
@@ -1,3 +1,9 @@
+---
+name: remember
+description: Store a learning, pattern, or decision in the memory system for future recall
+user-invocable: false
+---
+
 # Remember - Store Learning in Memory
 
 Store a learning, pattern, or decision in the memory system for future recall.
diff --git a/.claude/skills/repo-research-analyst/SKILL.md b/.claude/skills/repo-research-analyst/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: repo-research-analyst
 description: Analyze repository structure, patterns, conventions, and documentation for understanding a new codebase
 ---
 
diff --git a/.claude/skills/resume_handoff/SKILL.md b/.claude/skills/resume_handoff/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: resume-handoff
 description: Resume work from handoff document with context analysis and validation
 ---
 
diff --git a/.claude/skills/system_overview/SKILL.md b/.claude/skills/system_overview/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: system-overview
+description: Show users how Continuous Claude works - the opinionated setup with hooks, memory, and coordination
+---
+
 # System Overview
 
 Show users how Continuous Claude works - the opinionated setup with hooks, memory, and coordination.
diff --git a/.claude/skills/tldr-deep/SKILL.md b/.claude/skills/tldr-deep/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: tldr-deep
+description: Full 5-layer analysis of a specific function. Use when debugging or deeply understanding code.
+---
+
 # TLDR Deep Analysis
 
 Full 5-layer analysis of a specific function. Use when debugging or deeply understanding code.
diff --git a/.claude/skills/tldr-overview/SKILL.md b/.claude/skills/tldr-overview/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: tldr-overview
+description: Get a token-efficient overview of any project using the TLDR stack
+---
+
 # TLDR Project Overview
 
 Get a token-efficient overview of any project using the TLDR stack.
diff --git a/.claude/skills/tldr-router/SKILL.md b/.claude/skills/tldr-router/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: tldr-router
+description: Maps questions to the optimal tldr command. Use this to pick the right layer
+---
+
 # TLDR Smart Router
 
 Maps questions to the optimal tldr command. Use this to pick the right layer.
diff --git a/.claude/skills/tldr-stats/SKILL.md b/.claude/skills/tldr-stats/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: tldr-stats
 description: Show full session token usage, costs, TLDR savings, and hook activity
 ---
 
diff --git a/.claude/skills/tour/SKILL.md b/.claude/skills/tour/SKILL.md
@@ -1,3 +1,8 @@
+---
+name: tour
+description: Friendly onboarding when users ask about capabilities
+---
+
 # Tour: What Can I Do?
 
 Friendly onboarding when users ask about capabilities.
diff --git a/.claude/skills/validate-agent/SKILL.md b/.claude/skills/validate-agent/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: validate-agent
 description: Validation agent that validates plan tech choices against current best practices
 ---
 
PATCH

echo "Gold patch applied."
