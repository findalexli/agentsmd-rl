#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "description: Project and feature planning with 4 phases - Specify, Design, Tasks" "packages/skills-catalog/skills/(development)/tlc-spec-driven/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/skills-catalog/skills/(development)/tlc-spec-driven/SKILL.md b/packages/skills-catalog/skills/(development)/tlc-spec-driven/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: tlc-spec-driven
-description: Project and feature planning with 4 phases - Specify, Design, Tasks, Implement+Validate. Creates atomic tasks with verification criteria and maintains persistent memory across sessions. Stack-agnostic. Use when: (1) Starting new projects (initialize vision, goals, roadmap), (2) Working with existing codebases (map stack, architecture, conventions), (3) Planning features (requirements, design, task breakdown), (4) Implementing with verification, (5) Tracking decisions/blockers across sessions, (6) Pausing/resuming work. Triggers on "initialize project", "map codebase", "specify feature", "design", "tasks", "implement", "pause work", "resume work".
+description: Project and feature planning with 4 phases - Specify, Design, Tasks, Implement+Validate. Creates atomic tasks with verification criteria and maintains persistent memory across sessions. Stack-agnostic. Use when (1) Starting new projects (initialize vision, goals, roadmap), (2) Working with existing codebases (map stack, architecture, conventions), (3) Planning features (requirements, design, task breakdown), (4) Implementing with verification, (5) Tracking decisions/blockers across sessions, (6) Pausing/resuming work. Triggers on "initialize project", "map codebase", "specify feature", "design", "tasks", "implement", "pause work", "resume work".
 metadata:
   author: github.com/felipfr
   version: "1.0.0"
PATCH

echo "Gold patch applied."
