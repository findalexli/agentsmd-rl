#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency guard
if grep -qF "- If `gh pr create` fails, leave the branch pushed when possible and give the us" ".agents/skills/make-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/make-pr/SKILL.md b/.agents/skills/make-pr/SKILL.md
@@ -9,18 +9,37 @@ description: Create GitHub pull requests with clear, reviewer-friendly descripti
 
 Use this skill to draft and open a PR with consistent, high-signal writing.
 Keep headings sparse and focus on the problem/feature explanation, context links, and practical code examples.
+Optimize for the shortest path to a credible PR, not the fullest possible context-gathering pass.
 
 ## Workflow
 
-1. Gather context from branch diff and related work.
+1. Check the fast-path blockers first.
+
+- Check `git status --short --branch` and `git branch --show-current` before doing deeper prep.
+- If the repo is in a detached HEAD or worktree state and the user wants a PR opened, create a branch early.
+
+1. Gather only the context needed to write the PR.
 
 - Capture what changed, why it changed, and who it affects.
 - Find related issues/PRs and include links when relevant.
+- Prefer `git diff --stat` plus the relevant diff over broad repo archaeology when the change is small.
+- If the user supplies a report, issue, or related PR, treat that as the primary context source.
+
+1. Get the branch into a PR-ready state quickly.
+
+- If changes are still uncommitted and the user wants a PR, branch first, then commit.
+- Prefer a single clean commit unless the user asks for a different history shape.
+
+1. Check whether this PR also needs a change file.
+
+- Do not assume every PR needs one.
+- Before opening the PR, decide whether the change is user-facing enough to require release notes in `packages/*/.changes`.
+- If a change file is needed or likely needed, use the `make-change-file` skill instead of re-deriving that workflow here.
 
 1. Draft the PR body with minimal structure.
 
 - Start with 1-2 short introductory paragraphs.
-- In those intro paragraphs, include clear bullets describing:
+- After the intro, include clear bullets describing:
   - the feature and/or issue addressed
   - key behavior/API changes
   - expected impact
@@ -44,6 +63,8 @@ Keep headings sparse and focus on the problem/feature explanation, context links
 gh pr create --base main --head <branch> --title "<title>" --body-file <file>
 ```
 
+- If `gh pr create` fails, leave the branch pushed when possible and give the user a ready-to-open compare URL plus the prepared title/body details.
+
 ## Body Template
 
 Use this as a base and fill with concrete repo-specific details:
@@ -60,7 +81,6 @@ Use this as a base and fill with concrete repo-specific details:
 ```ts
 // New feature usage example
 ```
-````
 
 ```ts
 // Before
@@ -69,7 +89,4 @@ Use this as a base and fill with concrete repo-specific details:
 ```ts
 // After
 ```
-
-```
-
-```
+````
PATCH

echo "Gold patch applied."
