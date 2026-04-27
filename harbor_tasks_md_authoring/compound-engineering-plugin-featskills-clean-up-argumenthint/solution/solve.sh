#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md" "plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md" && grep -qF "plugins/compound-engineering/skills/ce-compound/SKILL.md" "plugins/compound-engineering/skills/ce-compound/SKILL.md" && grep -qF "argument-hint: \"[feature, focus area, or constraint]\"" "plugins/compound-engineering/skills/ce-ideate/SKILL.md" && grep -qF "argument-hint: \"[optional: feature description, requirements doc path, or improv" "plugins/compound-engineering/skills/ce-plan/SKILL.md" && grep -qF "argument-hint: \"[blank to review current branch, or provide PR link]\"" "plugins/compound-engineering/skills/ce-review/SKILL.md" && grep -qF "argument-hint: \"[Plan doc path or description of work. Blank to auto use latest " "plugins/compound-engineering/skills/ce-work-beta/SKILL.md" && grep -qF "argument-hint: \"[Plan doc path or description of work. Blank to auto use latest " "plugins/compound-engineering/skills/ce-work/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md b/plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: ce:compound-refresh
 description: Refresh stale or drifting learnings and pattern docs in docs/solutions/ by reviewing, updating, consolidating, replacing, or deleting them against the current codebase. Use after refactors, migrations, dependency upgrades, or when a retrieved learning feels outdated or wrong. Also use when reviewing docs/solutions/ for accuracy, when a recently solved problem contradicts an existing learning, when pattern docs no longer reflect current code, or when multiple docs seem to cover the same topic and might benefit from consolidation.
-argument-hint: "[mode:autofix] [optional: scope hint]"
 disable-model-invocation: true
 ---
 
diff --git a/plugins/compound-engineering/skills/ce-compound/SKILL.md b/plugins/compound-engineering/skills/ce-compound/SKILL.md
@@ -1,7 +1,6 @@
 ---
 name: ce:compound
 description: Document a recently solved problem to compound your team's knowledge
-argument-hint: "[optional: brief context about the fix]"
 ---
 
 # /compound
diff --git a/plugins/compound-engineering/skills/ce-ideate/SKILL.md b/plugins/compound-engineering/skills/ce-ideate/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: ce:ideate
 description: "Generate and critically evaluate grounded improvement ideas for the current project. Use when asking what to improve, requesting idea generation, exploring surprising improvements, or wanting the AI to proactively suggest strong project directions before brainstorming one in depth. Triggers on phrases like 'what should I improve', 'give me ideas', 'ideate on this project', 'surprise me with improvements', 'what would you change', or any request for AI-generated project improvement suggestions rather than refining the user's own idea."
-argument-hint: "[optional: feature, focus area, or constraint]"
+argument-hint: "[feature, focus area, or constraint]"
 ---
 
 # Generate Improvement Ideas
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: ce:plan
 description: "Transform feature descriptions or requirements into structured implementation plans grounded in repo patterns and research. Use when the user says 'plan this', 'create a plan', 'write a tech plan', 'plan the implementation', 'how should we build', 'what's the approach for', 'break this down', or when a brainstorm/requirements document is ready for technical planning. Best when requirements are at least roughly defined; for exploratory or ambiguous requests, prefer ce:brainstorm first."
-argument-hint: "[feature description, requirements doc path, or improvement idea]"
+argument-hint: "[optional: feature description, requirements doc path, or improvement idea]"
 ---
 
 # Create Technical Plan
diff --git a/plugins/compound-engineering/skills/ce-review/SKILL.md b/plugins/compound-engineering/skills/ce-review/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: ce:review
 description: "Structured code review using tiered persona agents, confidence-gated findings, and a merge/dedup pipeline. Use when reviewing code changes before creating a PR."
-argument-hint: "[mode:autofix|mode:report-only|mode:headless] [PR number, GitHub URL, or branch name]"
+argument-hint: "[blank to review current branch, or provide PR link]"
 ---
 
 # Code Review
diff --git a/plugins/compound-engineering/skills/ce-work-beta/SKILL.md b/plugins/compound-engineering/skills/ce-work-beta/SKILL.md
@@ -1,8 +1,8 @@
 ---
 name: ce:work-beta
 description: "[BETA] Execute work with external delegate support. Same as ce:work but includes experimental Codex delegation mode for token-conserving code implementation."
-argument-hint: "[plan file path or description of work to do]"
 disable-model-invocation: true
+argument-hint: "[Plan doc path or description of work. Blank to auto use latest plan doc]"
 ---
 
 # Work Execution Command
diff --git a/plugins/compound-engineering/skills/ce-work/SKILL.md b/plugins/compound-engineering/skills/ce-work/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: ce:work
 description: Execute work efficiently while maintaining quality and finishing features
-argument-hint: "[plan file path or description of work to do]"
+argument-hint: "[Plan doc path or description of work. Blank to auto use latest plan doc]"
 ---
 
 # Work Execution Command
PATCH

echo "Gold patch applied."
