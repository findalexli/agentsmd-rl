#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "**If you're on `main` or `master`, you MUST create a feature branch first** \u2014 un" "skills/commit/SKILL.md" && grep -qF "If on `main` or `master`, create a feature branch and move any uncommitted chang" "skills/pr-writer/SKILL.md" && grep -qF "Synthesize a new skill named `pi-agent-integration-eval` for working with `@mari" "skills/skill-writer/EVAL.md" && grep -qF "A skill's runtime behavior must not depend on another skill being present. Do no" "skills/skill-writer/references/design-principles.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/commit/SKILL.md b/skills/commit/SKILL.md
@@ -15,15 +15,7 @@ Before committing, always check the current branch:
 git branch --show-current
 ```
 
-**If you're on `main` or `master`, you MUST create a feature branch first** — unless the user explicitly asked to commit to main. Do not ask the user whether to create a branch; just proceed with branch creation. The `create-branch` skill should derive and create a suitable branch name automatically.
-
-Use the `create-branch` skill to create the branch. After `create-branch` completes, verify the current branch has changed before proceeding:
-
-```bash
-git branch --show-current
-```
-
-If still on `main` or `master`, stop — do not commit.
+**If you're on `main` or `master`, you MUST create a feature branch first** — unless the user explicitly asked to commit to main. Do not ask the user whether to create a branch; just proceed with branch creation, then re-check the current branch before committing. If still on `main` or `master`, stop — do not commit.
 
 ## Format
 
diff --git a/skills/pr-writer/SKILL.md b/skills/pr-writer/SKILL.md
@@ -11,14 +11,15 @@ Create pull requests following Sentry's engineering practices.
 
 ## Prerequisites
 
-Before creating a PR, ensure all changes are committed. If there are uncommitted changes, run the `sentry-skills:commit` skill first to commit them properly.
+Before creating a PR, ensure all changes are committed **to a feature branch**, not to the default branch.
 
 ```bash
-# Check for uncommitted changes
+# Check current branch and for uncommitted changes
+git branch --show-current
 git status --porcelain
 ```
 
-If the output shows any uncommitted changes (modified, added, or untracked files that should be included), invoke the `sentry-skills:commit` skill before proceeding.
+If on `main` or `master`, create a feature branch and move any uncommitted changes onto it before committing — a PR cannot be opened from the default branch against itself. If there are uncommitted changes, commit them on the feature branch before proceeding.
 
 ## Process
 
diff --git a/skills/skill-writer/EVAL.md b/skills/skill-writer/EVAL.md
@@ -6,7 +6,7 @@ These are optional guidance artifacts, not required outputs for every skill.
 ## Integration/Documentation Depth Eval
 
 ```text
-Use `sentry-skills:skill-writer` to synthesize a new skill named `pi-agent-integration-eval` for working with `@mariozechner/pi-agent-core` as a consumer in downstream libraries.
+Synthesize a new skill named `pi-agent-integration-eval` for working with `@mariozechner/pi-agent-core` as a consumer in downstream libraries.
 
 Primary objective: produce a non-surface-level integration skill that covers API surface, known issues/workarounds, and common real-world use cases.
 
diff --git a/skills/skill-writer/references/design-principles.md b/skills/skill-writer/references/design-principles.md
@@ -117,6 +117,20 @@ Pick one term for each concept and use it throughout the skill. Inconsistent ter
 | "field" everywhere | "field", "box", "element", "control" |
 | "extract" everywhere | "extract", "pull", "get", "retrieve" |
 
+## Independence
+
+A skill's runtime behavior must not depend on another skill being present. Do not instruct the agent to invoke another skill by name (`run the X skill`, `use \`sentry-skills:Y\``, `hand off to Z`), and do not treat another skill's files as runtime resources (`load skills/other-skill/references/foo.md`). Other skills may not be installed, may be renamed, or may be overridden by a user's own skill of the same name; any runtime dependency silently breaks in all three cases.
+
+State the intent directly and trust the agent's skill discovery to pick up whatever skill matches:
+
+| Do | Don't |
+|----|-------|
+| "If you're on `main`, create a feature branch first." | "Use the `create-branch` skill to create the branch." |
+| "If there are uncommitted changes, commit them first." | "Run the `sentry-skills:commit` skill before proceeding." |
+| "For deeper guidance on X, see `references/x.md`." | "See the `other-skill` skill for X." |
+
+Mentioning another skill's name in non-runtime content — provenance logs, audit allowlists, eval prompts meant to be copy-pasted by a human — is fine. The rule targets runtime behavior, not any mention of a skill's name.
+
 ## Avoid Duplication
 
 Information should live in either SKILL.md or reference files, not both. Prefer reference files for detailed content and SKILL.md for the core procedural workflow.
PATCH

echo "Gold patch applied."
