#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents-at-scale-ark

# Idempotency guard
if grep -qF "3. **Research informs scope, not implementation.** Codebase research belongs in " ".claude/skills/issue-creation/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/issue-creation/SKILL.md b/.claude/skills/issue-creation/SKILL.md
@@ -36,7 +36,9 @@ Before writing anything, investigate the relevant code:
 - Identify the scope and blast radius of the problem
 - Note relevant file paths and code references
 
-Use Grep, Glob, Read, and the Explore agent as needed. Include key findings in the issue body so reviewers have context without re-doing the research.
+Use Grep, Glob, Read, and the Explore agent as needed. Include key findings in the issue's Context section so reviewers can orient themselves without re-doing the research.
+
+**Important:** The purpose of research is to understand the problem's scope and surface area — NOT to prescribe a solution. Do not let research findings leak into prescriptive implementation tasks. Knowing which files are involved helps the implementer orient; telling them what to change in those files anchors them on a path that may be wrong.
 
 ### Step 3: Check for duplicates and dependencies
 
@@ -84,8 +86,8 @@ Use this template:
 
 ## Task Breakdown
 
-- [ ] [Discrete, actionable task 1]
-- [ ] [Discrete, actionable task 2]
+- [ ] [Problem-level task describing WHAT needs to change, not HOW]
+- [ ] [Another problem-level task]
 - [ ] ...
 
 ## Testing Approach
@@ -123,10 +125,12 @@ Title must use conventional commit prefix: `feat:`, `fix:`, `docs:`, `chore:`, `
 ## Rules
 
 1. **Always ask clarifying questions first.** Never skip straight to research or drafting. Confirm understanding before proceeding.
-2. **Focus on the problem.** Never propose a design or solution unless the user explicitly asks for one.
-3. **Research first.** Every issue must include codebase research findings.
-4. **No duplicates.** Always check existing issues before creating.
-5. **Task breakdown required.** Break the work into discrete, actionable tasks.
-6. **Testing approach required.** Suggest how to verify the fix/feature.
-7. **Always add "needs grooming" label.** Every issue created by this skill gets this label.
-8. **Link dependencies.** Reference related issues when they exist.
+2. **Focus on the problem, not the solution.** The issue author's job is to be the expert on the problem. Never propose a design, implementation approach, or specific code changes unless the user explicitly asks for one.
+3. **Research informs scope, not implementation.** Codebase research belongs in the Context section to help the implementer orient. It must NOT leak into the Task Breakdown as prescriptive implementation steps. Knowing which files are involved is useful context; telling the implementer what to change in those files anchors them on a path that may be wrong.
+4. **Tasks describe WHAT, not HOW.** Each task should describe a problem to solve or a behavior to achieve. Bad: "Add sanitization in `services/ark-api/handlers/query.go`". Good: "Handle special characters in query input". The implementer — who will have deep context when they pick up the work — decides the how.
+5. **No uninformed specificity.** Implementation details written by someone without deep codebase knowledge create false confidence and anchoring bias. A vague-but-accurate issue is more useful than a specific-but-wrong one.
+6. **Research first.** Every issue must include codebase research findings.
+7. **No duplicates.** Always check existing issues before creating.
+8. **Testing approach required.** Suggest how to verify the fix/feature.
+9. **Always add "needs grooming" label.** Every issue created by this skill gets this label.
+10. **Link dependencies.** Reference related issues when they exist.
PATCH

echo "Gold patch applied."
