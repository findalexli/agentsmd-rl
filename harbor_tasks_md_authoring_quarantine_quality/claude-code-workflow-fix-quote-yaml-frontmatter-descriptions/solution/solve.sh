#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-workflow

# Idempotency guard
if grep -qF "description: \"Unified multi-dimensional code review with automated fix orchestra" ".claude/skills/review-cycle/SKILL.md" && grep -qF "description: \"Specification generator - 6 phase document chain producing product" ".claude/skills/spec-generator/SKILL.md" && grep -qF "description: \"Unified team skill for code review. 3-role pipeline: scanner, revi" ".claude/skills/team-review/SKILL.md" && grep -qF "description: \"Unified planning skill - 4-phase planning workflow, plan verificat" ".claude/skills/workflow-plan/SKILL.md" && grep -qF "description: \"Unified issue discovery and creation. Create issues from GitHub/te" ".codex/skills/issue-discover/SKILL.md" && grep -qF "description: \"Unified multi-dimensional code review with automated fix orchestra" ".codex/skills/review-cycle/SKILL.md" && grep -qF "description: \"Specification generator - 7 phase document chain producing product" ".codex/skills/spec-generator/SKILL.md" && grep -qF "description: \"End-to-end test-fix workflow generate test sessions with progressi" ".codex/skills/workflow-test-fix-cycle/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/review-cycle/SKILL.md b/.claude/skills/review-cycle/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: review-cycle
-description: Unified multi-dimensional code review with automated fix orchestration. Routes to session-based (git changes), module-based (path patterns), or fix mode. Triggers on "workflow:review-cycle", "workflow:review-session-cycle", "workflow:review-module-cycle", "workflow:review-cycle-fix".
+description: "Unified multi-dimensional code review with automated fix orchestration. Routes to session-based (git changes), module-based (path patterns), or fix mode. Triggers on \"workflow:review-cycle\", \"workflow:review-session-cycle\", \"workflow:review-module-cycle\", \"workflow:review-cycle-fix\"."
 allowed-tools: Agent, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, Read, Write, Edit, Bash, Glob, Grep, Skill
 ---
 
diff --git a/.claude/skills/spec-generator/SKILL.md b/.claude/skills/spec-generator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: spec-generator
-description: Specification generator - 6 phase document chain producing product brief, PRD, architecture, and epics. Triggers on "generate spec", "create specification", "spec generator", "workflow:spec".
+description: "Specification generator - 6 phase document chain producing product brief, PRD, architecture, and epics. Triggers on \"generate spec\", \"create specification\", \"spec generator\", \"workflow:spec\"."
 allowed-tools: Agent, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, Read, Write, Edit, Bash, Glob, Grep, Skill
 ---
 
diff --git a/.claude/skills/team-review/SKILL.md b/.claude/skills/team-review/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: team-review
-description: Unified team skill for code review. 3-role pipeline: scanner, reviewer, fixer. Triggers on "team-review".
+description: "Unified team skill for code review. 3-role pipeline: scanner, reviewer, fixer. Triggers on team-review."
 allowed-tools: TeamCreate(*), TeamDelete(*), SendMessage(*), TaskCreate(*), TaskUpdate(*), TaskList(*), TaskGet(*), Agent(*), AskUserQuestion(*), Read(*), Write(*), Edit(*), Bash(*), Glob(*), Grep(*), mcp__ace-tool__search_context(*)
 ---
 
diff --git a/.claude/skills/workflow-plan/SKILL.md b/.claude/skills/workflow-plan/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: workflow-plan
-description: Unified planning skill - 4-phase planning workflow, plan verification, and interactive replanning. Triggers on "workflow-plan", "workflow-plan-verify", "workflow:replan".
+description: "Unified planning skill - 4-phase planning workflow, plan verification, and interactive replanning. Triggers on \"workflow-plan\", \"workflow-plan-verify\", \"workflow:replan\"."
 allowed-tools: Skill, Agent, AskUserQuestion, TodoWrite, Read, Write, Edit, Bash, Glob, Grep
 ---
 
diff --git a/.codex/skills/issue-discover/SKILL.md b/.codex/skills/issue-discover/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: issue-discover
-description: Unified issue discovery and creation. Create issues from GitHub/text, discover issues via multi-perspective analysis, or prompt-driven iterative exploration. Triggers on "issue:new", "issue:discover", "issue:discover-by-prompt", "create issue", "discover issues", "find issues".
+description: "Unified issue discovery and creation. Create issues from GitHub/text, discover issues via multi-perspective analysis, or prompt-driven iterative exploration. Triggers on \"issue:new\", \"issue:discover\", \"issue:discover-by-prompt\", \"create issue\", \"discover issues\", \"find issues\"."
 allowed-tools: spawn_agent, wait, send_input, close_agent, request_user_input, Read, Write, Edit, Bash, Glob, Grep, mcp__ace-tool__search_context, mcp__exa__search
 ---
 
diff --git a/.codex/skills/review-cycle/SKILL.md b/.codex/skills/review-cycle/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: review-cycle
-description: Unified multi-dimensional code review with automated fix orchestration. Supports session-based (git changes) and module-based (path patterns) review modes with 7-dimension parallel analysis, iterative deep-dive, and automated fix pipeline. Triggers on "workflow:review-cycle", "workflow:review-session-cycle", "workflow:review-module-cycle", "workflow:review-cycle-fix".
+description: "Unified multi-dimensional code review with automated fix orchestration. Supports session-based (git changes) and module-based (path patterns) review modes with 7-dimension parallel analysis, iterative deep-dive, and automated fix pipeline. Triggers on \"workflow:review-cycle\", \"workflow:review-session-cycle\", \"workflow:review-module-cycle\", \"workflow:review-cycle-fix\"."
 ---
 
 # Review Cycle
diff --git a/.codex/skills/spec-generator/SKILL.md b/.codex/skills/spec-generator/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: spec-generator
-description: Specification generator - 7 phase document chain producing product brief, PRD, architecture, epics, and issues. Agent-delegated heavy phases (2-5, 6.5) with Codex review gates. Triggers on "generate spec", "create specification", "spec generator", "workflow:spec".
+description: "Specification generator - 7 phase document chain producing product brief, PRD, architecture, epics, and issues. Agent-delegated heavy phases (2-5, 6.5) with Codex review gates. Triggers on \"generate spec\", \"create specification\", \"spec generator\", \"workflow:spec\"."
 allowed-tools: Agent, request_user_input, TaskCreate, TaskUpdate, TaskList, Read, Write, Edit, Bash, Glob, Grep, Skill
 ---
 
diff --git a/.codex/skills/workflow-test-fix-cycle/SKILL.md b/.codex/skills/workflow-test-fix-cycle/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: workflow-test-fix-cycle
-description: End-to-end test-fix workflow generate test sessions with progressive layers (L0-L3), then execute iterative fix cycles until pass rate >= 95%. Combines test-fix-gen and test-cycle-execute into a unified pipeline. Triggers on "workflow:test-fix-cycle".
+description: "End-to-end test-fix workflow generate test sessions with progressive layers (L0-L3), then execute iterative fix cycles until pass rate >= 95%. Combines test-fix-gen and test-cycle-execute into a unified pipeline. Triggers on \"workflow:test-fix-cycle\"."
 allowed-tools: spawn_agent, wait, send_input, close_agent, request_user_input, Read, Write, Edit, Bash, Glob, Grep
 ---
 
PATCH

echo "Gold patch applied."
