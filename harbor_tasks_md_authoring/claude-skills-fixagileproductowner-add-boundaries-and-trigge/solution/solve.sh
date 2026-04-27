#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-skills

# Idempotency guard
if grep -qF "not_for: Kanban-only workflows, waterfall project planning, general task managem" "product-team/agile-product-owner/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/product-team/agile-product-owner/SKILL.md b/product-team/agile-product-owner/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: "agile-product-owner"
 description: Agile product ownership for backlog management and sprint execution. Covers user story writing, acceptance criteria, sprint planning, and velocity tracking. Use for writing user stories, creating acceptance criteria, planning sprints, estimating story points, breaking down epics, or prioritizing backlog.
+not_for: Kanban-only workflows, waterfall project planning, general task management, non-Scrum agile frameworks (SAFe, LeSS) without adaptation
 triggers:
   - write user story
   - create acceptance criteria
@@ -9,6 +10,9 @@ triggers:
   - break down epic
   - prioritize backlog
   - sprint planning
+  - backlog grooming
+  - sprint retrospective
+  - definition of done
   - INVEST criteria
   - Given When Then
   - user story template
@@ -24,6 +28,7 @@ Backlog management and sprint execution toolkit for product owners, including us
 
 ## Table of Contents
 
+- [What Makes This Skill Different](#what-makes-this-skill-different)
 - [User Story Generation Workflow](#user-story-generation-workflow)
 - [Acceptance Criteria Patterns](#acceptance-criteria-patterns)
 - [Epic Breakdown Workflow](#epic-breakdown-workflow)
@@ -34,6 +39,14 @@ Backlog management and sprint execution toolkit for product owners, including us
 
 ---
 
+## What Makes This Skill Different
+
+- **Capacity math that aligns with reality:** sprint capacity is based on velocity × availability factor, not hope.
+- **Acceptance criteria scaled by story size:** minimum AC counts map to story points to avoid under-spec'ing large items.
+- **Weighted prioritization that stays consistent:** value 40%, impact 30%, risk 15%, effort 15% keeps tradeoffs explicit.
+- **Systematic epic splitting techniques:** five concrete split patterns prevent oversized stories.
+- **INVEST validation baked into workflows:** every story includes a validation step, not just guidance.
+
 ## User Story Generation Workflow
 
 Create INVEST-compliant user stories from requirements:
PATCH

echo "Gold patch applied."
